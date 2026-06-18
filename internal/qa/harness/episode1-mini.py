#!/usr/bin/env python3
"""Mini-Episoden-Playtest v3: Sarah (Noob) spielt Solo pur Lvl 1.
v3 fixes gegenüber v2:
- Mission-Chat startet mit explizitem Briefing-Befehl (nicht mit 'Mission starten' als Sarah-Dialog)
- Mission-Turn-Budget auf 32 (reicht für 12 Szenen + Briefing + Debrief)
- Score-Screen als Mission-Ende-Primärsignal
- Sarah-Persona adaptiert: in Mission-Chats entschlossener als in HQ-RP
"""
import json, os, time, re, requests
from pathlib import Path

API_KEY = os.environ["OPENWEBUI_API_KEY"]
BASE = os.environ.get("OPENWEBUI_URL", "http://127.0.0.1:8080").rstrip("/") + "/api/chat/completions"
MODEL = "anthropic/claude-sonnet-4.6"

# --- Pfade (2026-04-27 Cleanup: env-überschreibbar, Default = neue Workspace-Struktur) ---
_PLAYTESTS_ROOT = Path(os.environ.get(
    "ZEITRISS_PLAYTEST_OUT_ROOT",
    str(Path.home() / ".openclaw" / "workspace-cloud" / "playtests" / "zeitriss"),
))
SL_SYSTEM = (_PLAYTESTS_ROOT / "harness" / "zeitriss-sysprompt.txt").read_text()
_STAMP = time.strftime("%Y-%m-%d-%H%M")
OUT_DIR = _PLAYTESTS_ROOT / "runs" / f"{_STAMP}-episode1-mini-solo-sarah"
OUT_DIR.mkdir(exist_ok=True, parents=True)
REPORT = OUT_DIR / "_bericht.md"
LOG = OUT_DIR / "_live.log"

SARAH_PERSONA_HQ = """Du bist Sarah, 34, Marketing. Erste Begegnung mit Pen&Paper. Du spielst ZEITRISS im Chat.

STIL im HQ:
- Antworte KURZ (1-3 Saetze, max 4 Zeilen)
- Neugierig, social, du sprichst gerne mit NSCs
- Kein Gamer-Jargon, kein P&P-Vokabular
- Story interessiert dich mehr als Mechanik
- Wenn cool: "oh cool" / "krass"
- NIEMALS meta-kommentieren
- NIEMALS Regel-Namen die du nicht vorher gehoert hast

Antworte NUR mit Sarahs direkter Eingabe - keine Anfuehrungszeichen."""

SARAH_PERSONA_MISSION = """Du bist Sarah, 34, Marketing. Du spielst ZEITRISS im Chat.
Du bist jetzt in einer echten Mission, keine HQ-Plauderei mehr.

STIL in Mission:
- Antworte KURZ (1-3 Saetze)
- Handlungsorientiert: wahle Optionen, nicht endlose Nachfragen
- Wenn Optionen angeboten: nimm eine klare (z.B. "Ich nehm 2" oder "Ich schleich mich")
- Bei Kampf: "Ich hau drauf" / "Ich schiess"
- Bei Verwirrung: rate einfach ("okay ich versuchs"), frag nur wenn wirklich noetig
- Vorwaertsdruck: nach Briefing-Bestaetigung -> "Los, sprung ausfuehren" etc.
- Wenn SL fragt ob du weitermachst: ja, weitermachen
- NIEMALS meta-kommentieren

Antworte NUR mit Sarahs direkter Eingabe."""

def log(msg):
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] {msg}\n"
    print(line, end="", flush=True)
    with LOG.open("a") as f:
        f.write(line)

def call_api(system, messages, max_tokens=3000, temp=0.8):
    # OWUI 0.9.5 Workaround: chat_id Pflicht, sonst 400 (NoneType.startswith).
    # local: prefix verhindert DB-Persistenz (rein synthetischer Smoke-Chat).
    r = requests.post(BASE,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"model": MODEL,
              "messages": [{"role": "system", "content": system}] + messages,
              "temperature": temp, "top_p": 0.9, "frequency_penalty": 0.3,
              "max_tokens": max_tokens,
              "chat_id": f"local:harness-{_STAMP}"},
        timeout=180)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

def sarah_reply(last_sl_text, persona):
    msg = f"Die KI-Spielleitung schreibt dir:\n\n---\n{last_sl_text[:3500]}\n---\n\nWas tippst du jetzt in den Chat? Kurz, als Sarah."
    return call_api(persona, [{"role": "user", "content": msg}], max_tokens=200, temp=0.9).strip()

