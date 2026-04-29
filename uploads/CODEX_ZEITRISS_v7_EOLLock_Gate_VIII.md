# Codex-Briefing — ZEITRISS v7 EOL-Lock Gate VIII

## Ziel

Der Spielvertrag ist jetzt weitgehend sauber. Nicht redesignen. Dieser Pass ist ein **technischer EOL-/Smoke-Lock** plus zwei kleine Restdrifts.

Aktueller Review-Befund:

- Masterprompt-v7, Schema, Arena-Checkpoint, Psi-/Artefaktfelder und aktive v7-Pflichtfeldliste sind deutlich nachgezogen.
- `speicher-fortsetzung.md` enthält jetzt den richtigen Arena-Sentinel-Vertrag.
- Masterprompt-Load ist HQ-only-kompatibel.
- Blocker bleibt: Raw-Download zeigt `scripts/smoke.sh` weiterhin als faktisch 2 LF-Zeilen und `.gitattributes` als 1 LF-Zeile. GitHub UI rendert zwar viele Zeilen, aber das ist typisch für CR-only oder gemischte EOL-Probleme. Für `bash scripts/smoke.sh` ist das ein echter Gate-Blocker.
- Kleinere Restdrifts: ein alter Satz sagt noch `optional arena`; ein großer Legacy-JSON-Block ist trotz Warnhinweisen weiterhin sehr kopierfähig und enthält `v: 7` mit Legacy-Rootfeldern.

Wenn dieser Pass erledigt ist und `bash scripts/smoke.sh` wirklich lokal grün läuft, ist der nächste Review ein ernsthafter Jubeltest-Kandidat.

---

## 0. Branch

```bash
git checkout -b codex/eol-lock-gate-viii
```

---

## 1. EOL hart normalisieren

### Befund

Raw-Download:

- `scripts/smoke.sh`: 2 physische LF-Zeilen, erste Zeile enthält Shebang plus fast alle Befehle; zweite beginnt mitten in `verankerte HQ-Projektion)`.
- `.gitattributes`: 1 physische LF-Zeile mit allen Patterns hintereinander.

GitHub UI zeigt zwar viele Zeilen, aber Raw/Parser sprechen für CR-only oder gemischte Zeilenenden. Das ist ein Gate-Blocker.

### Patch

Führe im Repo aus:

```bash
python3 - <<'PY'
from pathlib import Path

def normalize_lf(path: str) -> None:
    p = Path(path)
    data = p.read_bytes()
    text = data.decode("utf-8")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    p.write_text(text, encoding="utf-8", newline="\n")

normalize_lf("scripts/smoke.sh")
PY
```

Danach `.gitattributes` **explizit neu schreiben**, nicht nur normalisieren:

```bash
cat > .gitattributes <<'EOF'
*.md text eol=lf
*.json text eol=lf
*.js text eol=lf
*.py text eol=lf
*.sh text eol=lf
scripts/*.sh text eol=lf
EOF
```

Dann:

```bash
chmod +x scripts/smoke.sh
git add --renormalize scripts/smoke.sh .gitattributes
```

Falls `git add --renormalize .` nötig ist, nur verwenden, wenn der Diff kontrollierbar bleibt.

---

## 2. Externen EOL-Watchguard ergänzen

### Problem

`tools/test_smoke_script_sanity.js` ist gut, aber wenn `smoke.sh` selbst kollabiert, wird dieser Test im Smoke möglicherweise nie erreicht. Trotzdem soll er zusätzlich im Smoke bleiben.

### Patch

Ergänze optional, aber empfohlen, einen separaten Guard:

`tools/test_eol_lf_watchguard.js`

Minimalinhalt:

```js
const fs = require('fs');
const path = require('path');

function assert(condition, message) {
  if (!condition) {
    console.error(message);
    process.exit(1);
  }
}

const ROOT = path.resolve(__dirname, '..');

const checks = [
  { rel: 'scripts/smoke.sh', minLf: 80 },
  { rel: '.gitattributes', minLf: 5 },
];

for (const { rel, minLf } of checks) {
  const p = path.join(ROOT, rel);
  const data = fs.readFileSync(p);
  const lf = [...data].filter((b) => b === 0x0a).length;
  const cr = [...data].filter((b) => b === 0x0d).length;
  assert(cr === 0, `${rel}: enthält CR-Zeichen (${cr}). Bitte LF-only normalisieren.`);
  assert(lf >= minLf, `${rel}: zu wenige LF-Zeilen (${lf}); Datei wirkt kollabiert.`);
}

console.log('eol-lf-watchguard-ok');
```

Diesen Test im Smoke sehr früh verankern, direkt nach `mkdir -p out` oder unmittelbar nach `export PYTHONPATH`, aber erst nachdem `smoke.sh` syntaktisch sauber ist:

```bash
node tools/test_eol_lf_watchguard.js > out/eol_lf_watchguard.log
grep "eol-lf-watchguard-ok" out/eol_lf_watchguard.log
```

---

## 3. `scripts/smoke.sh` lokal prüfen

Nach EOL-Fix lokal ausführen:

