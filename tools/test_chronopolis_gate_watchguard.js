const fs = require('fs');
const path = require('path');
const assert = require('assert');

const root = path.resolve(__dirname, '..');

function walk(dir) {
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name.startsWith('.git')) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walk(full));
    else out.push(full);
  }
  return out;
}

function findRuntimeMacroFile() {
  const preferred = path.join(root, 'internal', 'runtime', 'toolkit-runtime-makros.md');
  if (fs.existsSync(preferred)) {
    const txt = fs.readFileSync(preferred, 'utf8');
    if (/macro\s+chrono_grant_key_if_lvl10\(\)/.test(txt) && /macro\s+chrono_launch_rift\(seed_id\)/.test(txt)) {
      return { file: preferred, text: txt };
    }
  }

  const candidates = walk(root)
    .filter((p) => p.endsWith('.md'))
    .filter((p) => /runtime|toolkit|makro|macro/i.test(p));

  const hits = candidates
    .map((file) => ({ file, text: fs.readFileSync(file, 'utf8') }))
    .filter(({ text }) => /macro\s+chrono_grant_key_if_lvl10\(\)/.test(text) && /macro\s+chrono_launch_rift\(seed_id\)/.test(text));

  assert.ok(hits.length > 0, 'Chronopolis-Watchguard: Kein Runtime-Makrofile mit chrono_* Makros gefunden.');
  assert.ok(hits.length === 1, `Chronopolis-Watchguard: Mehrdeutige Zielpfade gefunden (${hits.map((h) => path.relative(root, h.file)).join(', ')}).`);

  return hits[0];
}

const { file: macroFile, text } = findRuntimeMacroFile();

function must(regex, message) {
  assert.match(text, regex, message);
}

// 1) Lvl10 ohne Key -> HQ-Entry vergibt Schlüssel + HUD-Hinweis
must(/macro\s+chrono_grant_key_if_lvl10\(\)[\s\S]*\(char\.lvl\s*or\s*1\)\s*>=\s*10[\s\S]*char\.flags\.chronokey\s*=\s*true[\s\S]*Schlüssel erteilt/, 'Chronopolis-Key-Grant (Lvl10/HQ) fehlt oder driftet.');
must(/macro\s+hq_entry_hook\(\)[\s\S]*chrono_grant_key_if_lvl10\(\)/, 'HQ-Entry-Hook ruft chrono_grant_key_if_lvl10() nicht auf.');

// 2) fr_contact: CITY blockiert, HQ erlaubt
must(/macro\s+fr_contact\(channel,\s*subject\)[\s\S]*campaign\.loc\s*!=\s*'HQ'[\s\S]*FR-Kontakt nur im ITI-HQ erlaubt/, 'FR-Kontakt-HQ-Block fehlt.');
must(/macro\s+fr_contact\(channel,\s*subject\)[\s\S]*FR-Kanal\s*'\s*~\s*channel\s*~\s*'\s*·\s*Thema:\s*'\s*~\s*subject/, 'FR-Kontakt-Erfolgszweig (HQ) fehlt.');

// 3) chrono_launch_rift: nur HQ + episode_completed
must(/macro\s+chrono_can_launch_rift\(\)[\s\S]*campaign\.loc\s*==\s*'HQ'[\s\S]*campaign\.episode_completed/, 'chrono_can_launch_rift()-Gate für HQ/Episodenende fehlt.');
must(/macro\s+chrono_launch_rift\(seed_id\)[\s\S]*chrono_can_launch_rift\(\)\s*!=\s*'true'[\s\S]*Rift-Start blockiert\s*-\s*erst im HQ nach Episodenende/, 'chrono_launch_rift()-Blockzweig fehlt oder driftet.');

// 4) chrono_launch_rift ohne chrono.epoch nutzt campaign.epoch
must(/macro\s+chrono_launch_rift\(seed_id\)[\s\S]*set\s+ep_use\s*=\s*\(chrono\s+and\s+chrono\.epoch\)\s+or\s+campaign\.epoch/, 'Epoch-Fallback (chrono.epoch -> campaign.epoch) fehlt.');

// 5) Chronopolis bleibt CITY (kein HQ-Savepunkt)
must(/Chronopolis\s+selbst\s+ist\s+`CITY`\s+und\s+zählt\s+\*\*nicht\*\*\s+als\s+HQ/, 'CITY-vs-HQ-Anker für Chronopolis fehlt.');

console.log(`Chronopolis-Watchguard Zielpfad: ${path.relative(root, macroFile)}`);
console.log('chronopolis-gate-watchguard-ok');
