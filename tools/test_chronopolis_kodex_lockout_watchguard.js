const path = require('path');
const assert = require('assert');
const { createDocTextLoader } = require('./watchguard_doc_loader');

const root = path.resolve(__dirname, '..');
const { readMarkdown } = createDocTextLoader({
  root,
  scopeLabel: 'Chronopolis-Kodex-Lockout-Watchguard'
});

function mustIn(doc, regex, message) {
  assert.match(doc.text, regex, `${message} (${doc.file})`);
}

const hud = readMarkdown(
  'characters/hud-system.md',
  [/Chronopolis \(`CITY`\)/, /Kodex dunkel, HUD lebendig/],
  'Chronopolis-Kodex-Lockout-Watchguard HUD'
);

const spieler = readMarkdown(
  'core/spieler-handbuch.md',
  [/Chronopolis bewusst im Sperrmodus/, /kodex \[thema\]/],
  'Chronopolis-Kodex-Lockout-Watchguard Spieler-Handbuch'
);

const sl = readMarkdown(
  'core/sl-referenz.md',
  [/Chronopolis \(`CITY`\)[\s\S]{0,120}eigene Sperrmodus-Antwort/, /HQ\/ITI-Kern außerhalb `CITY` = Vollzugriff/],
  'Chronopolis-Kodex-Lockout-Watchguard SL-Referenz'
);

const masterprompt = readMarkdown(
  'meta/masterprompt_v6.md',
  [/Kodex-Sperrmodus in Chronopolis/, /Kodex dunkel, HUD lebendig/],
  'Chronopolis-Kodex-Lockout-Watchguard Masterprompt'
);

mustIn(
  hud,
  /Chronopolis \(`CITY`\):\*\*[\s\S]{0,40}\*\*Sperrmodus\*\*[\s\S]*Kodex dunkel, HUD lebendig/,
  'HUD-System muss den CITY-Sperrmodus als „Kodex dunkel, HUD lebendig“ führen.'
);
mustIn(
  hud,
  /Kodex-Zugriff:[^\n]*kodex \[thema\][^\n]*\(nicht in `?CITY`?\)/,
  'HUD-Menü muss `kodex [thema]` als in CITY nicht verfügbar markieren.'
);

mustIn(
  spieler,
  /Chronopolis bewusst im Sperrmodus\*\*:[\s\S]*Kodex dunkel, HUD lebendig/,
  'Spieler-Handbuch muss den Chronopolis-Sperrmodus explizit benennen.'
);
mustIn(
  spieler,
  /\| `kodex \[thema\]` \|[^\n]*\(in `CITY` gesperrt\)/,
  'Spieler-Handbuch-Befehlsliste muss `kodex [thema]` als in CITY gesperrt ausweisen.'
);

mustIn(
  sl,
  /Chronopolis \(`CITY`\)[\s\S]{0,120}eigene Sperrmodus-Antwort statt Re-Sync-Flow/,
  'SL-Referenz muss für `!offline` in CITY den Sperrmodus statt Re-Sync führen.'
);
mustIn(
  sl,
  /HQ\/ITI-Kern außerhalb `CITY` = Vollzugriff/,
  'SL-Referenz muss Vollzugriff auf außerhalb CITY begrenzen.'
);

mustIn(
  masterprompt,
  /Kodex-Sperrmodus in Chronopolis:[\s\S]*Kodex dunkel, HUD lebendig/,
  'Masterprompt muss den Chronopolis-Sperrmodus als SSOT-Anker enthalten.'
);

console.log('chronopolis-kodex-lockout-watchguard-ok');
