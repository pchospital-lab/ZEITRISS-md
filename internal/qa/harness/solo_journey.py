#!/usr/bin/env python3
"""
ZEITRISS Solo-Journey-Harness (2026-06-15)
==========================================
Die "echte Reise": EIN Spieler (Persona) spielt ZEITRISS so, wie ein Mensch es
tut — über MEHRERE Chats hinweg, mit Save-Handover dazwischen. Das ist näher am
Nutzer als der Single-Chat-Canary, weil der echte Flow chat-getrennt ist:
  Chargen -> !save -> NEUER CHAT (Save pasten) -> HQ/Mission -> !save -> NEUER CHAT ...

Das ist gleichzeitig das Fundament für den späteren 5er-Split/Merge:
ein sauberer Save-Capture + Chat-Handover-Mechanismus.

ARCHITEKTUR (Browser-Pfad, endnutzer-identisch):
  - SL     = OWUI-Preset zeitriss-v426-uncut (Sonnet), pro Spielabschnitt EIN
             frischer OWUIChat (local:-Temp-Chat, OWUI-eigenes RAG).
  - Spieler= Persona (claude-sonnet-4.6), stateless, sieht VOLLEN SL-Text +
             rollierende Verlaufs-Summary (G2-Fix).

CRITIC-FIXES eingebaut:
  - G4: Save-Detection via JSON-Parse (v:7 + last_seen.mode), NICHT Prosa-Grep.
        Ein Save löst Chat-Handover aus statt Skript-Abbruch.
  - G2: Persona sieht vollen SL-Text (kein [:4000]) + Roll-Summary letzter N Turns.
  - B1: HARTE Turn-Obergrenze als echter Stopp (Kosten nur Anzeige, da OWUIs
        interne Task-Calls nicht in usage auftauchen -> Geld-Limit unzuverlässig).

Aufruf:
  set -a; . ~/.openwebui_env; set +a
  python3 harness/solo_journey.py --persona noob --max-turns 60 --max-chats 6

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
SL_MODEL = "zeitriss-v426-uncut"
PLAYER_MODEL = "anthropic/claude-sonnet-4.6"
KB_ID = "a56706c9-e427-4c6c-9dcb-0eb7cea095c0"

PRICE_IN, PRICE_OUT = 3.0, 15.0     # Sonnet-4.6 USD/1M, nur Anzeige
SL_TEXT_CAP = 16000                 # G2: großzügig (Briefings/Saves sprengen 4k)
ROLL_SUMMARY_TURNS = 6              # G2: rollierender Verlauf statt nur letztem Turn

HOME = Path(os.path.expanduser("~"))
PLAYTESTS = HOME / ".openclaw" / "workspace-cloud" / "playtests" / "zeitriss"
RUNNING_DIR = HOME / ".openclaw" / "workspace-cloud" / "tmp" / "running"
RUNNING_DIR.mkdir(parents=True, exist_ok=True)
TIMEOUT_SL = 420
TIMEOUT_PERSONA = 60

# ─── Personas ───────────────────────────────────────────────────────────────
PERSONAS: dict[str, dict] = {
    "noob": {
        "real_name": "Sarah",
        "system": (
            "Du bist Sarah, 34, Marketing-Angestellte. Du spielst ZEITRISS zum "
            "ALLERERSTEN Mal. NULL Pen-and-Paper-Erfahrung — kennst Sims und "
            "Handy-Games. Du willst es einfach ausprobieren.\n\n"
            "SPIELVERHALTEN:\n"
            "- Du willst SOFORT spielen, kein Regelwerk lesen.\n"
            "- Regel-Erklärungen/Zahlen/engl. Fachbegriffe nerven — du fragst nach "
            "('Was heißt SYS?') oder überspringst.\n"
            "- Bauchentscheidungen, keine Taktik ('Ich hau einfach drauf').\n"
            "- Story/Atmosphäre fesseln dich, Mechanik langweilt.\n"
            "- Kurze Eingaben, manchmal Tippfehler.\n"
            "- Bei viel SL-Text: 'puh okay, was soll ich jetzt machen?'\n"
            "- Wenn die SL dich zum Speichern/Chat-Wechsel auffordert: du machst "
            "das mit, auch wenn du's umständlich findest.\n\n"
            "WICHTIG: Antworte NUR mit dem, was Sarah tippt. Kein Meta-Kommentar, "
            "keine Anführungszeichen, keine Regie. 1-3 Sätze."
        ),
    },
    "tactician": {
        "real_name": "Spieler A",
        "system": (
            "Du bist erfahrener P&P-Spieler (DSA, Shadowrun). Ergebnisorientiert, "
            "planst, willst Würfel sehen, knapp/sachlich. Nutzt Regelbegriffe "
            "korrekt. Gibst dem Charakter eine Stimme. Folgst Save-/Chat-Wechsel-"
            "Aufforderungen der SL prompt. Antworte NUR mit Chat-Eingabe. 1-4 Sätze."
        ),
    },
    "eager": {
        "real_name": "Jonas",
        "system": (
            "Du bist Jonas, 28, hast schon ein paar RPGs gespielt (Witcher, "
            "Cyberpunk 2077) und KENNST das Grundprinzip. Du WILLST SOFORT IN DIE "
            "ACTION — Charaktererstellung und Vorgeplänkel langweilen dich.\n\n"
            "SPIELVERHALTEN:\n"
            "- Chargen winkst du zügig durch: nimmst Vorschläge/Defaults an, statt "
            "lange zu optimieren ('passt, weiter', 'mach du, Hauptsache los').\n"
            "- Du drängst aktiv auf den Einsatz: 'wann geht's endlich los?', 'können "
            "wir die Mission starten?', 'ich will raus ins Feld'.\n"
            "- In HQ/Briefing hältst du dich kurz — du willst nicht lang quatschen, "
            "sondern handeln. Lange Briefings überfliegst du ('ja gut, und jetzt?').\n"
            "- Im Feld bist du neugierig und gehst voran, probierst Dinge aus.\n"
            "- Du folgst Save-/Chat-Wechsel-Aufforderungen der SL prompt, ohne zu "
            "murren.\n"
            "- Du gibst dem Charakter eine Stimme, bleibst aber knapp.\n\n"
            "WICHTIG: Antworte NUR mit dem, was Jonas in den Chat tippt. Kein "
            "Meta-Kommentar, keine Regie, keine Anführungszeichen. 1-3 Sätze."
        ),
    },
}

OPENING = "Spiel starten (solo klassisch)"


# ─── Save-Detection (G4-Fix) ──────────────────────────────────────────────────
def extract_save(sl_text: str) -> dict | None:
    """Findet einen v7-Save-JSON-Block im SL-Output. Gibt das geparste dict
    zurück oder None. Robust: sucht ```json-Fence ODER nacktes {...} mit '"v"'.
    """
    # 1) ```json ... ``` Fence
    for m in re.finditer(r"```(?:json)?\s*(\{.*?\})\s*```", sl_text, re.DOTALL):
        obj = _try_save(m.group(1))
        if obj:
            return obj
    # 2) nacktes Top-Level-JSON mit "v": 7 (greedy bis letzte })
    if '"v"' in sl_text:
        start = sl_text.find("{")
        end = sl_text.rfind("}")
        if 0 <= start < end:
            obj = _try_save(sl_text[start:end + 1])
            if obj:
                return obj
    return None


def _try_save(blob: str) -> dict | None:
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


# ─── Persona-Turn (G2: voller SL-Text + Roll-Summary) ─────────────────────────
def persona_turn(persona: dict, sl_text: str, roll_summary: str) -> str:
    ctx = ("Die KI-Spielleitung schreibt gerade folgendes in den Chat:\n\n"
           f"---\n{sl_text[:SL_TEXT_CAP]}\n---\n\n")
    if roll_summary:
        ctx += f"Was bisher in dieser Session geschah (Kurzverlauf):\n{roll_summary}\n\n"
    ctx += "Was tippst du jetzt in den Chat?"
    return stateless_completion(
        BASE_URL, API_KEY, PLAYER_MODEL,
        system=persona["system"], user=ctx,
        temperature=0.9, max_tokens=320, timeout=TIMEOUT_PERSONA)


# ─── Quick-Checks ─────────────────────────────────────────────────────────────
def quick_checks(sl_text: str, save: dict | None) -> list[str]:
    f = []
    if re.search(r'\bHP\b', sl_text) and not re.search(r'\bLP\b', sl_text):
        f.append("TERMINOLOGIE: 'HP' ohne 'LP'")
    m = re.search(r'W10.{0,40}?Attribut\s+(\d+)', sl_text, re.IGNORECASE)
    if m and int(m.group(1)) < 11:
        f.append(f"W10-SCHWELLE: W10 bei Attribut {m.group(1)} (<11)")
    if re.search(r'Mid-?Scene-?(Save|Snapshot)', sl_text, re.IGNORECASE):
        f.append("SAVEGUARD: Mid-Scene-Save erwähnt")
    # Save-Zwang-Diagnose: SL behauptet einen Save in Prosa, liefert aber kein JSON.
    # Genau der Methodenfehler aus der Split/Merge-Session (Prosa statt JSON).
    if save is None and re.search(
            r'(gespeichert|speicherstand|abgespeichert|stand gesichert|save erstellt|saved)',
            sl_text, re.IGNORECASE):
        f.append("SAVE-PROSE: SL behauptet Save in Prosa, aber kein v7-JSON-Block im Output")
    if save is not None:
        mode = save_mode(save)
        # Chargen-Erst-Save MUSS hq sein, nicht char-gen
        if mode in ("char-gen", "chargen", "character_creation"):
            f.append(f"SAVE-GATE: Erst-Save mode='{mode}' (muss 'hq' sein)")
        # Attribut-Summe-Sanity (Fresh-Char = 18)
        try:
            for c in save["characters"]:
                s = sum(c["attr"].values())
                if c.get("lvl", 1) == 1 and s != 18:
                    f.append(f"CHARGEN: {c.get('name','?')} attr-Summe {s}≠18 bei lvl1")
        except (KeyError, TypeError):
            pass
    return f


# ─── PID-Guard ────────────────────────────────────────────────────────────────
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


def new_sl_chat() -> OWUIChat:
    return OWUIChat(BASE_URL, API_KEY, SL_MODEL, kb_id=KB_ID, timeout=TIMEOUT_SL)


# ─── Runner ─────────────────────────────────────────────────────────────────
def run(persona_key: str, max_turns: int, max_chats: int):
    persona = PERSONAS[persona_key]
    stamp = time.strftime("%Y-%m-%d-%H%M")
    out = PLAYTESTS / "runs" / f"{stamp}-solo-journey-{persona_key}"
    out.mkdir(parents=True, exist_ok=True)
    log_path = out / "_live.log"
    report = out / "_transkript.md"
    turns_jsonl = out / "turns.jsonl"
    saves_dir = out / "saves"
    saves_dir.mkdir(exist_ok=True)

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

    rep(f"# ZEITRISS Solo-Journey — {persona['real_name']} ({persona_key})\n\n"
        f"**Datum:** {time.strftime('%Y-%m-%d %H:%M')}  \n"
        f"**SL:** {SL_MODEL} (OWUI-RAG, Browser-Pfad, Multi-Chat-Handover)  \n"
        f"**Spieler:** {PLAYER_MODEL}  \n"
        f"**Limits:** max_turns={max_turns}, max_chats={max_chats}\n\n---\n")
    log(f"=== START Solo-Journey persona={persona_key} max_turns={max_turns} max_chats={max_chats} ===")

    sl = new_sl_chat()
    chat_idx = 1
    log(f"Chat #{chat_idx} (Chargen/Start) — {sl.chat_id}")
    rep(f"## 🗂 Chat #{chat_idx} — Start\n")

    cum_cost = 0.0
    findings: list[str] = []
    history_lines: list[str] = []   # roll-summary Quelle
    next_input = OPENING
    last_save: dict | None = None
    total_turn = 0

    def roll_summary() -> str:
        return "\n".join(history_lines[-ROLL_SUMMARY_TURNS * 2:])

    log(f">>> {persona['real_name']} (Opener): {next_input}")
    rep(f"**{persona['real_name']}:** {next_input}")
    history_lines.append(f"{persona['real_name']}: {next_input}")

    while total_turn < max_turns and chat_idx <= max_chats:
        total_turn += 1
        # --- SL ---
        try:
            res = sl.say(next_input)
        except Exception as e:  # noqa: BLE001
            log(f"[turn {total_turn}] SL FAIL: {e}")
            jlog({"turn": total_turn, "chat": chat_idx, "role": "sl", "error": str(e)})
            break
        sl_text = res["content"]
        ptok = res["usage"].get("prompt_tokens", 0)
        ctok = res["usage"].get("completion_tokens", 0)
        cum_cost += ptok / 1e6 * PRICE_IN + ctok / 1e6 * PRICE_OUT
        src = sl.source_files()
        log(f"[turn {total_turn} / chat {chat_idx}] SL ({len(sl_text)} chars, "
            f"{ptok}+{ctok} tok, RAG={len(src)}, ~${cum_cost:.2f})")
        rep(f"### Turn {total_turn} — SL\n\n{sl_text}")
        if src:
            rep(f"> _RAG: {', '.join(src)}_")
        history_lines.append(f"SL: {sl_text[:300]}")

        # --- Save-Detection (G4) ---
        save = extract_save(sl_text)
        fnds = quick_checks(sl_text, save)
        for fd in fnds:
            findings.append(f"T{total_turn}: {fd}")
            log(f"  ⚠️ {fd}")
            rep(f"> **⚠️ Finding:** {fd}")

        jlog({"turn": total_turn, "chat": chat_idx, "role": "sl", "content": sl_text,
              "prompt_tokens": ptok, "completion_tokens": ctok,
              "rag_sources": src, "save_detected": bool(save),
              "save_mode": save_mode(save) if save else None})

        if save:
            last_save = save
            sp = saves_dir / f"chat{chat_idx:02d}-turn{total_turn:02d}-{save_mode(save)}.json"
            sp.write_text(json.dumps(save, ensure_ascii=False, indent=2))
            mode = save_mode(save)
            log(f"  💾 SAVE erkannt (mode={mode}) -> {sp.name}")
            rep(f"> 💾 **Save erkannt** (mode=`{mode}`) — gespeichert als `{sp.name}`")

            # HANDOVER: nur wenn HQ-Save (echter Abschnittsübergang).
            # SaveGuard-Saves (Kurzstatus außerhalb HQ) lösen keinen Wechsel aus.
            if mode == "hq" and chat_idx < max_chats:
                chat_idx += 1
                sl = new_sl_chat()
                log(f"  🔄 CHAT-HANDOVER -> Chat #{chat_idx} ({sl.chat_id}), paste Save")
                rep(f"\n## 🗂 Chat #{chat_idx} — nach Handover (Save reingepastet)\n")
                # Spieler pastet Save als erste Nachricht in den neuen Chat
                next_input = ("Spiel laden:\n\n```json\n"
                              + json.dumps(save, ensure_ascii=False) + "\n```")
                history_lines.append(f"[Spieler öffnet neuen Chat #{chat_idx}, pastet Save]")
                continue
            # kein Handover -> Spiel läuft im selben Chat weiter

        # --- Persona ---
        try:
            p_text = persona_turn(persona, sl_text, roll_summary())
        except Exception as e:  # noqa: BLE001
            log(f"[turn {total_turn}] Persona FAIL: {e}")
            jlog({"turn": total_turn, "chat": chat_idx, "role": "persona", "error": str(e)})
            break
        next_input = p_text
        history_lines.append(f"{persona['real_name']}: {p_text}")
        log(f">>> {persona['real_name']}: {p_text[:90]}")
        rep(f"**{persona['real_name']}:** {p_text}")
        jlog({"turn": total_turn, "chat": chat_idx, "role": "persona", "content": p_text})

    stop = ("max_turns" if total_turn >= max_turns
            else "max_chats" if chat_idx > max_chats else "ended")
    summary = {
        "persona": persona_key, "turns": total_turn, "chats": chat_idx,
        "stop_reason": stop, "cum_cost_est_usd": round(cum_cost, 3),
        "findings": findings, "last_save_mode": save_mode(last_save) if last_save else None,
        "saves_captured": len(list(saves_dir.glob("*.json"))),
    }
    (out / "_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    rep(f"\n---\n\n## Zusammenfassung\n\n"
        f"- Turns: {total_turn} über {chat_idx} Chat(s)\n"
        f"- Stop: {stop}\n- Saves erfasst: {summary['saves_captured']}\n"
        f"- Geschätzte Kosten (ohne OWUI-interne Calls!): ~${cum_cost:.2f}\n"
        f"- Auto-Findings: {len(findings)}\n"
        + ("\n".join(f"  - {x}" for x in findings) if findings else "  (keine)"))
    log(f"=== ENDE === turns={total_turn} chats={chat_idx} stop={stop} "
        f"saves={summary['saves_captured']} findings={len(findings)} ~${cum_cost:.2f}")
    print(f"\nSUMMARY_JSON: {out / '_summary.json'}")
    print(f"OUT_DIR: {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--persona", default="noob", choices=list(PERSONAS))
    ap.add_argument("--max-turns", type=int, default=60)   # B1: harte Turn-Grenze
    ap.add_argument("--max-chats", type=int, default=6)
    args = ap.parse_args()

    if not API_KEY:
        raise SystemExit("OPENWEBUI_API_KEY fehlt — erst: set -a; . ~/.openwebui_env; set +a")

    def _sigterm(*_a):
        print("[solo-journey] SIGTERM — sauberer Abbruch", file=sys.stderr)
        sys.exit(143)
    signal.signal(signal.SIGTERM, _sigterm)

    with PIDFile(f"solo-journey-{args.persona}"):
        run(args.persona, args.max_turns, args.max_chats)


if __name__ == "__main__":
    main()
