const path = require('path');
const { createDocTextLoader } = require('./watchguard_doc_loader');

const root = path.resolve(__dirname, '..');
const { readMarkdown } = createDocTextLoader({
  root,
  scopeLabel: 'V7-Export-Fieldlist-Watchguard',
});

function assert(condition, message) {
  if (!condition) {
    console.error(message);
    process.exit(1);
  }
}

const doc = readMarkdown(
  'systems/gameflow/speicher-fortsetzung.md',
  [/\*\*v7-Export-Pflichtfelder \(kanonisch, nicht Runtime-Bridge\):\*\*/i, /### Kompakt-Profil \(Save v7\)/i],
  'v7-Export-Pflichtfelder',
);

const masterprompt = readMarkdown(
  'meta/masterprompt_v6.md',
  [/Bei `!save` oder `speichern` IMMER folgenden JSON-Block/i, /\*\*Visual-Split\/Merge:\*\*/i],
  'Masterprompt-v7-Visual-Identity-Vertrag',
);

const requiredSnippets = [
  'campaign { episode, mission, px, px_state, mode, rift_seeds[], entry_choice_skipped, episode_start, episode_end }',
  'entry_choice_skipped', 'episode_start', 'episode_end',
  'logs.hud', 'logs.psi', 'logs.arena_psi',
  'research { projects[]',
  'kind, scope, missions_total, missions_done, status',
  'ui.intro_seen', 'ui.dice.debug_rolls',
  'has_psi', 'psi_heat', 'pp', 'psi_abilities', 'artifact?', 'visual_identity?',
  'draft|locked', 'revision', 'appearance', 'performance', 'locks', 'avoid', 'reference',
  'arena.active', 'arena.phase', 'arena.queue_state',
  'arena.contract_id', 'arena.streak',
  'arena.pending_rewards', 'arena.banked_rewards',
  'arena.first_wins', 'arena.match_policy'
];

for (const snippet of requiredSnippets) {
  assert(doc.text.includes(snippet), `v7-watchguard: Pflichtfeld fehlt: ${snippet}`);
}

assert(doc.text.includes('höhere Visual-Revision'), 'v7-watchguard: Mergeanker höhere Visual-Revision fehlt.');
assert(doc.text.includes('Gleiche Revision') && doc.text.includes('Kontinuitätskonflikt'), 'v7-watchguard: Konfliktanker bei gleicher Revision fehlt.');

assert(!doc.text.includes('`arena?`'), 'v7-watchguard: Verbotenes optionales arena?-Feld gefunden.');
assert(!/Arena nur wenn genutzt/.test(doc.text), 'v7-watchguard: Restdrift "Arena nur wenn genutzt" gefunden.');

const masterpromptSnippets = [
  '`visual_identity?` (optional, mechanikfrei)',
  '{v:1, status:draft|locked, revision>=1, appearance:',
  'performance:{voice,movement}, locks[], avoid[], reference?}',
  'ausschließlich Sidecar-Metadaten',
  'niemals Base64 oder Binärdaten',
  'Plattform-/Providerparameter wie Modellname',
  'Equipment und epochenabhängige Kleidung',
  'niemals Boni, Mali, Werte',
  'Talente oder andere Mechanik',
  'Ein `locked`-Block bleibt im normalen Spielbetrieb wortgetreu',
  '`visual_identity?` reist mit `characters[].id`',
  'Fehlt der Block in einem Zweig, gewinnt',
  'der vorhandene',
  'höhere Visual-Revision',
  'unabhängig',
  'Gleiche Revision plus verschiedener Inhalt erzeugt einen strukturierten Kontinuitätskonflikt und eine Spielerentscheidung',
  'vollständigem, gültigem v7-HQ-Save als Quelle und aktivem',
  'Creator-Bootstrap',
  '`parent_save_id` erhält die bisherige `save_id`',
  '`-VIS-R<revision>`',
  '`branch_id` und `merge_id` bleiben unverändert',
  'Gameplay-Felder bleiben semantisch wertgleich',
  'ausschließlich ein nicht ladbarer `CREATOR_PATCH`',
];

const normalizedMasterprompt = masterprompt.text.replace(/\s+/g, ' ').toLowerCase();
for (const snippet of masterpromptSnippets) {
  assert(normalizedMasterprompt.includes(snippet.replace(/\s+/g, ' ').toLowerCase()), `v7-watchguard: Masterprompt-Vertrag fehlt: ${snippet}`);
}

const defaultTemplateMatch = masterprompt.text.match(
  /Bei `!save` oder `speichern` IMMER folgenden JSON-Block[\s\S]*?```json\s*\n([\s\S]*?)\n```/i,
);
assert(defaultTemplateMatch, 'v7-watchguard: Kanonischer JSON-Default-Templateblock nicht gefunden.');
assert(!/"visual_identity"\s*:/.test(defaultTemplateMatch[1]), 'v7-watchguard: Default-Template darf visual_identity nicht aufblasen.');

console.log('v7-export-fieldlist-watchguard-ok');
