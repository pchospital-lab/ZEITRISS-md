'use strict';

// Deterministische CI-Pruefhilfe fuer den dokumentierten Exportvertrag. Sie
// simuliert keine Regeln, sondern uebernimmt ausschliesslich vorgegebene,
// bereits abgeschlossene HQ-Zustaende.
const clone = (value) => JSON.parse(JSON.stringify(value));
const canonical = (value) => {
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  if (value && typeof value === 'object') return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonical(value[key])}`).join(',')}}`;
  return JSON.stringify(value);
};

function openSession(saves) {
  if (!Array.isArray(saves) || saves.length === 0) throw new Error('Mindestens ein Save erforderlich.');
  const byCharacter = new Map();
  const bySaveId = new Map();
  const order = [];
  for (const source of saves) {
    const fingerprint = canonical(source);
    if (bySaveId.has(source.save_id)) {
      if (bySaveId.get(source.save_id) !== fingerprint) throw new Error(`Abweichender Inhalt fuer save_id ${source.save_id}`);
      continue;
    }
    bySaveId.set(source.save_id, fingerprint);
    for (const character of source.characters || []) {
      if (byCharacter.has(character.id)) throw new Error(`Widerspruechlicher Stand fuer ${character.id}`);
      order.push(character.id);
      byCharacter.set(character.id, { save: clone(source), character: clone(character) });
    }
  }
  const processedDebriefs = new Set();
  for (const { save } of byCharacter.values()) {
    for (const entry of save.logs?.trace || []) {
      if (entry?.event === 'rift_payoff' && typeof entry.debrief_id === 'string') {
        processedDebriefs.add(entry.debrief_id);
      }
    }
  }
  return { anchorId: order[0], order, byCharacter, importedSaveIds: new Set(bySaveId.keys()), processedDebriefs };
}

const openRifts = (save) => (save.campaign?.rift_seeds || []).filter((seed) => seed.status === 'open');

function leaderRiftBoard(session) {
  const leader = session.byCharacter.get(session.anchorId);
  const seeds = clone(openRifts(leader.save));
  const n = seeds.length;
  return { leader_id: session.anchorId, seeds, sg_bonus: Math.min(3, n), cu_multi: Math.min(1.6, 1 + 0.2 * n) };
}

function assignRiftPayoff(session, { debriefId, seeds, participants, random = Math.random }) {
  if (!debriefId) throw new Error('Stabile Debrief-ID erforderlich.');
  if (session.processedDebriefs.has(debriefId)) return { assigned: [], handedToIti: [], repeated: true };
  const leaderRecord = session.byCharacter.get(session.anchorId);
  if (!leaderRecord || leaderRecord.save.campaign?.px !== 5) throw new Error('Rift-Payoff erfordert Leader-Px 5.');
  if (!Array.isArray(seeds) || seeds.length < 1 || seeds.length > 2) throw new Error('Rift-Payoff erfordert ein oder zwei Instanzen.');
  const seedIds = seeds.map((entry) => entry?.id).filter((id) => typeof id === 'string' && id.trim());
  if (seedIds.length !== seeds.length || new Set(seedIds).size !== seedIds.length) throw new Error('Rift-Instanzen benötigen eindeutige IDs.');
  const knownIds = new Set([...session.byCharacter.values()].flatMap(({ save }) =>
    (save.campaign?.rift_seeds || []).map((entry) => entry?.id).filter(Boolean)));
  if (seedIds.some((id) => knownIds.has(id))) throw new Error('Bekannte Rift-Instanz darf nicht erneut vergeben werden.');
  const unique = [...new Set(participants || [])].filter((id) => session.byCharacter.has(id));
  if (!unique.length) throw new Error('Mindestens ein tatsächlicher Spieler-Teilnehmer erforderlich.');
  const assigned = [];
  const handedToIti = [];
  for (const source of seeds || []) {
    const eligible = unique.filter((id) => openRifts(session.byCharacter.get(id).save).length < 12);
    if (!eligible.length) { handedToIti.push(source.id); continue; }
    const ownerId = eligible[Math.min(eligible.length - 1, Math.floor(random() * eligible.length))];
    const origin = session.byCharacter.get(ownerId);
    origin.save.campaign.rift_seeds.push({ ...clone(source), status: 'open' });
    assigned.push({ seed_id: source.id, owner_id: ownerId });
  }
  const leader = session.byCharacter.get(session.anchorId).save.campaign;
  leader.px = 0;
  delete leader.paradoxon_index;
  leader.px_state = 'stable';
  for (const { save } of session.byCharacter.values()) {
    save.logs ||= {};
    save.logs.trace ||= [];
    save.logs.trace.push({ event: 'rift_payoff', debrief_id: debriefId,
      assigned: assigned.filter((entry) => entry.owner_id === save.characters?.[0]?.id).map((entry) => entry.seed_id),
      iti_handoff: handedToIti });
  }
  session.processedDebriefs.add(debriefId);
  return { assigned, handedToIti, repeated: false };
}

function projectPersonalSaves(session, completion = {}) {
  if (completion.hq !== true) throw new Error('SaveGuard: Speichern nur im HQ');
  return session.order.map((id) => {
    const origin = session.byCharacter.get(id);
    const out = clone(origin.save);
    const final = completion.personal?.[id];
    const completedCharacter = final?.character ? clone(final.character) : clone(origin.character);
    out.characters = [completedCharacter];
    // Nur der Anker bekommt explizit vorgegebene Kampagnen-Roots. Gast-Roots
    // stammen weiterhin vollstaendig aus ihrer persoenlichen Vorgaengerkette.
    if (id === session.anchorId) {
      for (const [root, value] of Object.entries(completion.anchorRoots || {})) {
        if (root !== 'campaign') out[root] = clone(value);
      }
      if (completion.anchorRoots?.campaign) {
        const projected = clone(completion.anchorRoots.campaign);
        projected.rift_seeds = clone(out.campaign.rift_seeds);
        if (session.processedDebriefs.size) {
          projected.px = out.campaign.px;
          projected.px_state = out.campaign.px_state;
        }
        out.campaign = projected;
      }
    }
    for (const [root, value] of Object.entries(final?.roots || {})) out[root] = clone(value);
    out.economy.wallets = { [id]: { balance: out.characters[0].wallet, name: out.characters[0].name } };
    // v7-Neuexporte haben genau eine Geldwahrheit: Character-Wallet plus
    // ownergebundener Wallet-Cache. `economy.cu` bleibt nur Legacy-Input.
    delete out.economy.cu;
    out.continuity.npc_roster = out.continuity.npc_roster.filter(
      (npc) => npc.scope !== 'personal' || npc.owner_id === id
    );
    out.continuity.active_npc_ids = out.continuity.active_npc_ids.filter((npcId) =>
      out.continuity.npc_roster.some((npc) => npc.id === npcId)
    );
    out.parent_save_id = origin.save.save_id;
    out.save_id = `${origin.save.save_id}-NEXT-${id}`;
    return out;
  });
}

module.exports = { openSession, projectPersonalSaves, leaderRiftBoard, assignRiftPayoff };