```bash
python3 - <<'PY'
from pathlib import Path

for rel, min_lf in [("scripts/smoke.sh", 80), (".gitattributes", 5)]:
    data = Path(rel).read_bytes()
    print(rel, "bytes", len(data), "LF", data.count(b"\n"), "CR", data.count(b"\r"))
    assert data.count(b"\r") == 0
    assert data.count(b"\n") >= min_lf
PY

node tools/test_smoke_script_sanity.js
bash -n scripts/smoke.sh
bash scripts/smoke.sh
```

Wichtig: Den echten Output in die Commit-Message schreiben. Nicht rekonstruieren.

---

## 4. Kleine Restdrift: `optional arena` entfernen

### Befund

In `systems/gameflow/speicher-fortsetzung.md` steht in einem aktiven Satz noch sinngemäß:

```text
Pflichtfelder (v7-Export): ... `logs`, `ui` und optional `arena`.
```

Das widerspricht dem neuen strict-v7-Vertrag: `arena` ist Root-Pflichtblock, auch im Idle-Default.

### Patch

Ändern zu:

```text
Pflichtfelder (v7-Export): `v`, `zr`, `campaign.px`, `characters[]`
(kanonischer Charakterbogen inkl. `wallet`, `history`, `carry`,
`quarters_stash`, `vehicles`), `economy.hq_pool`, `arc`, `logs`,
`ui` und `arena` als vollständiger Default-/Checkpoint-Block.
```

Prüfe, dass `tools/test_v7_export_fieldlist_watchguard.js` bei `arena?`/`optional arena` künftig failt. Der Test blockt bereits `arena?`, sollte aber zusätzlich auf `/optional\s+`?`?arena/i` oder den deutschen Satz prüfen.

---

## 5. Legacy-v7-Block härter entwaffnen

### Befund

`speicher-fortsetzung.md` enthält weiterhin einen großen, kopierfähigen JSON-Codeblock mit:

- `"v": 7`
- `"zr_version"`
- root `"location"`
- root `"phase"`
- root `"character"`
- `characters[].attributes` statt `attr`
- alte Log-Felder

Der Block ist mit Warnhinweisen versehen und als Legacy-/Import-Bridge markiert. Das ist besser als vorher. Trotzdem bleibt er LLM-gefährlich, weil ein großer `json`-Block mit `"v": 7` leicht als Beispiel für `!save` imitiert wird.

### Patch-Option A, empfohlen

Den Codeblock aus `speicher-fortsetzung.md` in einen Appendix oder `internal/qa/legacy_import_examples.md` verschieben und im Wissensspeicher nur einen kurzen Hinweis behalten:

```text
Legacy-Importbeispiele liegen außerhalb des aktiven Spiel-Wissensspeichers.
Sie sind nur für Repo-Tests und Migrationen bestimmt. Kein JSON-Block in
diesem Abschnitt darf als `!save`-Vorlage imitiert werden.
```

### Patch-Option B, falls A zu groß ist

Code-Fence von `json` auf `text` ändern und davor/danach jeweils in Großschrift:

```text
IMPORT-ONLY / NICHT KOPIEREN / KEIN !save-BEISPIEL
```

Zusätzlich den Block hinter das Kompakt-Profil verschieben, damit der kanonische Vertrag zuerst kommt.

---

## 6. Akzeptanz

Dieser Pass gilt nur als bestanden, wenn:

```bash
git diff --check

python3 - <<'PY'
from pathlib import Path
for rel, min_lf in [("scripts/smoke.sh", 80), (".gitattributes", 5)]:
    data = Path(rel).read_bytes()
    print(rel, "bytes", len(data), "LF", data.count(b"\n"), "CR", data.count(b"\r"))
    assert data.count(b"\r") == 0
    assert data.count(b"\n") >= min_lf
PY

node tools/test_eol_lf_watchguard.js
node tools/test_smoke_script_sanity.js
node tools/test_v7_export_fieldlist_watchguard.js
node tools/test_px_language_watchguard.js
node tools/test_v7_character_optional_fields_schema.js
bash -n scripts/smoke.sh
bash scripts/smoke.sh
```

Zusätzlich nach Push prüfen:

- Raw-Download von `scripts/smoke.sh` zeigt viele LF-Zeilen, nicht 2.
- Raw-Download von `.gitattributes` zeigt 6 LF-Zeilen, nicht 1.
- GitHub UI und Raw sind sich beim Zeilenbild einig.
- In `speicher-fortsetzung.md` steht kein aktiver Satz mehr, der `arena` optional nennt.
- Der große Legacy-Block ist nicht mehr als kopierfähiges v7-`json`-Save-Beispiel im aktiven Wissensspeicher präsent.

---

## Commit Message

```text
fix(v7): lock LF smoke gate and remove final save-contract drift
```

Body:

```text
## Was
- Normalize smoke.sh and .gitattributes to LF-only.
- Add/anchor EOL watchguard for smoke gate.
- Remove final optional-arena wording.
- De-arm or relocate legacy v7 import JSON example.

## Warum
The v7 save contract is now largely aligned, but Raw still exposed CR/collapsed
EOL in the release gate files. This made smoke unreliable and kept the final
Jubeltest formally blocked.

## Verifikation
<echten Output der Akzeptanzbefehle einfügen>
```
