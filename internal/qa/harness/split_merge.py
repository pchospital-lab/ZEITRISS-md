#!/usr/bin/env python3
"""
ZEITRISS 5er-Split/Merge-Harness (2026-06-16) — Variante A (Mechanik-Canary)
============================================================================
Testet die Save-/Merge-MECHANIK an den Sync-Punkten (docs/testing.md §P1-1),
NICHT das Spielgefühl. Das ist der billige Canary VOR dem teuren organischen
Persona-Lauf (Variante B).

WARUM gescriptete Spieler-Eingaben (kein Persona-LLM)?
  A isoliert die SL-Merge-Mechanik. Persona-Rauschen würde den Test
  nicht-deterministisch machen und Tokens verbrennen, ohne mehr über das
  Schema-/Merge-Verhalten auszusagen. Die Eingaben steuern gezielt die
  Sync-Punkte an: Anker-Load -> Split -> Branch-Saves -> Merge.

ABLAUF (4/1-Split, kanonisch):
  Chat#1 (Anker):  5er-HQ-Save laden -> Kontinuitätsrückblick + HQ-Hub
                   -> Split ankündigen -> SL Split-Beat + 2 Branch-Saves
  Chat#2 (4er):    Branch-A-Save laden -> kurzer HQ-Beat -> !save (Ergebnis A)
  Chat#3 (1er):    Branch-B-Save laden -> kurzer HQ-Beat -> !save (Ergebnis B)
  Chat#4 (Merge):  beide Ergebnis-Saves laden -> SL Merge + Rückblick -> !save

VALIDIERUNG (merge_assert.py, gegen Repo-Kanon):
  - validate_export (volles v7-Schema) auf jeden !save-Output
  - assert_merge auf das Merge-Ergebnis (Anker-Priorität, resolved_threads,
    convergence_ready, Echo-Dedup, Seed-Cap, imported_saves)
  - Pflichtbeats (Split-Beat, Rejoin-HQ-Beat) via Text-Heuristik

KOSTEN: usage.cost (echt, von OWUI/LiteLLM) wird pro Turn mitgeschrieben.
        Cache-Hit-Rate aus prompt_tokens_details.cached_tokens.

Aufruf:
  set -a; . ~/.openwebui_env; set +a
  python3 harness/split_merge.py --case 4-1 [--max-turns-per-phase 8]

Env: OPENWEBUI_URL, OPENWEBUI_API_KEY
"""
from __future__ import annotations
import argparse
import json
import os
import re
import signal
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from owui_client import OWUIChat  # noqa: E402
import merge_assert as MA  # noqa: E402

# ─── Config ───────────────────────────────────────────────────────────────────
BASE_URL = os.environ.get("OPENWEBUI_URL", "http://127.0.0.1:8080")
API_KEY = os.environ.get("OPENWEBUI_API_KEY", "")
SL_MODEL = "zeitriss-v426-uncut"
KB_ID = "a56706c9-e427-4c6c-9dcb-0eb7cea095c0"
TIMEOUT_SL = 420

REPO = Path("/mnt/agent_share/cloud/repos/ZEITRISS-md-git")
ANCHOR_FIXTURE = REPO / "internal" / "qa" / "fixtures" / "savegame_v7_5er_hq_highlevel.json"

HOME = Path(os.path.expanduser("~"))
PLAYTESTS = HOME / ".openclaw" / "workspace-cloud" / "playtests" / "zeitriss"
RUNNING_DIR = HOME / ".openclaw" / "workspace-cloud" / "tmp" / "running"
RUNNING_DIR.mkdir(parents=True, exist_ok=True)

# ─── Save-Extraktion (multi-fähig, anders als solo_journey extract_save) ───────
def extract_all_saves(text: str) -> list[dict]:
    """Findet ALLE v7-Save-JSON-Blöcke im SL-Output (Split gibt 2 Saves)."""
    out: list[dict] = []
    seen: set[str] = set()
    # 1) ```json ... ``` Fences (bevorzugt)
    for m in re.finditer(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL):
        obj = _try_v7(m.group(1))
        if obj is not None:
            key = obj.get("save_id") or json.dumps(obj, sort_keys=True)[:80]
            if key not in seen:
                seen.add(key)
                out.append(obj)
    # 2) Fallback: nacktes Top-Level-JSON, nur wenn keine Fences gefunden
    if not out and '"v"' in text:
        start, end = text.find("{"), text.rfind("}")
        if 0 <= start < end:
            obj = _try_v7(text[start:end + 1])
            if obj is not None:
                out.append(obj)
    return out


