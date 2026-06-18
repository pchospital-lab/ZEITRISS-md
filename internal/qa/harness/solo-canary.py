#!/usr/bin/env python3
"""
ZEITRISS Solo-Canary-Harness (2026-06-15)
=========================================
Vorsichtiger Durchstich: 1 SL + 1 Persona, FRISCHER Start (keine Fixture).

Warum dieser Pfad (v2, 2026-06-15):
  - Wir fahren EXAKT den Browser-Chat-Pfad (`/api/chat/completions` mit
    `parent_id`/`user_message` + `chat_id="local:..."`-Temporary-Chat).
  - OWUI macht damit sein EINGEBAUTES RAG selbst (KB-Retrieval-Inject,
    sichtbar als `sources` + [n]-Zitate) — KEIN manuelles Snippet-Injizieren.
  - Stock-OWUI, KEIN Source-Patch -> endnutzer-identisch + update-fest.
  - `local:`-Prefix => kein DB-Müll (Temporary-Chat-Modus des Browsers).
  - Hintergrund: der kopflose API-Pfad OHNE chat_id ist in 0.9.5 kaputt
    ('NoneType'.startswith). Der Browser-Pfad umgeht das sauber.
  - Client-Logik: harness/owui_client.py

Zwei-KI-Architektur:
  - SL     = OWUI-Preset zeitriss-v426-uncut (Sonnet, Masterprompt + KB-Inject)
  - Spieler= Persona-Profil (claude-sonnet-4.6 direkt), stateless, reine Eingabe

Aufruf:
  source ~/.openwebui_env
  python3 harness/solo-canary.py --persona noob --max-turns 18

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
from owui_client import OWUIChat, stateless_completion  # noqa: E402

# ─── Config ─────────────────────────────────────────────────────────────────
BASE_URL = os.environ.get("OPENWEBUI_URL", "http://127.0.0.1:8080")
API_KEY = os.environ.get("OPENWEBUI_API_KEY", "")

SL_MODEL = "zeitriss-v426-uncut"                 # OWUI-Preset (Masterprompt)
PLAYER_MODEL = "anthropic/claude-sonnet-4.6"     # Persona, direkt
KB_ID = "a56706c9-e427-4c6c-9dcb-0eb7cea095c0"   # live Preset-KB (verifiziert 2026-06-15)

COST_LIMIT_USD = 4.0                              # harter Watchdog-Stop (Solo ist billig)
# grobe Sonnet-4.6-Preise (USD/1M tok), nur fürs Watchdog-Schätzen:
PRICE_IN, PRICE_OUT = 3.0, 15.0

HOME = Path(os.path.expanduser("~"))
PLAYTESTS = HOME / ".openclaw" / "workspace-cloud" / "playtests" / "zeitriss"
RUNNING_DIR = HOME / ".openclaw" / "workspace-cloud" / "tmp" / "running"
RUNNING_DIR.mkdir(parents=True, exist_ok=True)

TIMEOUT_SL = 420       # SL-Turns können lang sein (großer MP)
TIMEOUT_PERSONA = 60

# ─── Personas ───────────────────────────────────────────────────────────────
# "Sarah/Noob" = der Frischstart-Härtetest: kein P&P-Wissen, will sofort spielen,
# Story > Mechanik, gibt bei Frust auf. Genau der erste-Kontakt-Stresstest.
PERSONAS: dict[str, dict] = {
    "noob": {
        "real_name": "Sarah",
        "system": (
            "Du bist Sarah, 34, Marketing-Angestellte. Du spielst ZEITRISS zum "
            "ALLERERSTEN Mal. Du hast NULL Pen-and-Paper-Erfahrung — kennst Sims "
            "und Handy-Games. Du hast auf Social Media von einem 'KI-Rollenspiel' "
            "gelesen und willst es einfach ausprobieren.\n\n"
            "SPIELVERHALTEN:\n"
            "- Du willst SOFORT spielen, kein Regelwerk lesen.\n"
            "- Regel-Erklärungen, Zahlen, englische Fachbegriffe nerven dich — du "
            "fragst dann nach ('Was heißt SYS? Ist das was Schlimmes?') oder "
            "überspringst sie.\n"
            "- Du entscheidest aus dem Bauch, ohne Taktik ('Ich hau einfach drauf').\n"
            "- Story und Atmosphäre fesseln dich, Mechanik langweilt.\n"
            "- Du tippst kurz, manchmal unvollständig, gelegentlich mit Tippfehlern.\n"
            "- Wenn die SL viel Text schreibt: 'puh okay, was soll ich jetzt machen?'\n"
            "- Du nimmst es locker, lachst wenn was schiefgeht.\n\n"
            "WICHTIG: Antworte NUR mit dem, was Sarah in den Chat tippt. Kein "
            "Meta-Kommentar, keine Anführungszeichen drumrum, keine Regie-Anweisung. "
            "1-3 Sätze."
        ),
    },
    "tactician": {
        "real_name": "Spieler A",
        "system": (
            "Du bist ein erfahrener P&P-Spieler (DSA, Shadowrun). Ergebnisorientiert, "
            "planst, willst Würfel sehen, knapp und sachlich. Du nutzt Regelbegriffe "
            "korrekt, übernimmst gern die Führung. Du gibst deinem Charakter eine "
            "Stimme. Antworte NUR mit dem, was du in den Chat tippst. 1-4 Sätze. "
            "Kein Meta-Kommentar."
        ),
    },
}

# Stop-Hints: Mission-Ende / Save-Angebot erreicht = Canary-Ziel erfüllt.
STOP_HINTS = [
    "PHASE Debrief", "PHASE debrief", "Mission abgeschlossen",
    "SC 4/12", "SC 5/12", "Episode endet", "Save empfohlen",
    "Charakter gespeichert", '"v": 7', '"v":7',
]


# ─── Persona-Turn (stateless, Browser-Pfad, kein RAG) ─────────────────────────
def persona_turn(persona: dict, sl_text: str, round_hint: str = "") -> str:
    ctx = (f"Die KI-Spielleitung schreibt gerade folgendes in den Chat:\n\n"
           f"---\n{sl_text[:4000]}\n---\n\n")
    if round_hint:
        ctx += f"Bisher kurz:\n{round_hint[:500]}\n\n"
    ctx += "Was tippst du jetzt in den Chat?"
    return stateless_completion(
        BASE_URL, API_KEY, PLAYER_MODEL,
        system=persona["system"], user=ctx,
        temperature=0.92, max_tokens=300, timeout=TIMEOUT_PERSONA)


# ─── PID-Guard ──────────────────────────────────────────────────────────────
class PIDFile:
    def __init__(self, name: str):
        self.path = RUNNING_DIR / f"{name}.pid"

    def __enter__(self):
        self.path.write_text(str(os.getpid()))
        return self

    def __exit__(self, *a):
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass


# ─── Quick-Checks (automatisch, ohne Wertung) ─────────────────────────────────
def quick_checks(sl_text: str) -> list[str]:
    f = []
    if '"v":' in sl_text and '"v": 7' not in sl_text and '"v":7' not in sl_text:
        f.append("SAVE-SCHEMA: Save-JSON ohne v:7")
    if re.search(r'\bHP\b', sl_text) and 'LP' not in sl_text:
        f.append("TERMINOLOGIE: 'HP' statt 'LP'")
    m = re.search(r'W10.{0,40}?Attribut\s+(\d+)', sl_text, re.IGNORECASE)
    if m and int(m.group(1)) < 11:
        f.append(f"W10-SCHWELLE: mögliche W10-Halluzination bei Attribut {m.group(1)}")
    if re.search(r'\bMid-?Scene-?(Save|Snapshot)\b', sl_text, re.IGNORECASE):
        f.append("SAVEGUARD: Mid-Scene-Save erwähnt")
    return f


# ─── Runner ─────────────────────────────────────────────────────────────────
def run(persona_key: str, max_turns: int, opening: str):
    persona = PERSONAS[persona_key]
    stamp = time.strftime("%Y-%m-%d-%H%M")
    out = PLAYTESTS / "runs" / f"{stamp}-solo-canary-{persona_key}"
    out.mkdir(parents=True, exist_ok=True)

    log_path = out / "_live.log"
    report = out / "_transkript.md"
    turns_jsonl = out / "turns.jsonl"
    tokens_csv = out / "_tokens.csv"
    tokens_csv.write_text("turn,prompt_tokens,completion_tokens,cum_cost_usd,latency_s,sl_chars\n")

    def log(msg: str):
        line = f"[{time.strftime('%H:%M:%S')}] {msg}"
        print(line, flush=True)
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    def rep(text: str):
        with report.open("a", encoding="utf-8") as fh:
            fh.write(text + "\n\n")

    def jlog(obj: dict):
        with turns_jsonl.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(obj, ensure_ascii=False) + "\n")

    sl = OWUIChat(BASE_URL, API_KEY, SL_MODEL, kb_id=KB_ID, timeout=TIMEOUT_SL)

    rep(f"# ZEITRISS Solo-Canary — Persona: {persona['real_name']} ({persona_key})\n\n"
        f"**Datum:** {time.strftime('%Y-%m-%d %H:%M')}  \n"
        f"**SL:** {SL_MODEL} (OWUI-eigenes RAG, KB {KB_ID[:8]}, Browser-Pfad)  \n"
        f"**Spieler:** {PLAYER_MODEL}  \n"
        f"**Start:** frisch (kein Save-Import)  \n"
        f"**Max-Turns:** {max_turns}\n\n---\n")

    log(f"=== START Solo-Canary persona={persona_key} max_turns={max_turns} ===")
    log(f"SL temp-chat_id={sl.chat_id}")

    cum_cost = 0.0
    findings: list[str] = []
    round_hint = ""
    next_input = opening

    # Turn 0: Persona-Opener
    log(f">>> {persona['real_name']} (Opener): {opening}")
    rep(f"## Turn 0 — Start\n\n**{persona['real_name']}:** {opening}")

    for turn in range(1, max_turns + 1):
        # --- SL ---
        try:
            res = sl.say(next_input)
        except Exception as e:  # noqa: BLE001
            log(f"[turn {turn}] SL FAIL: {e}")
            jlog({"turn": turn, "role": "sl", "error": str(e)})
            break
        sl_text = res["content"]
        ptok = res["usage"].get("prompt_tokens", 0)
        ctok = res["usage"].get("completion_tokens", 0)
        lat = res["latency_s"]
        src = sl.source_files()
        cum_cost += ptok / 1e6 * PRICE_IN + ctok / 1e6 * PRICE_OUT
        log(f"[turn {turn}] SL ({len(sl_text)} chars, {ptok}+{ctok} tok, {lat:.1f}s, "
            f"RAG={len(src)} files, ~${cum_cost:.2f})")
        rep(f"## Turn {turn} — SL\n\n{sl_text}")
        if src:
            rep(f"> _RAG-Quellen: {', '.join(src)}_")
        jlog({"turn": turn, "role": "sl", "content": sl_text,
              "prompt_tokens": ptok, "completion_tokens": ctok, "latency_s": lat,
              "rag_sources": src})
        with tokens_csv.open("a") as fh:
            fh.write(f"{turn},{ptok},{ctok},{cum_cost:.4f},{lat:.1f},{len(sl_text)}\n")

        for fnd in quick_checks(sl_text):
            findings.append(f"T{turn}: {fnd}")
            log(f"  ⚠️ FINDING [{fnd}]")
            rep(f"> **⚠️ Finding:** {fnd}")

        # Stop-Bedingungen
        if cum_cost >= COST_LIMIT_USD:
            log(f"🛑 Cost-Watchdog: ${cum_cost:.2f} >= ${COST_LIMIT_USD}")
            rep(f"> 🛑 **Cost-Watchdog gestoppt** bei ~${cum_cost:.2f}")
            break
        hit = next((h for h in STOP_HINTS if h in sl_text), None)
        if hit:
            log(f"🏁 Stop-Hint '{hit}' erkannt — Canary-Ziel erreicht")
            rep(f"> 🏁 **Stop-Hint:** '{hit}'")
            break

        # --- Persona ---
        try:
            p_text = persona_turn(persona, sl_text, round_hint)
        except Exception as e:  # noqa: BLE001
            log(f"[turn {turn}] Persona FAIL: {e}")
            jlog({"turn": turn, "role": "persona", "error": str(e)})
            break
        next_input = p_text
        round_hint = p_text
        log(f">>> {persona['real_name']}: {p_text[:100]}")
        rep(f"**{persona['real_name']}:** {p_text}")
        jlog({"turn": turn, "role": "persona", "content": p_text})

    # Abschluss
    summary = {
        "persona": persona_key, "turns_done": turn,
        "cum_cost_usd": round(cum_cost, 3), "findings": findings,
        "out_dir": str(out),
    }
    (out / "_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    rep(f"\n---\n\n## Zusammenfassung\n\n"
        f"- Turns: {turn}\n- Geschätzte Kosten: ~${cum_cost:.2f}\n"
        f"- Auto-Findings: {len(findings)}\n"
        + ("\n".join(f"  - {x}" for x in findings) if findings else "  (keine)"))
    log(f"=== ENDE === Turns={turn} ~${cum_cost:.2f} Findings={len(findings)}")
    log(f"Artefakte: {out}")
    print(f"\nSUMMARY_JSON: {out / '_summary.json'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--persona", default="noob", choices=list(PERSONAS))
    ap.add_argument("--max-turns", type=int, default=18)
    ap.add_argument("--opening", default="Spiel starten (solo klassisch)")
    args = ap.parse_args()

    if not API_KEY:
        raise SystemExit("OPENWEBUI_API_KEY fehlt — erst: source ~/.openwebui_env")

    def _sigterm(*_a):
        print("[solo-canary] SIGTERM — sauberer Abbruch", file=sys.stderr)
        sys.exit(143)
    signal.signal(signal.SIGTERM, _sigterm)

    with PIDFile(f"solo-canary-{args.persona}"):
        run(args.persona, args.max_turns, args.opening)


if __name__ == "__main__":
    main()
