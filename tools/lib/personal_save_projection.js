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
  return { anchorId: order[0], order, byCharacter, importedSaveIds: new Set(bySaveId.keys()) };
}

function projectPersonalSaves(session, completion = {}) {
  if (completion.hq !== true) throw new Error('SaveGuard: Speichern nur im HQ');
  return session.order.map((id) => {
    const origin = session.byCharacter.get(id);
    const out = clone(origin.save);
    const final = completion.personal?.[id];
    if (final?.character) origin.character = clone(final.character);
    out.characters = [clone(origin.character)];
    // Nur der Anker bekommt explizit vorgegebene Kampagnen-Roots. Gast-Roots
    // stammen weiterhin vollstaendig aus ihrer persoenlichen Vorgaengerkette.
    if (id === session.anchorId) {
      for (const [root, value] of Object.entries(completion.anchorRoots || {})) out[root] = clone(value);
    }
    for (const [root, value] of Object.entries(final?.roots || {})) out[root] = clone(value);
    out.economy.wallets = { [id]: { balance: out.characters[0].wallet, name: out.characters[0].name } };
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

module.exports = { openSession, projectPersonalSaves };