def _try_v7(blob: str) -> dict | None:
    try:
        obj = json.loads(blob)
    except (json.JSONDecodeError, ValueError):
        return None
    if isinstance(obj, dict) and obj.get("v") == 7 and "characters" in obj:
        return obj
    return None


def save_mode(save: dict) -> str:
    try:
        return save["continuity"]["last_seen"]["mode"]
    except (KeyError, TypeError):
        return "?"


# ─── Save-Zwang (gehaertet) ───────────────────────────────────────────────────
# Prosa-statt-JSON ist die haeufigste Save-Erfassungsluecke: die SL antwortet
# "Ich habe gespeichert ..." / "Speicherstand erstellt" ohne JSON-Block. Frueher
# gab der Harness nach einem schwachen "!save"-Retry auf -> Folgepruefungen
# (z.B. Konflikt-Check) liefen nie. Diese Heuristik erkennt den Prosa-Fall, und
# request_save eskaliert die Aufforderung mehrstufig, bevor es FAILt.
_SAVE_PROSE_RE = re.compile(
    r"(gespeichert|speicherstand|speicher-stand|save\s+erstellt|abgespeichert|"
    r"stand gesichert|gesichert\b|!save ausgef|saved)",
    re.IGNORECASE,
)


def claims_save_in_prose(text: str) -> bool:
    """True, wenn der SL-Text einen Save behauptet, aber KEIN v7-JSON-Block da ist."""
    return bool(_SAVE_PROSE_RE.search(text)) and not extract_all_saves(text)


# Eskalationsstufen fuer den Save-Zwang. Jede Stufe wird nur gefahren, wenn die
# vorige keinen JSON-Save lieferte. Bewusst zunehmend explizit/streng.
_SAVE_ESCALATION = [
    "!save",
    ("Bitte gib den Speicherstand JETZT als vollstaendigen v7-JSON-Block aus, "
     "eingefasst in einen ```json ... ``` Codeblock. Kein Fliesstext, keine "
     "Zusammenfassung — nur der JSON-Block."),
    ("SYSTEM/Testharness: Der vorige Output enthielt KEINEN maschinenlesbaren "
     "Speicherstand. Gib ausschliesslich den kompletten v7-Save als einen "
     "einzigen ```json-Codeblock aus (Felder v, zr, characters, economy, "
     "continuity ...). Beginne deine Antwort direkt mit ```json."),
]


def request_save(run: "Run", sl: "OWUIChat", phase: str, label: str,
                 want: int = 1, seed_text: str = "") -> list[dict]:
    """Fordert mind. `want` v7-Saves an und eskaliert bei Prosa-statt-JSON.
    Gibt die extrahierten Saves zurueck (ggf. leer). Protokolliert einen
    praezisen PROSE-SAVE-Befund, wenn die SL einen Save nur behauptet hat.
    `seed_text` haengt bereits gesehenen SL-Text vorne an, damit dort schon
    enthaltene Saves nicht verloren gehen (z.B. P1-Split-Vorlauf).
    """
    last = sl.history[-1]["content"] if sl.history else ""
    accumulated_text = (seed_text + "\n" + last) if seed_text else last
    saves = extract_all_saves(accumulated_text)
    prose_only_seen = False
    for stage, prompt in enumerate(_SAVE_ESCALATION, start=1):
        if len(saves) >= want:
            break
        if claims_save_in_prose(accumulated_text):
            prose_only_seen = True
            run.log(f"  ⚠️ [{phase}] SL behauptet Save in Prosa, kein JSON-Block "
                    f"-> Eskalation Stufe {stage}")
        txt = sl_say(run, sl, prompt, phase, f"{label} [Save-Zwang {stage}/{len(_SAVE_ESCALATION)}]")
        accumulated_text += "\n" + txt
        saves = extract_all_saves(accumulated_text)
    if prose_only_seen and saves:
        run.findings.append(MA.Finding("SAVE-PROSE", "SOFT",
            f"{phase}: SL gab Save erst nach Eskalation als JSON (zuerst nur Prosa)"))
    elif prose_only_seen and not saves:
        run.findings.append(MA.Finding("SAVE-PROSE", "FAIL",
            f"{phase}: SL behauptete Save in Prosa, lieferte aber trotz Eskalation "
            f"kein JSON (Save-Zwang verletzt)"))
    return saves


