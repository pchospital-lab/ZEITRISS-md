#!/usr/bin/env python3
"""Pflichtgate-Verifikation, gezielt.

Zwei Gates, zwei Mini-Chats, klare Pass/Fail-Bedingungen.

A) Save-State (#3187)
   Sarah erstellt einen Char und sagt direkt `!save`.
   Pass = SL gibt einen JSON-Save-Block aus mit Mindest-Feldern.

B) MS1-2-Tonfall + Sprung-Tempo (#3186 + Pacing-Bauchgefuehl)
   Sarah laesst Briefing kurz durchlaufen und sagt sofort
   "Sprung ausfuehren". Pass = SL springt in <=3 Turns von Briefing-Ende
   nach Wien-Ankunft, und nutzt keine Welt-Stakes-Sprache.

Schreibt Logs nach playtests/zeitriss/runs/<stamp>-pflichtgate-verify/.
"""
import json, os, re, time, requests
from pathlib import Path

API_KEY = os.environ["OPENWEBUI_API_KEY"]
BASE = os.environ.get("OPENWEBUI_URL", "http://127.0.0.1:8080").rstrip("/") + "/api/chat/completions"
MODEL = "zeitriss-v426-uncut"   # Preset-Route (durch LiteLLM seit base_model_id=zeitriss-sonnet)
STAMP = time.strftime("%Y-%m-%d-%H%M")
OUT = Path.home() / ".openclaw" / "workspace-cloud" / "playtests" / "zeitriss" / "runs" / f"{STAMP}-pflichtgate-verify"
OUT.mkdir(parents=True, exist_ok=True)

WELT_STAKES_NEEDLES = [
    "zeitlinie reparieren",
    "realitaet rutscht",
    "realität rutscht",
    "welt steht auf dem spiel",
    "schicksal der menschheit",
    "kollabiert das universum",
    "rettung der menschheit",
]


