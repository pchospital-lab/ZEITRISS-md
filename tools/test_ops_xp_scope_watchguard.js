const path = require('path');
const assert = require('assert');
const { createDocTextLoader } = require('./watchguard_doc_loader');

const ROOT = path.join(__dirname, '..');
const { readMarkdown } = createDocTextLoader({
  root: ROOT,
  scopeLabel: 'Ops-XP-Scope-Watchguard'
});

function read(relPath, anchor) {
  return readMarkdown(relPath, [anchor], `Ops-XP-Scope (${relPath})`).text;
}

function section(text, start, end) {
  const from = text.search(start);
  assert.notStrictEqual(from, -1, `Abschnitt fehlt: ${start}`);
  const rest = text.slice(from);
  const to = end ? rest.slice(1).search(end) : -1;
  return to === -1 ? rest : rest.slice(0, to + 1);
}

const master = read('meta/masterprompt_v6.md', /XP-Geltung \(SSOT\)/);
assert.match(master, /XP-Geltung \(SSOT\)/);
assert.match(master, /Core-Ops und Rift-Ops/);
// PvP-BO3-Serie gibt XP wie eine Mission; Chronopolis bleibt XP-frei; kein pauschales Arena-/Training-Verbot mehr:
assert.match(master, /gewonnene PvP-Best-of-three-Serie/);
assert.match(master, /Chronopolis gibt kein XP/);
assert.doesNotMatch(master, /Chronopolis, Arena und Training geben keine XP/);
assert.doesNotMatch(master, /XP nur aus Core/);

const zeitrissCore = read('core/zeitriss-core.md', /Core-Ops- oder Rift-Ops-Mission/);
// Beide kanonischen Regelstellen pinnen (Phase-1-Bullet + XP-Kurve-Bullet):
assert.match(zeitrissCore, /Phase 1 \(Level 1-10\):[\s\S]{0,120}Core-Ops- oder Rift-Ops-Mission/);
assert.match(zeitrissCore, /XP-Kurve:[\s\S]{0,160}Core-Ops- oder Rift-Ops-Mission/);
assert.match(zeitrissCore, /PvP-BO3-Serie/);
assert.match(zeitrissCore, /Chronopolis gibt kein XP/);
assert.doesNotMatch(zeitrissCore, /Arena\/Training geben keine XP/);

const slReferenz = read('core/sl-referenz.md', /Core-\/Rift-Ops-Mission/);
assert.match(slReferenz, /Core-\/Rift-Ops-Mission/);
assert.match(slReferenz, /gewonnene PvP-BO3-Serie/);
assert.match(slReferenz, /Chronopolis: kein XP/);
assert.doesNotMatch(slReferenz, /Chronopolis\/Arena\/Training: keine XP/);

const spielerHandbuch = read('core/spieler-handbuch.md', /Core-\/Rift-Ops-Mission/);
assert.match(spielerHandbuch, /Core-\/Rift-Ops-Mission/);
assert.match(spielerHandbuch, /gewonnene PvP-BO3-Serien/);
assert.match(spielerHandbuch, /Chronopolis: kein XP/);
assert.doesNotMatch(spielerHandbuch, /Chronopolis\/Arena\/Training: keine XP/);

const campaign = read('gameplay/kampagnenstruktur.md', /Chronopolis vergibt keine XP/);
assert.match(campaign, /Chronopolis vergibt keine XP/);

// Die alten "PvP gibt kein XP / außerhalb der Kurve"-Verbote müssen durch den Cashout-Pfad ersetzt sein:
const slDebrief = read('core/sl-referenz.md', /Arena-\/PvP-Debrief/);
assert.doesNotMatch(slDebrief, /weil PvP außerhalb der Kampagnen-XP-Kurve läuft/);
assert.match(slDebrief, /PvP-only Progression/);

const speicherDebrief = read('systems/gameflow/speicher-fortsetzung.md', /Arena\/PvP-Debrief \(Match-Debrief\)/);
assert.doesNotMatch(speicherDebrief, /weil PvP nicht zur[\s\S]{0,12}Kampagnen-XP-Kurve beiträgt/);
assert.match(speicherDebrief, /Pending\/Cashout-Verbuchung/);

const pvpProg = section(
  read('gameplay/kampagnenstruktur.md', /PvP-only Progression/),
  /^#### PvP-only Progression/m,
  /^#### Diminishing Returns/m
);
assert.match(pvpProg, /Missionsäquivalent/);

console.log('ops-xp-scope-watchguard-ok');