# ─── Pflichtbeat-Heuristik (speicher-fortsetzung.md §Pflichtbeats) ────────────
def detect_beats(text: str) -> dict[str, bool]:
    t = text.lower()
    return {
        "split_beat": bool(re.search(r"\b(teilt? euch|aufteil|split|getrennte wege|"
                                     r"trennt euch|zwei (gruppen|teams|threads|branches)|"
                                     r"spaltet|branch-trennung|split-protokoll|"
                                     r"sync-station|family_id)", t)),
        "rejoin_beat": bool(re.search(r"\b(wieder (zusammen|vereint)|rückkehr|kehrt? "
                                      r"zurück|treffen euch|zusammenführ|rejoin|"
                                      r"andocken|heimkehr|konvergenz|merge|vereint)", t)),
        "continuity_recap": bool(re.search(r"\b(session-?anker|kontinuität|rückblick|"
                                           r"rückkehrer|nachwirkung|konvergenz)", t)),
    }


# ─── Run-Logging ──────────────────────────────────────────────────────────────
class Run:
    def __init__(self, case: str):
        stamp = time.strftime("%Y-%m-%d-%H%M")
        self.out = PLAYTESTS / "runs" / f"{stamp}-split-merge-{case}"
        self.out.mkdir(parents=True, exist_ok=True)
        self.saves_dir = self.out / "saves"
        self.saves_dir.mkdir(exist_ok=True)
        self.log_path = self.out / "_live.log"
        self.report = self.out / "_transkript.md"
        self.jsonl = self.out / "turns.jsonl"
        self.case = case
        self.cum_cost = 0.0
        self.cum_prompt = 0
        self.cache_hits: list[float] = []
        self.findings: list[MA.Finding] = []
        self.turn = 0

    def log(self, msg: str):
        line = f"[{time.strftime('%H:%M:%S')}] {msg}"
        print(line, flush=True)
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    def rep(self, text: str):
        with self.report.open("a", encoding="utf-8") as fh:
            fh.write(text + "\n\n")

    def jlog(self, obj: dict):
        with self.jsonl.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(obj, ensure_ascii=False) + "\n")

    def account(self, usage: dict):
        cost = usage.get("cost")
        if isinstance(cost, (int, float)):
            self.cum_cost += cost
        ptok = usage.get("prompt_tokens", 0)
        self.cum_prompt = max(self.cum_prompt, ptok)
        det = usage.get("prompt_tokens_details") or {}
        cached = det.get("cached_tokens", 0)
        if ptok:
            self.cache_hits.append(cached / ptok)

    def add_findings(self, res: MA.Result, phase: str):
        for f in res.findings:
            self.findings.append(f)
            sev = {"FAIL": "❌", "SOFT": "⚠️", "INFO": "ℹ️"}.get(f.severity, "·")
            self.log(f"  {sev} [{phase}] {f.code}: {f.msg}")
            self.rep(f"> {sev} **[{phase}] {f.code}:** {f.msg}")


def sl_say(run: Run, sl: OWUIChat, user_text: str, phase: str, label: str) -> str:
    run.turn += 1
    run.log(f">>> [{phase}] Spieler: {label}")
    run.rep(f"**Spieler [{phase}]:** {label}")
    res = sl.say(user_text)
    txt = res["content"]
    run.account(res["usage"])
    src = sl.source_files()
    cache = run.cache_hits[-1] if run.cache_hits else 0
    run.log(f"<<< [{phase}] SL ({len(txt)} chars, {res['usage'].get('prompt_tokens',0)} ptok, "
            f"cache {cache:.0%}, RAG={len(src)}, cum ${run.cum_cost:.4f})")
    run.rep(f"### [{phase}] SL\n\n{txt}")
    if src:
        run.rep(f"> _RAG: {', '.join(src)}_")
    run.jlog({"turn": run.turn, "phase": phase, "label": label, "sl": txt,
              "usage": res["usage"], "rag": src})
    return txt


