// Research-Feld-Hygiene-Watchguard (Status-Enum + Dauer-Eindeutigkeit)
//
// Hintergrund A (Playtest 2026-06-16, eager-Solo-Lauf): Die SL schrieb
// research.projects[].status = "active" in einen echten Save. Gueltig sind laut
// v7-Export-Schema NUR ["in_progress","ready","collected"]. Ursache: "active"
// ist anderswo im Save-Schema gueltig (arena.queue_state, Rift-Seeds), und das
// Research-Pflichtgate nannte den START-Status eines neu angelegten Projekts
// nirgends -> die SL erfand das naheliegende "active".
//
// Hintergrund B (Review 2026-06-16): research trug frueher zusaetzlich ein
// `tier`-Feld als Dauer-Wunschwert. "tier" ist im Spiel aber dreifach belegt
// (Lizenz-Tier 0-V, Equipment-Tier, arena.tier) -> Verwechslungsgefahr fuer
// das Sprachmodell. `tier` wurde aus research ELIMINIERT: Dauer wird
// ausschliesslich in `missions_total` (Einsaetze) gemessen. "Tier" ist jetzt
// allein der Lizenz-/Ausruestungs-Begriff.
//
// Dieser Watchguard verankert beide Korrekturen dauerhaft:
//   1. Der Masterprompt nennt den Start-Status "in_progress" explizit.
//   2. Der Masterprompt verbietet "active" als research-status explizit.
//   3. Das Feld-SSOT (speicher-fortsetzung.md) traegt genau das kanonische
//      Enum in_progress|ready|collected.
//   4. Das v7-Export-Schema traegt genau dieses Enum (Validierungs-Autoritaet).
//   5. Das v7-Export-Schema fuehrt KEIN research-`tier`-Feld mehr (weder
//      required noch als property) -> Dauer-Eindeutigkeit ueber missions_total.
//   6. Der Masterprompt sagt explizit, dass research kein `tier` kennt.
// So kann keiner der beiden Fixes still wieder herausdriften.

const fs = require('fs');
const path = require('path');
const { createDocTextLoader } = require('./watchguard_doc_loader');

const root = path.resolve(__dirname, '..');
const { readText } = createDocTextLoader({
  root,
  scopeLabel: 'Research-Status-Enum-Watchguard',
});

function assert(condition, message) {
  if (!condition) {
    console.error(`research-status-enum-watchguard-fail: ${message}`);
    process.exit(1);
  }
}

// 1) + 2) Masterprompt: Start-Status + active-Verbot
const mp = readText('meta/masterprompt_v6.md');
assert(
  /status:\s*"in_progress"/.test(mp),
  'Masterprompt nennt den Research-Start-Status `in_progress` nicht mehr.',
);
assert(
  /in_progress`?\s*(?:→|->)\s*`?ready`?\s*(?:→|->)\s*`?collected/.test(mp),
  'Masterprompt nennt die kanonische Status-Reihenfolge in_progress -> ready -> collected nicht mehr.',
);
// Verbots-Klausel: an die AUSSAGE gekoppelt (active ist kein gueltiger research-Status),
// nicht an das exakte Schluesselwort "Niemals" -> robust gegen harmlose Umformulierung.
assert(
  /`active`[^\n]*(?:kein|nicht)[^\n]*research/i.test(mp)
    || /(?:nie|niemals|kein)[^\n]*`active`/i.test(mp),
  'Masterprompt verbietet `active` als research-status nicht mehr explizit.',
);

// 3) Feld-SSOT: kanonisches Enum unveraendert
const ssot = readText('systems/gameflow/speicher-fortsetzung.md');
assert(
  /status:\s*"in_progress"\|"ready"\|"collected"/.test(ssot),
  'Feld-SSOT (speicher-fortsetzung.md) traegt das Research-Status-Enum nicht mehr kanonisch.',
);

// 4) Validierungs-AUTORITAET: das v7-Export-Schema selbst traegt genau dieses Enum.
// Faengt Drift an der eigentlichen Schema-Quelle (nicht nur in der Prosa-SSOT).
const schemaRaw = fs.readFileSync(
  path.join(root, 'systems/gameflow/saveGame.v7.export.schema.json'),
  'utf8',
);
const schema = JSON.parse(schemaRaw);
let enumVals = null;
try {
  enumVals = schema.properties.research.properties.projects.items.properties.status.enum;
} catch (e) {
  assert(false, 'v7-Export-Schema: Pfad research.projects.items.status.enum nicht auffindbar.');
}
assert(
  Array.isArray(enumVals)
    && enumVals.length === 3
    && ['in_progress', 'ready', 'collected'].every((v, i) => enumVals[i] === v),
  `v7-Export-Schema research.status-Enum weicht ab: ${JSON.stringify(enumVals)} (erwartet ["in_progress","ready","collected"]).`,
);
assert(
  !enumVals.includes('active'),
  'v7-Export-Schema erlaubt "active" als research-status (darf es nicht).',
);

// 5) Dauer-Eindeutigkeit: research-Projekte fuehren KEIN `tier`-Feld mehr.
const projItem = schema.properties.research.properties.projects.items;
assert(
  Array.isArray(projItem.required) && !projItem.required.includes('tier'),
  'v7-Export-Schema: research.projects[] hat `tier` noch in required (muss raus -> Dauer = missions_total).',
);
assert(
  !(projItem.properties && Object.prototype.hasOwnProperty.call(projItem.properties, 'tier')),
  'v7-Export-Schema: research.projects[] definiert noch ein `tier`-property (muss raus -> Dauer = missions_total).',
);
assert(
  Array.isArray(projItem.required) && projItem.required.includes('missions_total'),
  'v7-Export-Schema: research.projects[] fuehrt `missions_total` nicht als required (= die Dauer-SSOT).',
);

// 6) Masterprompt sagt explizit, dass research kein `tier` kennt (Anti-Verwechslung).
assert(
  /research[^\n]*kein[^\n]*`tier`/i.test(mp) || /kein[^\n]*`tier`-Feld/i.test(mp),
  'Masterprompt stellt nicht mehr klar, dass research kein `tier`-Feld kennt.',
);

console.log('research-status-enum-watchguard-ok');
