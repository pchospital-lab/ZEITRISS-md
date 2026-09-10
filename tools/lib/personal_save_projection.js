'use strict';

// Deterministischer CI-Helfer fuer den dokumentierten Exportvertrag. Dies ist
// weder Loader noch Spielengine: Er projiziert vorgegebene HQ-Abschlussdeltas.
const clone = (value) => JSON.parse(JSON.stringify(value));

function openSession(saves) {
  if (!Array.isArray(saves) || saves.length === 0) throw new Error('Mindestens ein Save erforderlich.');
  const byCharacter = new Map();
  const order = [];
  for (const source of saves) {
    for (const character of source.characters || []) {
      const previous = byCharacter.get(character.id);
      if (previous && previous.save.save_id !== source.save_id) {
        throw new Error(`Widerspruechlicher Stand fuer ${character.id}`);
      }
      if (!previous) order.push(character.id);
      byCharacter.set(character.id, { save: clone(source), character: clone(character) });
    }
  }
  return { anchorId: order[0], order, byCharacter, importedSaveIds: new Set(saves.map((s) => s.save_id)) };
}

function projectPersonalSaves(session, completion = {}) {
  if (completion.hq !== true) throw new Error('SaveGuard: Speichern nur im HQ');
  const uniqueItemOwners = new Map();
  return session.order.map((id) => {
    const origin = session.byCharacter.get(id);
    const out = clone(origin.save);
    const delta = completion.personal?.[id] || {};
    const character = clone(origin.character);
    character.xp = (character.xp || 0) + (delta.xp || 0);
    character.wallet = (character.wallet || 0) + (delta.cu || 0);
    character.carry = character.carry || [];
    for (const item of delta.items || []) {
      if (uniqueItemOwners.has(item.id)) throw new Error(`Einzigartige Beute doppelt: ${item.id}`);
      uniqueItemOwners.set(item.id, id);
      character.carry.push(clone(item));
    }
    character.history = character.history || { background: '', milestones: [] };
    character.history.milestones = character.history.milestones || [];
    if (completion.memory) character.history.milestones.push(completion.memory);
    out.characters = [character];
    // Jeder Export beginnt beim importierten persoenlichen Rootzustand. Nur die
    // Ankerkampagne erhaelt den definierten Kampagnenabschluss.
    if (id === session.anchorId && completion.anchorCampaign) out.campaign = clone(completion.anchorCampaign);
    out.economy.wallets = { [id]: { balance: character.wallet, name: character.name } };
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