def validate_and_store(run: Run, save: dict, name: str, phase: str) -> MA.Result:
    sp = run.saves_dir / f"{name}.json"
    sp.write_text(json.dumps(save, ensure_ascii=False, indent=2))
    run.log(f"  💾 Save '{name}' (mode={save_mode(save)}) -> {sp.name}")
    res = MA.validate_export(save, name)
    res.merge(MA.check_echo_formats(save, name))
    res.merge(MA.check_seed_cap(save, name))
    run.add_findings(res, phase)
    return res


# ─── Generischer Split/Merge-Case ─────────────────────────────────────────────
# Partition: Liste von Agent-Gruppen, z.B. [["A","B","C","D"],["E"]] = 4/1.
CASES: dict[str, dict] = {
    "4-1":  {"partition": [["A", "B", "C", "D"], ["E"]], "desc": "4/1-Split (kanonisch)"},
    "3-2":  {"partition": [["A", "B", "C"], ["D", "E"]], "desc": "3/2-Split mit Rejoin"},
    "resplit": {"partition": [["A", "B", "C"], ["D", "E"]], "resplit": [["A", "B"], ["C"]],
                "desc": "Resplit 3→2/1 (erste Gruppe teilt sich erneut)"},
    "konflikt": {"partition": [["A", "B", "C", "D"], ["E"]], "conflict": True,
                 "desc": "Konfliktfall / non-canonical Import (doppelte Charakter-ID)"},
}


