// Gruppenkasse-Sigma-Anzeige-Watchguard
//
// Hintergrund (Playtest 2026-06-16, organischer 5er-Wallet-Lauf):
// Die SL listete Wallet-Staende konsequent EINZELN auf (z.B.
// "Astra 52.400 CU | Blitz 8.100 CU | ..."), zeigte aber NIE die berechnete
// Summenzeile "Gruppenkasse: <Σ> CU" -- weder nach CU-Uebergabe, noch im
// Debrief-Wallet-Split, noch als die Buchhalter-Persona aktiv nach dem
// Gesamtueberblick fragte.
//
// Ursache: Die Gruppenkasse-Anzeige war zwar im KB-Modul (cu-waehrungssystem.md)
// und in der sl-referenz.md beschrieben UND in runtime.js (group_treasury_view)
// implementiert -- aber der Masterprompt, der die SL am staerksten steuert, hatte
// KEINE durchsetzende Anzeige-Regel. Klassischer "runtime hat's, Prompt nicht"-Fall.
//
// Suffix-Nuance (Spec-Critic 2026-06-16): runtime.js emittiert das Suffix
// "(Σ Wallets)" NUR im Debrief-Wallet-Split (apply_wallet_split, ~Z5896/5928).
// Der !uebergabe-Pfad (~Z10330) gibt "Gruppenkasse: <n> CU." OHNE Suffix aus.
// Die MP-Regel muss diese Differenzierung treu abbilden, sonst erzeugt sie eine
// NEUE Prompt<->Runtime-Drift im Uebergabe-Fall.
//
// Dieser Watchguard verankert die Korrektur dauerhaft und prueft ALLE drei
// Drift-Achsen (Masterprompt, KB/SSOT-Doku, UND runtime.js):
//   1. Masterprompt: Summenzeile-Pflicht bei >1 Charakter.
//   2. Masterprompt: alle DREI Anlaesse genannt (Uebergabe, Debrief-Split, Anfrage).
//   3. Masterprompt: Gruppenkasse = berechneter View, kein Topf.
//   4. Masterprompt: Solo-Ausnahme.
//   5. KB-Modul cu-waehrungssystem.md: kanonische Beispielzeile.
//   6. sl-referenz.md: Gruppenkasse = Σ Wallets.
//   7. runtime.js: Debrief-Split emittiert "(Σ Wallets)"-Suffix (Output-SSOT,
//      die eigentliche Achse des Originalbugs -> False-Negative-Schutz).
//   8. runtime.js: Uebergabe-Pfad emittiert die Gruppenkasse-Zeile.
// So kann die Anzeige-Pflicht weder im Prompt noch in der Runtime still
// herausdriften.

const fs = require('fs');
const path = require('path');
const { createDocTextLoader } = require('./watchguard_doc_loader');

const root = path.resolve(__dirname, '..');
const { readText } = createDocTextLoader({
  root,
  scopeLabel: 'Gruppenkasse-Anzeige-Watchguard',
});

function assert(condition, message) {
  if (!condition) {
    console.error(`gruppenkasse-anzeige-watchguard-fail: ${message}`);
    process.exit(1);
  }
}

// ── Masterprompt ──────────────────────────────────────────────────────────
const mp = readText('meta/masterprompt_v6.md');

// 1) Kanonische Summenzeile vorhanden.
assert(
  /Gruppenkasse:\s*<?Σ?>?\s*CU/.test(mp),
  'Masterprompt traegt die kanonische Gruppenkasse-Summenzeile `Gruppenkasse: <Σ> CU` nicht (mehr).',
);
// 1b) Als Pflicht bei mehr als einem Charakter verankert.
assert(
  /Gruppenkasse-Anzeige/i.test(mp)
    && /(?:mehr als ein|>\s*1|≥\s*2|zwei oder mehr|mehrere|Gruppe|Koop)[^\n]*Charakter/i.test(mp),
  'Masterprompt verankert die Gruppenkasse-Anzeige nicht mehr als Pflicht bei mehr als einem Charakter.',
);

// 2) Alle DREI Anlaesse explizit genannt (Kernforderung des Befunds).
assert(/CU-Übergabe/i.test(mp) || /nach einer CU-Übergabe/i.test(mp),
  'Masterprompt nennt den Anlass "CU-Übergabe" nicht mehr.');
assert(/Debrief-Wallet-Split/i.test(mp),
  'Masterprompt nennt den Anlass "Debrief-Wallet-Split" nicht mehr.');
assert(/(?:Geldstand|Gesamtüberblick|nach dem.*fragt)/i.test(mp),
  'Masterprompt nennt den Anlass "Crew fragt nach dem Geldstand/Überblick" nicht mehr.');

// 3) Gruppenkasse = berechneter View, kein Topf.
assert(
  /Gruppenkasse[^\n]*berechnete[rn]? View/i.test(mp)
    || /berechnete[rn]? View[^\n]*Wallet/i.test(mp),
  'Masterprompt stellt nicht (mehr) klar, dass die Gruppenkasse ein berechneter View ist.',
);

// 4) Solo-Ausnahme.
assert(
  /Solo[^\n]*keine Gruppenkasse|keine Gruppenkasse-Zeile/i.test(mp),
  'Masterprompt fuehrt die Solo-Ausnahme (keine Gruppenkasse-Zeile bei 1 Charakter) nicht mehr.',
);

// ── KB-Modul ────────────────────────────────────────────────────────────────
const cu = readText('systems/currency/cu-waehrungssystem.md');
assert(
  /Gruppenkasse:\s*\d[\d.]*\s*CU/.test(cu),
  'cu-waehrungssystem.md traegt die kanonische Gruppenkasse-Beispielzeile nicht mehr.',
);

// ── sl-referenz.md ────────────────────────────────────────────────────────────
const slref = readText('core/sl-referenz.md');
assert(
  /Gruppenkasse[^\n]*(?:=\s*)?Σ?\s*Wallet/i.test(slref)
    || /Gruppenkasse[^\n]*Wallet-Summe/i.test(slref),
  'sl-referenz.md beschreibt die Gruppenkasse nicht mehr als Summe der Wallets.',
);

// ── runtime.js (Output-SSOT — die eigentliche Drift-Achse) ────────────────────
const runtimeRaw = fs.readFileSync(path.join(root, 'runtime.js'), 'utf8');
// 7) Debrief-Split emittiert das "(Σ Wallets)"-Suffix.
assert(
  /Gruppenkasse:\s*\$\{[^}]+\}\s*CU\s*\(Σ Wallets\)/.test(runtimeRaw),
  'runtime.js: Debrief-Wallet-Split emittiert die Gruppenkasse-Zeile mit Suffix "(Σ Wallets)" nicht mehr — '
    + 'MP-Regel und Runtime-Output wuerden auseinanderlaufen.',
);
// 8) Uebergabe-Pfad emittiert die Gruppenkasse-Zeile (ohne Suffix, Runtime-treu).
assert(
  /CU-Uebergabe verbucht[\s\S]{0,160}Gruppenkasse:\s*\$\{[^}]+\}\s*CU/.test(runtimeRaw),
  'runtime.js: !uebergabe-Pfad emittiert die Gruppenkasse-Zeile nicht mehr.',
);

console.log('gruppenkasse-anzeige-watchguard-ok');