def extract_save(text):
    blocks = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    for block in reversed(blocks):
        try:
            parsed = json.loads(block)
            if isinstance(parsed, dict) and ("v" in parsed or "save_id" in parsed or "characters" in parsed):
                return block
        except Exception:
            continue
    return None

def run_chat(chat_label, opener_msg, prev_save_json, max_turns, persona, exit_trigger, inject_midpoint=None):
    """
    inject_midpoint: (turn_number, message) - bei diesem Turn NICHT Sarah-Sim sondern Hardcoded-Message senden.
        Nuetzlich um z.B. nach ein paar HQ-Turns "Ich bin bereit fuer das Briefing" zu forcieren.
    """
    log(f"=== {chat_label} ===")
    history = []

    if prev_save_json:
        first_user = f"Spiel laden\n```json\n{prev_save_json}\n```"
    else:
        first_user = opener_msg
    history.append({"role": "user", "content": first_user})
    log(f"  USER[0]: {first_user[:90]}")

    turn = 0
    last_save = None
    ended_clean = False
    last_sarah = ""

    while turn < max_turns:
        turn += 1
        try:
            sl_response = call_api(SL_SYSTEM, history, max_tokens=3500)
        except Exception as e:
            log(f"  ERROR SL: {e}")
            break
        history.append({"role": "assistant", "content": sl_response})
        preview = sl_response[:110].replace("\n", " ")
        log(f"  SL[{turn}]: {len(sl_response)} chars - {preview}...")

        maybe_save = extract_save(sl_response)
        if maybe_save:
            last_save = maybe_save
            log(f"  SAVE extrahiert ({len(maybe_save)} chars)")
            if last_sarah.lower().strip().startswith("!save"):
                log(f"  -> Chat sauber beendet nach !save")
                ended_clean = True
                break

        # Forced-Inject an midpoint
        if inject_midpoint and turn == inject_midpoint[0]:
            sarah_msg = inject_midpoint[1]
            log(f"  INJECT[{turn}]: {sarah_msg}")
        elif exit_trigger(turn, sl_response, last_sarah):
            sarah_msg = "!save"
            log(f"  TRIGGER Chat-Ende bei Turn {turn}")
        else:
            try:
                sarah_msg = sarah_reply(sl_response, persona)
            except Exception as e:
                log(f"  ERROR Sarah: {e}")
                sarah_msg = "weiter"
            sarah_msg = sarah_msg.strip().strip('"').strip("'")[:400]

        history.append({"role": "user", "content": sarah_msg})
        last_sarah = sarah_msg
        log(f"  SARAH[{turn}]: {sarah_msg}")
        time.sleep(0.5)

    chat_file = OUT_DIR / f"{chat_label}.md"
    with chat_file.open("w") as f:
        f.write(f"# {chat_label}\n\n**Turns:** {turn}  |  **Sauber beendet:** {ended_clean}  |  **Save:** {bool(last_save)}\n\n---\n\n")
        for i, m in enumerate(history):
            role = m["role"].upper()
            content = m["content"]
            if len(content) > 6000:
                content = content[:6000] + "\n[...gekuerzt...]"
            f.write(f"## [{i}] {role}\n\n{content}\n\n---\n\n")
    log(f"  Chat gespeichert: {chat_file}")
    return last_save, turn, ended_clean

# ===== Trigger-Funktionen =====

def trigger_chargen(turn, sl_text, last_sarah):
    low = sl_text.lower()
    save_ready = "deepsave wird generiert" in low or "deepsave moeglich" in low or "deepsave möglich" in low
    has_v7 = '"v": 7' in sl_text or '"v":7' in sl_text
    if (save_ready or has_v7) and turn >= 2:
        return True
    if turn >= 12:
        return True
    return False

def trigger_hq(turn, sl_text, last_sarah):
    low = sl_text.lower()
    # Nach 4 HQ-Turns direkt saven - das ist bewusstes HQ-Break
    if turn >= 4:
        return True
    return False

def trigger_mission(turn, sl_text, last_sarah):
    low = sl_text.lower()
    # Score-Screen + Debrief Signale
    score_signals = ["score-screen", "score screen", "missions-abschlussbildschirm",
                     "bewertung:", "loot-recap", "cu-auszahlung", "xp/level-up"]
    debrief_signals = ["debrief", "mission abgeschlossen", "rueckkehr ins hq", "rückkehr ins hq",
                       "zurueck im hq", "zurück im hq", "missionsabschluss",
                       "mission erfolgreich", "mission gescheitert"]
    if turn >= 6 and (any(s in low for s in score_signals) or any(s in low for s in debrief_signals)):
        return True
    if turn >= 30:
        return True
    return False