def run_split_case(run: Run, case: str, max_tpp: int):
    spec = CASES[case]
    partition = spec["partition"]
    anchor_save = json.loads(ANCHOR_FIXTURE.read_text(encoding="utf-8"))
    run.rep(f"# 5er-Split/Merge — Case {case} ({spec['desc']})\n\n"
            f"**Datum:** {time.strftime('%Y-%m-%d %H:%M')}  \n"
            f"**SL:** {SL_MODEL} (OWUI-RAG)  \n"
            f"**Anker-Fixture:** `{ANCHOR_FIXTURE.name}` (5× Lvl 900+)\n\n---\n")

    # ── Phase 1: Anker-Load + Split ──
    chat1 = OWUIChat(BASE_URL, API_KEY, SL_MODEL, kb_id=KB_ID, timeout=TIMEOUT_SL)
    run.log(f"=== Phase 1 (Anker) — Chat {chat1.chat_id} ===")
    run.rep("## 🗂 Chat #1 — Anker-Load (5er-Gruppe im HQ)\n")
    load_msg = ("Spiel laden:\n\n```json\n" + json.dumps(anchor_save, ensure_ascii=False) + "\n```")
    txt = sl_say(run, chat1, load_msg, "P1-load", "[5er-HQ-Save laden]")
    if not detect_beats(txt)["continuity_recap"]:
        run.findings.append(MA.Finding("RECAP", "SOFT", "Kein Kontinuitätsrückblick beim Anker-Load"))
        run.log("  ⚠️ [P1] kein Kontinuitätsrückblick")

    groups_desc = " / ".join("+".join(g) for g in partition)
    split_req = (
        f"Wir wollen uns am Sync-Punkt aufteilen ({len(partition)} Gruppen): {groups_desc}. "
        "Leite den Split ein und erstelle für JEDE Gruppe einen eigenen "
        "Speicherstand (!save) mit gesetztem continuity.split (family_id, thread_id, "
        "expected_threads), damit wir sie in getrennten Chats weiterspielen."
    )
    txt2 = sl_say(run, chat1, split_req, "P1-split", f"[{case}-Split + !save je Gruppe]")
    if not detect_beats(txt2)["split_beat"]:
        run.findings.append(MA.Finding("SPLIT-BEAT", "SOFT", "Kein expliziter Split-Beat erkannt"))

    branch_saves = extract_all_saves(txt2)
    if len(branch_saves) < len(partition):
        run.log(f"  … {len(branch_saves)}/{len(partition)} Saves, fordere getrennt nach")
        txt3 = sl_say(run, chat1,
                      f"Bitte gib mir alle {len(partition)} Speicherstände getrennt als JSON "
                      f"({groups_desc}), jeweils mit continuity.split gesetzt.",
                      "P1-split2", "[alle Branch-Saves getrennt anfordern]")
        branch_saves = extract_all_saves(txt2 + "\n" + txt3)
    # Save-Zwang gehaertet: wenn immer noch zu wenige, bei Prosa-statt-JSON eskalieren
    if len(branch_saves) < len(partition):
        branch_saves = request_save(run, chat1, "P1-split",
                                    f"[{len(partition)} Branch-Saves]", want=len(partition),
                                    seed_text=txt2 + "\n" + txt3)

    run.log(f"  → {len(branch_saves)} Branch-Save(s) extrahiert (erwartet {len(partition)})")
    for i, s in enumerate(branch_saves):
        n = len(s.get("characters", []))
        validate_and_store(run, s, f"p1-branch{i+1}-{n}er", "P1")
    if len(branch_saves) < len(partition):
        run.findings.append(MA.Finding("SPLIT-SAVES", "FAIL",
                            f"Split erzeugte {len(branch_saves)}/{len(partition)} Branch-Saves"))
        return finalize(run, merge_save=None, anchor=anchor_save, branches=[])

    # nach Charakterzahl absteigend sortieren (größte Gruppe = Branch 1)
    branch_saves = sorted(branch_saves, key=lambda s: -len(s.get("characters", [])))[:len(partition)]

    # ── Optionaler Resplit der ersten Gruppe ──
    if spec.get("resplit"):
        run.log("  ↪ Resplit der ersten Gruppe")
        first = branch_saves[0]
        rchat = OWUIChat(BASE_URL, API_KEY, SL_MODEL, kb_id=KB_ID, timeout=TIMEOUT_SL)
        run.rep("## 🗂 Chat — Resplit erste Gruppe\n")
        sl_say(run, rchat, "Spiel laden:\n\n```json\n" + json.dumps(first, ensure_ascii=False) + "\n```",
               "resplit", "[erste Gruppe laden]")
        rgroups = " / ".join("+".join(g) for g in spec["resplit"])
        rtxt = sl_say(run, rchat,
                      f"Diese Gruppe teilt sich erneut am Sync-Punkt: {rgroups}. "
                      "Erstelle für jede Untergruppe einen eigenen !save mit continuity.split.",
                      "resplit", f"[Resplit {rgroups}]")
        re_saves = extract_all_saves(rtxt)
        for i, s in enumerate(re_saves):
            validate_and_store(run, s, f"resplit-{i+1}", "resplit")
        if len(re_saves) >= 2:
            branch_saves = re_saves + branch_saves[1:]  # Resplit-Teile + Rest
            run.log(f"  → nach Resplit {len(branch_saves)} Branches gesamt")
        else:
            run.findings.append(MA.Finding("RESPLIT", "FAIL",
                                f"Resplit erzeugte nur {len(re_saves)} Save(s)"))

    # ── Branches kurz spielen ──
    results = []
    for i, bs in enumerate(branch_saves):
        n = len(bs.get("characters", []))
        r = play_branch(run, bs, f"{i+1}-{n}er", max_tpp)
        if r:
            results.append(r)

    if len(results) < 2:
        run.log("  ❌ ABBRUCH: <2 Branches mit Ergebnis-Save")
        return finalize(run, merge_save=None, anchor=anchor_save, branches=results)

    # ── Konfliktfall: künstliche Duplikat-Charakter-ID injizieren ──
    if spec.get("conflict") and results:
        dup = json.loads(json.dumps(results[-1]))  # deep copy letzter Branch
        # erste Char-ID des ersten Branches duplizieren -> Rejoin-Konflikt
        if results[0].get("characters"):
            dup_id = results[0]["characters"][0].get("id")
            if dup.get("characters"):
                dup["characters"][0]["id"] = dup_id
                dup["save_id"] = (dup.get("save_id") or "DUP") + "-CONFLICT"
                run.log(f"  ⚡ Konflikt-Injektion: dupliziere Char-ID '{dup_id}' in Zusatz-Save")
                run.rep(f"> ⚡ **Konflikt-Setup:** Zusatz-Save mit dupliziertem `{dup_id}` injiziert")
                results.append(dup)

    # ── Merge ──
    merge_save = play_merge(run, results, max_tpp)
    finalize(run, merge_save=merge_save, anchor=anchor_save, branches=results,
             conflict_expected=spec.get("conflict", False))