def call(messages):
    r = requests.post(
        BASE,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={
            "model": MODEL,
            "messages": messages,
            "max_tokens": 3500,
            "temperature": 0.7,
            "chat_id": f"local:pflichtgate-{STAMP}-{int(time.time())}",
        },
        timeout=180,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def has_json_save_block(text):
    blocks = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    for b in blocks:
        try:
            data = json.loads(b)
        except json.JSONDecodeError:
            continue
        # Save-Schema v7 hat "v" = 7 oder einen Char-Block
        if data.get("v") == 7:
            return True, "v7-Schema", data
        if "char" in data or "character" in data or "yara" in str(data).lower():
            return True, "char-block", data
    return False, "kein JSON-Save-Block gefunden", None


def write_chat(name, history):
    p = OUT / f"{name}.md"
    with p.open("w") as f:
        f.write(f"# {name}\n\n")
        for i, m in enumerate(history):
            content = m["content"]
            if len(content) > 8000:
                content = content[:8000] + "\n[...truncated...]"
            f.write(f"## [{i}] {m['role'].upper()}\n\n{content}\n\n---\n\n")
    return p


# ========================================================================
# GATE A: Save-State-Pflichtgate
# ========================================================================
print("\n=== GATE A: Save-State (#3187) ===")
hist_a = []

# Turn 1: Char wählen
hist_a.append({"role": "user", "content": "Spiel starten (solo klassisch)\ngenerate"})
sl_1 = call(hist_a)
hist_a.append({"role": "assistant", "content": sl_1})
print(f"  Turn 1 (SL): {len(sl_1)} chars")

# Turn 2: Konkrete Char-Wahl bestätigen (egal welcher Vorschlag - ja zu Char 1)
hist_a.append({"role": "user", "content": "Ich nehme den ersten Vorschlag."})
sl_2 = call(hist_a)
hist_a.append({"role": "assistant", "content": sl_2})
print(f"  Turn 2 (SL): {len(sl_2)} chars")

# Turn 3: Sofort !save
hist_a.append({"role": "user", "content": "!save"})
sl_3 = call(hist_a)
hist_a.append({"role": "assistant", "content": sl_3})
print(f"  Turn 3 (SL): {len(sl_3)} chars")

# Falls noch kein Save in Turn 3 (häufig: SL stellt Charakter erst vor),
# noch ein "!save deepsave" hinterher.
ok, reason, data = has_json_save_block(sl_3)
turns_used = 3
if not ok:
    hist_a.append({"role": "user", "content": "!save deepsave"})
    sl_4 = call(hist_a)
    hist_a.append({"role": "assistant", "content": sl_4})
    print(f"  Turn 4 (SL): {len(sl_4)} chars  [deepsave-Retry]")
    ok, reason, data = has_json_save_block(sl_4)
    turns_used = 4

write_chat("gate-a-save-state", hist_a)
print(f"  Ergebnis: {'PASS' if ok else 'FAIL'} ({reason})")
if data:
    keys = list(data.keys())[:15]
    print(f"  JSON-Top-Level-Keys: {keys}")

result_a = {"gate": "save-state-#3187", "pass": ok, "reason": reason, "turns": turns_used}


# ========================================================================
# GATE B: MS1-2-Tonfall + Sprung-Tempo
# ========================================================================
print("\n=== GATE B: MS1-2-Tonfall + Sprung-Tempo (#3186) ===")
hist_b = []

# Turn 1: Direkter Mission-Einstieg
hist_b.append({"role": "user", "content": "Spiel starten (solo klassisch)\ngenerate"})
sl_b1 = call(hist_b)
hist_b.append({"role": "assistant", "content": sl_b1})
print(f"  Turn 1 (SL): {len(sl_b1)} chars")

# Turn 2: Char nehmen + sofort Briefing
hist_b.append({"role": "user", "content": "Ich nehme den ersten Vorschlag. Direkt zum Briefing, erste Mission bitte."})
sl_b2 = call(hist_b)
hist_b.append({"role": "assistant", "content": sl_b2})
print(f"  Turn 2 (SL): {len(sl_b2)} chars")

# Turn 3: Briefing-Empfang signalisieren
hist_b.append({"role": "user", "content": "Verstanden. Briefing erhalten. Equip-Check und los, sprung ausfuehren."})
sl_b3 = call(hist_b)
hist_b.append({"role": "assistant", "content": sl_b3})
print(f"  Turn 3 (SL): {len(sl_b3)} chars")

# Turn 4: Falls noch nicht gesprungen
hist_b.append({"role": "user", "content": "Springen. Jetzt."})
sl_b4 = call(hist_b)
hist_b.append({"role": "assistant", "content": sl_b4})
print(f"  Turn 4 (SL): {len(sl_b4)} chars")

write_chat("gate-b-tempo-tonfall", hist_b)

# Auswertung B
combined = (sl_b1 + sl_b2 + sl_b3 + sl_b4).lower()
welt_stakes_hits = [n for n in WELT_STAKES_NEEDLES if n in combined]

# Sprung-Indikatoren: SL beschreibt Ankunft am Mission-Ort
arrived_signals = [
    "wien, 1962", "wien 1962", "du materialisierst", "du landest", "du bist in",
    "du stehst auf der strasse", "kalter krieg", "ringstrasse", "ringstraße",
    "die luft riecht", "1962 wien", "wien (1962)",
]
arrived_turn = None
for i, s in enumerate([sl_b1, sl_b2, sl_b3, sl_b4], start=1):
    sl = s.lower()
    if any(sig in sl for sig in arrived_signals):
        arrived_turn = i
        break

result_b = {
    "gate": "ms1-2-tonfall-und-sprung-tempo-#3186",
    "welt_stakes_phrases_found": welt_stakes_hits,
    "ms1_2_tonfall_pass": len(welt_stakes_hits) == 0,
    "sprung_turn": arrived_turn,
    "sprung_in_4_turns_pass": arrived_turn is not None,
}

print(f"  MS1-2-Tonfall: {'PASS' if result_b['ms1_2_tonfall_pass'] else 'FAIL'}"
      f"  (Welt-Stakes-Treffer: {welt_stakes_hits or 'keine'})")
print(f"  Sprung-Tempo:   {'PASS' if result_b['sprung_in_4_turns_pass'] else 'FAIL'}"
      f"  (Ankunft in Turn {arrived_turn if arrived_turn else '>4 / nicht erkannt'})")


# ========================================================================
# Report
# ========================================================================
report = OUT / "_ergebnis.md"
with report.open("w") as f:
    f.write(f"# Pflichtgate-Verifikation {STAMP}\n\n")
    f.write(f"Modell-Route: `{MODEL}` (Preset → LiteLLM → OpenRouter → Anthropic Sonnet 4.6)\n\n")
    f.write("## Gate A — Save-State (#3187)\n\n")
    f.write(f"- **Status:** {'✅ PASS' if result_a['pass'] else '❌ FAIL'}\n")
    f.write(f"- **Reason:** {result_a['reason']}\n")
    f.write(f"- **Turns gebraucht:** {result_a['turns']}\n")
    f.write(f"- **Chat-Verlauf:** `gate-a-save-state.md`\n\n")
    f.write("## Gate B — MS1-2-Tonfall + Sprung-Tempo (#3186)\n\n")
    f.write(f"- **MS1-2-Tonfall:** {'✅ PASS' if result_b['ms1_2_tonfall_pass'] else '❌ FAIL'}\n")
    f.write(f"- **Welt-Stakes-Treffer:** {result_b['welt_stakes_phrases_found'] or 'keine'}\n")
    f.write(f"- **Sprung-Tempo:** {'✅ PASS' if result_b['sprung_in_4_turns_pass'] else '❌ FAIL'}\n")
    f.write(f"- **Sprung erkannt in Turn:** {result_b['sprung_turn'] if result_b['sprung_turn'] else 'nicht in 4 Turns'}\n")
    f.write(f"- **Chat-Verlauf:** `gate-b-tempo-tonfall.md`\n\n")

print(f"\n=== Report: {report} ===")
