# Sweep 3 — Runtime/Toolkit-Drift

**Scope:** Reiner Lese-Audit. Drift zwischen den 5 WS-Doku-Patches (#3192–#3195) und der Runtime-/Toolkit-/Smoke-Schicht.
**Repo:** `/mnt/agent_share/cloud/repos/ZEITRISS-md-git` @ `main` (HEAD `5d6cd8ac`)
**Datum:** 2026-06-02

## Architektur-Vorklärung (wichtig für die Bewertung)

- **Masterprompt = System-Prompt, nicht WS-Slot.** `setup.json` (`"masterprompt": "meta/masterprompt_v6.md"`) und `.openwebui-sync.json` (`masterprompt_path` getrennt von `kb_files`) bestätigen: Der Masterprompt wird als OpenWebUI-Preset/System-Prompt geladen, nicht als Wissensspeicher-Datei. Er ist daher **immer** für die KI-SL sichtbar. Dass er nicht in `master-index.json` steht, ist **kein** Sichtbarkeits-Gap, sondern korrekt (master-index führt nur KB-Slots).
- **`runtime.js`/`toolkit-runtime-makros.md`/smoke = CI-/Makro-Schicht**, nicht Spiellogik. Die KI-SL liest Prosa (Masterprompt + 18 KB-Slots), nicht die Makros. Drift hier ist meist „kosmetisch für die Live-Runde, aber Schema-/Test-relevant" — außer wenn der Masterprompt selbst inkonsistent ist (dann sieht die SL es).

---

## Toolkit-Makro-Abgleich

**Debrief-Makro-Sequenz kennt den Research-Tick NICHT.**

`internal/runtime/toolkit-runtime-makros.md:1280`
```
⟨% macro debrief() -%⟩
⟪ render_rewards() ⟫
⟨% set temp_src = resolve_temp_for_px() %⟩
⟪ px_tracker(temp_src) ⟫
⟨%- endmacro %⟩
```
Die Makro-`debrief()`-Sequenz macht genau zwei Dinge: `render_rewards()` + `px_tracker()`. **Kein `research_tick`-Schritt, kein `research`-Hook.** Der Masterprompt schreibt dagegen seit #3194 (masterprompt_v6.md:98) eine erweiterte Debrief-Reihenfolge vor: `Score-Screen → Loot-Recap → CU-Auszahlung → XP/Level-Up → ITI-Ruf-Update → Px-Resonanz-Beat → Research-Tick → Lizenz-Tier`.
→ **Drift, UNKRITISCH** (Makro ist CI-Stub, nicht Live-Spiellogik; die SL folgt der Masterprompt-Prosa). Aber: siehe Punkt „Gesamturteil" — die Makro-Sequenz ist die einzige maschinell prüfbare Repräsentation der Debrief-Reihenfolge und hinkt der Doku jetzt zwei Beats hinterher (Px-Resonanz-Beat + Research-Tick).

**Px-Resonanz-Beat: Makro-Hook existiert teilweise.**
`px_tracker()` ist in `debrief()` eingehängt und der Debrief-Score-Screen zeigt seit jeher `Resonanz Px n/5` (`systems/toolkit-gpt-spielleiter.md:585`). #3195 reichert diesen bestehenden Beat mit In-World-Resonanz + Riss-Ortung an — also Anreicherung eines vorhandenen Hooks, **keine neue Makro-Pflicht**. Px5→`ClusterCreate()` ist ebenfalls vorhanden (`toolkit-gpt-spielleiter.md:597,603`; Makros `internal/runtime/...` nicht separat nötig). → **kein kritischer Drift.**

**Save-Serializer kennt `research.projects[]` NICHT.**
`grep "research.projects|field_decrypt|hq_research|missions_done"` über `toolkit-gpt-spielleiter.md` + `toolkit-runtime-makros.md` + `runtime-stub-routing-layer.md`: **NICHT GEFUNDEN.** Die Makro-Schicht serialisiert/normalisiert den neuen Root-Block nicht. → konsistent mit „Makro-Schicht = Stub", aber Beleg, dass `research` nirgends maschinell verankert ist.

**Achtung Namens-Falle:** `runtime.js` und Makros kennen `campaign.research_level` (Integer-Tech-Tree-Gate für Chronopolis-Shop, `runtime.js:3882, 6993, 7094`; Makro `toolkit-runtime-makros.md:35`). Das ist ein **völlig anderes Konzept** als der neue `research.{projects[]}`-Save-Block aus #3194. Nicht verwechseln — der neue Block hat **keinerlei** Runtime-Repräsentation.

## Smoke-Test-Coverage (research-Block getestet?)

**`research`-Block wird von KEINEM Test geprüft. NICHT GEFUNDEN in `tools/`, `scripts/`, `runtime.js`, `smoke.sh`.**

Vorhandene Save-Watchguards und ihre `research`-Blindheit:
- `tools/test_v7_export_fieldlist_watchguard.js:24-32` — `requiredSnippets` listet `campaign/logs/arena/ui/...`, **kein `research`**. Liest `speicher-fortsetzung.md` „v7-Export-Pflichtfelder"-Block; research steht dort nicht (siehe SSOT-Abschnitt).
- `tools/test_v7_schema_consistency.js:184` — `rootRequired = ['v','zr','save_id','parent_save_id','merge_id','branch_id','campaign','characters','economy','logs','summaries','continuity','arc','ui','arena']` — **`research` fehlt.** Strict-Fixtures dürfen `research` weglassen und gelten trotzdem als „strict vollständig".
- `scripts/lint_save_sync.py` — `grep research` = **NICHT GEFUNDEN**.
- `internal/qa/fixtures/savegame_v7_*.json` (10 Stück) — **keine** enthält `research.projects[]`. (Einzige Erwähnung: `savegame_v6_full.json:719` `"status": "research"` — unverwandter String.)
- `tools/test_debrief.js` / `smoke.sh:56-59` prüft den Debrief-Score-Screen inkl. `Resonanz Px [0-5]/5` und `Px … TEMP` — **Px-Resonanz IST getestet**, Research-Tick **nicht**.

**Bewertung: UNKRITISCH-mit-Auge.** Kein Save-Roundtrip-Test deckt `research` ab. Das wäre kritisch, *wenn* `research` ein Pflichtfeld mit hartem SaveGuard wäre. Ist es aber laut Migrations-Regel **nicht**: `speicher-fortsetzung.md:1214` — *„Ein in Legacy-/pre-Research-Saves fehlender `research`-Block wird beim Laden als `research: {projects: []}` initialisiert"*, und ein Projekt ohne `scope` → `campaign` (kein rückwirkendes Cap). `research` ist also ein **optionaler, safe-default Block**. Fehlende Test-Coverage ist daher ein **Gap, kein Bug** — aber empfehlenswert nachzuziehen, sobald research einen Pflicht-Status oder SaveGuard bekommt.

## Wissensspeicher-Sichtbarkeit (sind alle Patches in WS-Slots?)

**Alle 5 Patches landen in sichtbaren Flächen. KEIN Sichtbarkeits-Gap.**

| Patch | Geänderte Datei | In `master-index.json` (Slot) | In `.openwebui-sync.json` kb_files | Sichtbar für KI-SL? |
|---|---|---|---|---|
| #3192 | meta/masterprompt_v6.md | n/a (= System-Prompt) | masterprompt_path | ✅ System-Prompt |
| #3192 | gameplay/kampagnenstruktur.md | `kampagnenstruktur` slot:true | ✅ | ✅ |
| #3192 | gameplay/kreative-generatoren-missionen.md | `generatoren-missionen` slot:true | ✅ | ✅ |
| #3192 | core/sl-referenz.md | `sl-referenz` slot:true | ✅ | ✅ |
| #3193 | gameplay/kreative-generatoren-begegnungen.md | `generatoren-begegnungen` slot:true | ✅ | ✅ |
| #3193 | gameplay/kreative-generatoren-missionen.md | (s.o.) | ✅ | ✅ |
| #3194 | systems/gameflow/speicher-fortsetzung.md | `save` slot:true | ✅ (`speicher-fortsetzung.md`) | ✅ |
| #3194/#3195 | meta/masterprompt_v6.md | n/a (= System-Prompt) | masterprompt_path | ✅ System-Prompt |

Masterprompt-Inhalte verifiziert sichtbar: Research-Pflichtgate (masterprompt_v6.md:107-109), Px-Resonanz/Research-Tick in Debrief-Sequenz (`:98`), Arena-Sofort-Action-Pflicht (`:934`). Alles im aktiv geladenen System-Prompt. → **kein Gap.**

## Save-Schema-SSOT-Konsistenz (research im Masterprompt-JSON?)

**🔴 ECHTER KONSISTENZ-BUG: `research` fehlt im Masterprompt-JSON-Save-Template, obwohl es als Pflicht-Root-Block deklariert ist.**

Repo-AGENTS.md ist eindeutig:
- `AGENTS.md:19` — *„Schema-SSOT ist der Masterprompt."*
- `AGENTS.md:97` — *„Save-Schema v7 — Template im Masterprompt ist SSOT."*

Das kanonische JSON-Template im Masterprompt (`meta/masterprompt_v6.md:948-1078`, der einzige kopierfähige `!save`-Block) enthält die Root-Blöcke:
`v, zr, save_id, parent_save_id, merge_id, branch_id, campaign, characters, economy, logs, summaries, continuity, arc, ui, arena`
→ **`research` ist NICHT im Template.** (grep „research" im Masterprompt findet nur Prosa-Pflichtgate `:98,107,109` + `shared_echoes`-Beispiele, **keinen** Eintrag im JSON-Block `:948-1078`.)

Gleichzeitig deklariert `speicher-fortsetzung.md`:
- `:328` (Kompakt-Profil) — *„`economy`, **`research`**, `logs`, … liegen immer auf Root-Ebene"*
- `:349` — *„`research.{projects[]}` … Leeres Array, wenn nichts läuft."* (vollständiges Feld-Schema)

→ **Der Masterprompt (Schema-SSOT) und speicher-fortsetzung.md widersprechen sich.** speicher-fortsetzung listet research als Root-Pflichtblock; das SSOT-Template kennt ihn nicht. Ein KI-SL, die strikt „alle Felder Pflicht, kein Feld weglassen" (masterprompt_v6.md:945) gegen das Template prüft, würde `research` beim `!save` **nie ausgeben** — der missions-getaktete Fortschritt aus #3194 ginge bei jedem Save/Load verloren, obwohl er persistent gemeint ist.

**Verschärfend — die maschinelle SSOT-Spur ist ebenfalls research-blind:**
- `speicher-fortsetzung.md` „v7-Export-Pflichtfelder (kanonisch)"-Block (gelesen vom `v7-export-fieldlist-watchguard`) listet **alle** Root-Blöcke explizit auf — **außer `research`**. Header sagt sogar *„Template-SSOT = Masterprompt §F"*, ist also bewusst mit dem (research-losen) Masterprompt-Template synchronisiert.
- `test_v7_schema_consistency.js:184` `rootRequired` ohne `research`.

→ Die Doku ist **in sich gespalten**: Prosa-Pflichtgate + Kompakt-Profil-Pfadbaum sagen „research ist Pflicht-Root", aber das kanonische Template + die kanonische Export-Pflichtfeldliste + die Schema-Tests sagen „research existiert nicht".

**Mildernd:** Die Migrations-Regel (`:1214`) macht `research` faktisch optional mit safe default (`{projects:[]}`). Es ist also **kein** Crash-/Load-Bug. Aber es ist ein **echter Schema-SSOT-Widerspruch** im Sinne von AGENTS.md: Feature #3194 ist nur halb im Schema verankert. Bei strikter Template-Treue der SL verpufft das Feature.

## Gesamturteil + kritische Gaps

**Es gibt kritischen Drift — aber genau an einer Stelle: der Save-Schema-SSOT (Punkt 4).**

🔴 **KRITISCH (Schema-SSOT-Inkonsistenz):** `research.{projects[]}` ist als Pflicht-Root-Block in `speicher-fortsetzung.md:328/349` deklariert, fehlt aber im kanonischen JSON-Save-Template des Masterprompts (`masterprompt_v6.md:948-1078`) — dem laut `AGENTS.md:19,97` einzigen Schema-SSOT. Konsequenz: Eine SL, die das Template als „alle Felder Pflicht" liest, gibt `research` nie aus → missions-getakteter Forschungs-Fortschritt aus #3194 ist nicht save-persistent. **Fix-Vorschlag (1 Stelle):** `research: { projects: [] }`-Root in den Masterprompt-JSON-Block aufnehmen (zwischen `economy` und `logs`, passend zur Root-Reihenfolge in speicher-fortsetzung). Optional konsistenzhalber: `research` in den „v7-Export-Pflichtfelder"-Block + `rootRequired` in `test_v7_schema_consistency.js` aufnehmen, sonst bleibt das Feld dauerhaft test-unsichtbar.

🟡 **UNKRITISCH, aber beobachten:**
- Debrief-Makro (`toolkit-runtime-makros.md:1280`) kennt weder `research_tick` noch den `px_resonanz`-Beat — Makro ist CI-Stub, hinkt der Masterprompt-Debrief-Reihenfolge jetzt zwei Beats hinterher. Live-Spiel unbeeinträchtigt (SL folgt Prosa).
- Kein Test deckt den `research`-Block ab (Smoke/Fixtures/lint_save_sync). Solange `research` optional-mit-safe-default bleibt, tolerierbar; nachziehen, sobald research SaveGuard/Pflichtstatus erhält.

✅ **Sauber:** Wissensspeicher-Sichtbarkeit (alle 5 Patches in WS-Slots bzw. System-Prompt), Px-Resonanz (getestet via `test_debrief.js`, Hook via `px_tracker()`), Arena-Sofort (im sichtbaren Masterprompt `:934`), ClusterCreate/Px5 (toolkit vorhanden).