def play_branch(run: Run, branch_save: dict, tag: str, max_tpp: int) -> dict | None:
    chat = OWUIChat(BASE_URL, API_KEY, SL_MODEL, kb_id=KB_ID, timeout=TIMEOUT_SL)
    run.log(f"=== Branch {tag} — Chat {chat.chat_id} ===")
    run.rep(f"## 🗂 Chat — Branch {tag} (Save geladen, kurzer HQ-Beat)\n")
    load = "Spiel laden:\n\n```json\n" + json.dumps(branch_save, ensure_ascii=False) + "\n```"
    sl_say(run, chat, load, f"branch-{tag}", "[Branch-Save laden]")
    # kurzer HQ-Beat, damit ein realistischer Ergebnis-Save entsteht
    sl_say(run, chat, "Kurzer HQ-Aufenthalt: einmal kurz durchatmen, Stand sichten. "
                      "Dann bitte direkt !save für den aktuellen Stand dieser Gruppe.",
           f"branch-{tag}", "[HQ-Beat + !save]")
    # Save einsammeln (Save-Zwang gehaertet: eskaliert bei Prosa-statt-JSON)
    saves = request_save(run, chat, f"branch-{tag}", "[Branch-Ergebnis-Save]", want=1)
    if not saves:
        run.findings.append(MA.Finding("BRANCH-SAVE", "FAIL", f"Branch {tag}: kein Ergebnis-Save"))
        run.log(f"  ❌ Branch {tag}: kein Save erhalten")
        return None
    result = saves[0]
    validate_and_store(run, result, f"branch-{tag}-result", f"branch-{tag}")
    return result


def play_merge(run: Run, branches: list[dict], max_tpp: int) -> dict | None:
    chat = OWUIChat(BASE_URL, API_KEY, SL_MODEL, kb_id=KB_ID, timeout=TIMEOUT_SL)
    run.log(f"=== Phase 4 (Merge) — Chat {chat.chat_id} ===")
    run.rep("## 🗂 Chat — Merge (beide Branch-Saves zusammenführen)\n")
    # Multi-Save-Import: beide Saves in einer Nachricht stapeln (erster = Anker)
    blocks = "\n\n".join("```json\n" + json.dumps(s, ensure_ascii=False) + "\n```" for s in branches)
    merge_msg = ("Spiel laden (Gruppe wieder zusammen):\n\n" + blocks +
                 "\n\nDie Gruppe trifft sich wieder im HQ. Bitte führe die Stände "
                 "zusammen (Kontinuitätsrückblick) und erstelle danach einen "
                 "gemeinsamen Speicherstand (!save).")
    txt = sl_say(run, chat, merge_msg, "P4-merge", "[beide Branch-Saves laden + Merge]")
    beats = detect_beats(txt)
    if not beats["rejoin_beat"]:
        run.findings.append(MA.Finding("REJOIN-BEAT", "SOFT", "Kein Rejoin-HQ-Beat erkannt"))
        run.log("  ⚠️ [P4] kein Rejoin-Beat erkannt")
    if not beats["continuity_recap"]:
        run.findings.append(MA.Finding("MERGE-RECAP", "SOFT", "Kein Kontinuitätsrückblick beim Merge"))

    saves = extract_all_saves(txt)
    if not saves:
        # Save-Zwang gehaertet: eskaliert bei Prosa-statt-JSON statt sofort FAIL
        saves = request_save(run, chat, "P4-merge", "[Merge-Save]", want=1)
    if not saves:
        run.findings.append(MA.Finding("MERGE-SAVE", "FAIL", "Merge erzeugte keinen Save"))
        run.log("  ❌ [P4] kein Merge-Save erhalten")
        return None
    merge_save = saves[0]
    validate_and_store(run, merge_save, "merge-result", "P4")
    return merge_save


