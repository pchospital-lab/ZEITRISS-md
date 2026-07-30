const path = require('path');
const assert = require('assert');
const { createDocTextLoader } = require('./watchguard_doc_loader');

const ROOT = path.join(__dirname, '..');
const { readMarkdown } = createDocTextLoader({
  root: ROOT,
  scopeLabel: 'Physicality-Watchguard'
});

function readText(relPath, anchorRegex) {
  const { file, text } = readMarkdown(
    relPath,
    anchorRegex ? [anchorRegex] : [/./s],
    `Physicality-Watchguard (${relPath})`
  );
  return { relPath: path.relative(ROOT, file), text };
}

const checks = [
  {
    relPath: 'systems/toolkit-gpt-spielleiter.md',
    mustHave: [
      /Retina-HUD/i,
      /Handgelenk-Projektor/i,
      /Inworld-/i,
      /Kozyrev-Transfer-Beat/i,
      /legendary_temporal_ship[\s\S]{0,180}Hangar-Axis[\s\S]{0,180}ohne Personal-Spiegelkreis/i
    ],
    mustNotHave: [
      /schwebende\s+holografische\s+Displays/i,
      /Hologramm-Begleiter/i,
      /nur\s+f[üu]r\s+diese\s+Mission/i
    ]
  },
  {
    relPath: 'meta/masterprompt_v6.md',
    mustHave: [
      /Kontrollierter Nullzeit-Sprung \(Pflichtbeat, regulärer Personaltransfer\)/i,
      /Kozyrev-Spiegel[\s\S]{0,420}allzeitliche Unendlichkeit/i,
      /Ziel-Lock\/Auswurf[\s\S]{0,260}räumlichen Zielkorridor[\s\S]{0,180}Austrittsfläche und -winkel/i,
      /Schiffs-Ausnahme[\s\S]{0,220}legendary_temporal_ship[\s\S]{0,220}Hangar-Axis/i,
      /kein Personal-Spiegelkreis/i,
      /Kreis → Spiegel-Unendlichkeit → Ruck → Schnitt/i,
      /Spiegelung ist reine Kalibrierungsoptik/i,
      /Spiegel bleiben ITI-Hardware in der Nullzeit[\s\S]{0,180}Exfil\/Rückholung[\s\S]{0,100}nur der schmale Riss/i
    ],
    mustNotHave: [
      /Kontrollierter Nullzeit-Sprung \(Pflichtbeat\):/i,
      /Kozyrev-Spiegel[\s\S]{0,180}alternative Ichs (?:zeigen|offenbaren)/i
    ]
  },
  {
    relPath: 'core/sl-referenz.md',
    mustHave: [
      /Transfer-Beat \(SSOT, ohne Zusatzregeln\)/i,
      /Regulärer Transfer-Out aus der Nullzeit/i,
      /Ziel-Lock → Kozyrev-Kreis → Spiegel-Unendlichkeit → Ruck → Schnitt/i,
      /Zielkorridor[\s\S]{0,220}Austrittsfläche und -winkel/i,
      /Legendäres Zeitschiff[\s\S]{0,220}legendary_temporal_ship[\s\S]{0,220}Hangar-Axis/i,
      /keine alternativen Ichs, kein Multiversum, keine Prophezeiung/i,
      /Kozyrev-Spiegel bleiben ITI-Hardware in der Nullzeit/i,
      /Exfil\/Transfer-Back[\s\S]{0,120}nur der schmale Riss/i
    ],
    mustNotHave: [
      /Exfil\/Transfer-Back[\s\S]{0,120}Kozyrev-Kreis/i
    ]
  },
  {
    relPath: 'systems/gameflow/cinematic-start.md',
    mustHave: [
      /linsengebundene\s+HUD-Lichtbilder/i,
      /Briefingfl[äa]chen/i,
      /Kozyrev-Spiegel[\s\S]{0,320}allzeitliche Unendlichkeit/i,
      /letzten Countdown-Takt[\s\S]{0,200}metallischen Ruck/i,
      /Spiegel bleiben im Quarzatrium[\s\S]{0,160}Rückholung im Feld[\s\S]{0,80}allein der schmale Riss/i
    ],
    mustNotHave: [
      /Hologramm-Begleiter/i,
      /schwebende\s+holografische\s+Displays/i,
      /holografische\s+Anzeigen\s+erscheinen\s+in\s+deinem\s+Sichtfeld/i
    ]
  },
  {
    relPath: 'core/zeitriss-core.md',
    mustHave: [
      /Holosuite/i,
      /Retina-HUD/i,
      /Handgelenk-HUDs/i,
      /Reguläre ITI-Personaltransfers beginnen in der \*\*Sprungkammer des Quarzatriums\*\*/i,
      /Kozyrev-Spiegelsegmente[\s\S]{0,420}allzeitliche Unendlichkeit/i,
      /Ziel-Lock fixiert Zielzeit und einen räumlichen Zielkorridor/i,
      /verfügbare Fläche[\s\S]{0,220}Winkel[\s\S]{0,120}unberechenbar/i,
      /legendary_temporal_ship[\s\S]{0,180}Hangar-Axis[\s\S]{0,180}kein Personal-Spiegelkreis/i,
      /Ziel-Lock → Kozyrev-Kreis → Spiegel-Unendlichkeit → Ruck → Schnitt/i,
      /Exfil\/Rückholung zeigt im Feld nur den Riss/i,
      /Rückholungen werden vom selben Kozyrev-Array in der Nullzeit adressiert[\s\S]{0,100}am Einsatzort öffnet sich nur der Riss/i
    ],
    mustNotHave: [
      /Kontrollierte ITI-Sprünge beginnen in der \*\*Sprungkammer des Quarzatriums\*\*/i,
      /freischwebende\s+Hologramm-UI/i,
      /Handgelenk-Projektor-UI\s+als\s+Default/i
    ]
  },
  {
    relPath: 'gameplay/fahrzeuge-konflikte.md',
    mustHave: [
      /Transferort-SSOT/i,
      /Reguläre Personaltransfers[\s\S]{0,180}Kozyrev-Sprungkammer im Quarzatrium/i,
      /Standardfahrzeuge bleiben[\s\S]{0,120}zurück/i,
      /legendary_temporal_ship[\s\S]{0,180}Hangar-Axis[\s\S]{0,180}eigenen Chrono-Antrieb/i,
      /kein Personal-Spiegelkreis/i,
      /Schiffs-Riss bleibt ein Schnitt statt eines Portals/i
    ],
    mustNotHave: []
  },
  {
    relPath: 'core/spieler-handbuch.md',
    mustHave: [
      /Kozyrev-Spiegelsegmente[\s\S]{0,420}allzeitliche Unendlichkeit/i,
      /metallischen Ruck aus der Symmetrie/i,
      /Spiegel bleiben als ITI-Hardware in der Nullzeit/i,
      /Rücksprung im Feld[\s\S]{0,100}kein Ring[\s\S]{0,100}nur der schmale Schnitt/i
    ],
    mustNotHave: [
      /Sprungkreise\s+in\s+perfekter\s+Ruhe/i
    ]
  }
];

for (const check of checks) {
  const { relPath, text } = readText(check.relPath, check.mustHave[0]);
  for (const rx of check.mustHave) {
    assert.ok(rx.test(text), `${relPath}: Pflichtanker fehlt (${rx}).`);
  }
  for (const rx of check.mustNotHave) {
    assert.ok(!rx.test(text), `${relPath}: Verbotenes Driftmuster gefunden (${rx}).`);
  }
}

console.log('physicality-watchguard-ok');