# ===== HAUPTLAUF =====
LOG.write_text(f"# Mini-Playtest v3\nStart: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
log("Mini-Playtest v3 gestartet")

results = []

# CHAT 1: Chargen
save, turns, ended = run_chat(
    "chat1-chargen",
    "Spiel starten (solo klassisch)\ngenerate",
    prev_save_json=None,
    max_turns=12,
    persona=SARAH_PERSONA_HQ,
    exit_trigger=trigger_chargen
)
results.append(("Chat 1: Chargen", turns, ended, bool(save)))
if save: (OUT_DIR / "save-after-chargen.json").write_text(save)

# CHAT 2: HQ-Erkundung
if save:
    save2, turns, ended = run_chat(
        "chat2-hq-erkundung",
        "Spiel laden",
        prev_save_json=save,
        max_turns=6,
        persona=SARAH_PERSONA_HQ,
        exit_trigger=trigger_hq
    )
    results.append(("Chat 2: HQ-Erkundung", turns, ended, bool(save2)))
    if save2:
        (OUT_DIR / "save-after-hq.json").write_text(save2)
        save = save2

# CHAT 3: Mission 1 — aktiv gestartet
if save:
    save3, turns, ended = run_chat(
        "chat3-mission1",
        "Spiel laden",
        prev_save_json=save,
        max_turns=32,
        persona=SARAH_PERSONA_MISSION,
        exit_trigger=trigger_mission,
        inject_midpoint=(1, "Briefing - ich bin bereit fuer die erste Mission")
    )
    results.append(("Chat 3: Mission 1", turns, ended, bool(save3)))
    if save3:
        (OUT_DIR / "save-after-mission1.json").write_text(save3)
        save = save3

# CHAT 4: Mission 2
if save:
    save4, turns, ended = run_chat(
        "chat4-mission2",
        "Spiel laden",
        prev_save_json=save,
        max_turns=32,
        persona=SARAH_PERSONA_MISSION,
        exit_trigger=trigger_mission,
        inject_midpoint=(1, "Briefing - naechste Mission bitte")
    )
    results.append(("Chat 4: Mission 2", turns, ended, bool(save4)))
    if save4:
        (OUT_DIR / "save-after-mission2.json").write_text(save4)
        save = save4

# CHAT 5: Mission 3
if save:
    save5, turns, ended = run_chat(
        "chat5-mission3",
        "Spiel laden",
        prev_save_json=save,
        max_turns=32,
        persona=SARAH_PERSONA_MISSION,
        exit_trigger=trigger_mission,
        inject_midpoint=(1, "Briefing - naechste Mission bitte")
    )
    results.append(("Chat 5: Mission 3", turns, ended, bool(save5)))
    if save5:
        (OUT_DIR / "save-after-mission3.json").write_text(save5)

log("=== BERICHT ===")
total_turns = sum(r[1] for r in results)
successful = sum(1 for r in results if r[2])

with REPORT.open("w") as f:
    f.write(f"""# Mini-Playtest v3: Episode 1 Solo Lvl 1 (Sarah)

**Datum:** {time.strftime('%Y-%m-%d %H:%M')}
**Modell:** {MODEL} + ZEITRISS v4.2.6 Uncut (gepatcht: Chargen-Save-Gate)

## Verbesserungen v3

- Chat 2 HQ-Erkundung: strikt 4 Turns, dann Save
- Mission-Chats: injizieren Turn 1 Briefing-Request (kein passiver Sarah-Dialog)
- Mission-Persona: handlungsorientiert, nicht HQ-RP-neugierig
- Score-Screen als Mission-Ende-Primaersignal
- Turn-Budget Mission: 32 (12 Szenen + Briefing + Debrief + Puffer)

## Kette

| Chat | Turns | Sauber beendet | Save |
|------|-------|-----|-----|
""")
    for name, turns, ended, has_save in results:
        f.write(f"| {name} | {turns} | {'JA' if ended else 'NEIN'} | {'JA' if has_save else 'NEIN'} |\n")
    f.write(f"\n**Gesamt-Turns:** {total_turns}  |  **Erfolgreich:** {successful}/{len(results)}\n\n")
    f.write("## Save-Groessen\n\n")
    for sfn in ["save-after-chargen.json", "save-after-hq.json", "save-after-mission1.json", "save-after-mission2.json", "save-after-mission3.json"]:
        p = OUT_DIR / sfn
        if p.exists():
            f.write(f"- `{sfn}`: {p.stat().st_size} bytes\n")

log(f"DONE: {REPORT}")