def finalize(run: Run, merge_save: dict | None, anchor: dict, branches: list[dict],
             conflict_expected: bool = False):
    run.rep("\n---\n\n## Auswertung\n")
    if merge_save:
        res = MA.assert_merge(merge_save, anchor, branches, label="merge")
        run.add_findings(res, "MERGE-ASSERT")
        # Konfliktfall: Merge MUSS den Duplikat-Konflikt erkannt haben
        if conflict_expected:
            flags = ((merge_save.get("logs") or {}).get("flags") or {})
            dup_char = flags.get("duplicate_character_detected")
            confs = flags.get("continuity_conflicts") or []
            if dup_char or confs:
                run.findings.append(MA.Finding("CONFLICT-OK", "INFO",
                    f"Konflikt erkannt (dup_char={dup_char}, conflicts={len(confs)})"))
                run.log(f"  ✅ [CONFLICT] Duplikat erkannt (dup_char={dup_char}, conflicts={len(confs)})")
            else:
                run.findings.append(MA.Finding("CONFLICT-MISS", "FAIL",
                    "Duplikat-Charakter-ID NICHT als Konflikt erkannt (still überschrieben?)"))
                run.log("  ❌ [CONFLICT] Duplikat NICHT erkannt")

    fails = [f for f in run.findings if f.severity == "FAIL"]
    softs = [f for f in run.findings if f.severity == "SOFT"]
    avg_cache = sum(run.cache_hits) / len(run.cache_hits) if run.cache_hits else 0
    verdict = "PASS" if not fails else "FAIL"

    summary = {
        "case": run.case, "verdict": verdict,
        "turns": run.turn, "cost_usd": round(run.cum_cost, 4),
        "peak_prompt_tokens": run.cum_prompt, "avg_cache_hit": round(avg_cache, 3),
        "fails": [str(f) for f in fails], "softs": [str(f) for f in softs],
        "merge_save_captured": merge_save is not None,
    }
    (run.out / "_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    run.rep(f"**Verdict: {verdict}**\n\n"
            f"- Turns: {run.turn}\n- Kosten (echt, OWUI usage.cost): ${run.cum_cost:.4f}\n"
            f"- Peak Prompt-Tokens: {run.cum_prompt} ({run.cum_prompt/256_000:.1%} von 256k Sonnet-4.6-Kontext)\n"
            f"- Ø Cache-Hit: {avg_cache:.0%}\n"
            f"- Harte Fehler: {len(fails)} | Soft: {len(softs)}\n\n"
            + ("**FAILS:**\n" + "\n".join(f"- {f}" for f in fails) if fails else "")
            + ("\n\n**SOFT:**\n" + "\n".join(f"- {f}" for f in softs) if softs else ""))
    run.log(f"=== ENDE === verdict={verdict} turns={run.turn} ${run.cum_cost:.4f} "
            f"peak={run.cum_prompt} cache={avg_cache:.0%} fails={len(fails)} softs={len(softs)}")
    print(f"\nVERDICT: {verdict}")
    print(f"SUMMARY: {run.out / '_summary.json'}")
    print(f"OUT_DIR: {run.out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", default="4-1", choices=list(CASES))
    ap.add_argument("--max-turns-per-phase", type=int, default=8)
    args = ap.parse_args()
    if not API_KEY:
        raise SystemExit("OPENWEBUI_API_KEY fehlt — erst: set -a; . ~/.openwebui_env; set +a")

    def _sigterm(*_a):
        print("[split-merge] SIGTERM — Abbruch", file=sys.stderr)
        sys.exit(143)
    signal.signal(signal.SIGTERM, _sigterm)

    pid = RUNNING_DIR / f"split-merge-{args.case}.pid"
    pid.write_text(str(os.getpid()))
    try:
        run = Run(args.case)
        run.log(f"=== START 5er-Split/Merge Case {args.case} ===")
        run_split_case(run, args.case, args.max_turns_per_phase)
    finally:
        try:
            pid.unlink()
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    main()
