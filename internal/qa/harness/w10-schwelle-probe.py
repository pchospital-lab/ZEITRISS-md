#!/usr/bin/env python3
"""W10-Schwellen-Runtime-Verifikation V3 - Statistisch mit Mehrfachlaeufen.

V1/V2 haben gezeigt: Einzelne Runs geben kein sauberes Signal. Sonnet 4.6
antwortet probabilistisch. Daher jetzt jedes Szenario N-mal wiederholen
und Pass-Rate berechnen.

Fokus: Szenarien A (Level-Up INT 5->6) und D (Buff-Fall). B und C waren
in V1+V2 beide robust, brauchen kein Mehrfach-Checking.

N = 10 Runs pro Szenario. Gesamt: 20 API-Calls * ca. 3 Turns = ca. 60 Calls.
"""
import json, os, time, re, requests
from pathlib import Path
from collections import Counter

API_KEY = os.environ["OPENWEBUI_API_KEY"]
BASE = "http://127.0.0.1:3000/api/chat/completions"
MODEL = "anthropic/claude-sonnet-4.6"
N_RUNS = 10

# --- Pfade (2026-04-27 Cleanup: env-überschreibbar, Default = neue Workspace-Struktur) ---
_PLAYTESTS_ROOT = Path(os.environ.get(
    "ZEITRISS_PLAYTEST_OUT_ROOT",
    str(Path.home() / ".openclaw" / "workspace-cloud" / "playtests" / "zeitriss"),
))
SL_SYSTEM = (_PLAYTESTS_ROOT / "harness" / "zeitriss-sysprompt.txt").read_text()
# Ein Run pro Aufruf, Timestamp im Ordnernamen.
_STAMP = time.strftime("%Y-%m-%d-%H%M")
OUT_DIR = _PLAYTESTS_ROOT / "runs" / f"{_STAMP}-w10-schwelle-probe"
OUT_DIR.mkdir(exist_ok=True, parents=True)
REPORT = OUT_DIR / "_bericht.md"

def call_api(messages, max_tokens=2500):
    r = requests.post(BASE,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"model": MODEL,
              "messages": [{"role": "system", "content": SL_SYSTEM}] + messages,
              "temperature": 0.6, "top_p": 0.9, "frequency_penalty": 0.3,
              "max_tokens": max_tokens},
        timeout=180)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

def make_save(char_name, callsign, attributes, talents=None, level=2, mission_count=1):
    talents = talents or []
    return {
        "v": 7, "zr": "4.2.6",
        "save_id": f"SAVE-TEST-{callsign}-{int(time.time())}",
        "parent_save_id": None,
        "arc": {"factions": {"iti": 2, "tessera": 0, "echelon": 0},
                "questions": ["Ist die Zeitlinie noch stabil?"],
                "hooks": ["Naechster Sprung nach Krakau 1982."]},
        "characters": [{
            "id": f"CHR-{callsign}-TEST",
            "name": char_name, "callsign": callsign,
            "level": level, "xp": 0, "px": 1, "stress": 0, "vital": 10,
            "attributes": attributes,
            "talents": talents,
            "gear": [{"name": "Dienstpistole M7", "tier": 1}],
            "iti_reputation": 1, "license_tier": 1
        }],
        "progress": {"episode": 1, "mission": mission_count,
                     "completed_missions": list(range(1, mission_count + 1))},
        "status": {"location": "HQ", "phase": "HQ"}
    }

SZENARIEN = [
    {
        "id": "A_falsch_trigger",
        "titel": "Level-Up INT 5->6 (darf KEIN W10)",
        "save": make_save("Lena Voss", "Wire",
            {"STR": 3, "GES": 4, "INT": 5, "CHA": 3, "TEMP": 2, "SYS": 1},
            talents=[{"name": "Systemzugriff", "tier": "Basis",
                      "effect": "+2 auf INT-Proben bei Hacking und Technik-Analyse"}]),
        "user_msgs": [
            "Spiel laden",
            "Ich mache jetzt mein Level-Up. Ich nehm +1 Attribut - INT von 5 auf 6.",
            "Kannst du kurz INT-Probe machen, Datenanalyse? SG 7."
        ],
        "check_turn_index": -1,
        "verstoss_pattern": [
            (r"W10:\s*\[?\d", "W10-Wurf bei Probe"),
            (r"INT-Schwelle\s+6\s+erreicht|Wuerfelbasis\s+wechselt\s+auf\s+W10|W\u00fcrfelbasis\s+wechselt\s+auf\s+W10", "Halluzinierte Schwelle bei 6"),
            (r"Systemzugriff-Schwellenwert", "Talent-Schwellenwert-Halluzination"),
        ],
    },
    {
        "id": "D_temporaerer_buff",
        "titel": "Buff GES 9 + Injektor +3 (darf KEIN W10)",
        "save": make_save("Sara Lindqvist", "Axis",
            {"STR": 4, "GES": 9, "INT": 4, "CHA": 4, "TEMP": 2, "SYS": 1},
            talents=[{"name": "Adrenalin-Injektor", "tier": "Basis",
                      "effect": "Einmal pro Mission: +3 auf GES-Proben fuer eine Szene"}]),
        "user_msgs": [
            "Spiel laden",
            "Ich bin mitten in Verfolgungsjagd. Ich aktiviere Adrenalin-Injektor (+3 GES). Dann Kletterprobe, SG 10.",
        ],
        "check_turn_index": -1,
        "verstoss_pattern": [
            (r"W10:\s*\[?\d", "W10-Wurf bei Probe (Buff-Halluzination)"),
            (r"GES\s+9\s*\u2192\s*W10|GES\s*\u2265\s*9[\s\S]{0,40}W10", "Halluzinierte GES-Schwelle"),
            (r"\u230a12\s*/\s*2\u230b|\u230a\(9\s*\+\s*3\)\s*/\s*2\u230b", "Falsche Formel (Buff ins Attribut)"),
        ],
    }
]

def run_once(sz):
    save_json = json.dumps(sz["save"], ensure_ascii=False, indent=2)
    history = []
    for i, user_msg in enumerate(sz["user_msgs"]):
        full = f"{user_msg}\n```json\n{save_json}\n```" if i == 0 else user_msg
        history.append({"role": "user", "content": full})
        try:
            sl_response = call_api(history)
        except Exception as e:
            return None, f"API_ERROR: {e}"
        history.append({"role": "assistant", "content": sl_response})
        time.sleep(0.3)
    final = history[-1]["content"]
    verstoesse = []
    for pattern, label in sz["verstoss_pattern"]:
        m = re.search(pattern, final, re.IGNORECASE)
        if m:
            verstoesse.append((label, m.group(0)[:80]))
    return verstoesse, final

# Mehrfach-Runs
all_results = {}
for sz in SZENARIEN:
    print(f"\n=== {sz['id']}: {sz['titel']} ===")
    print(f"Running {N_RUNS} times...")
    results = []
    for i in range(N_RUNS):
        verstoesse, final = run_once(sz)
        passed = verstoesse == []
        results.append({"run": i + 1, "pass": passed, "verstoesse": verstoesse, "final": final})
        mark = "PASS" if passed else "FAIL"
        first_violation = verstoesse[0] if verstoesse else None
        print(f"  Run {i+1}/{N_RUNS}: {mark}" + (f" - {first_violation[0]}: {first_violation[1][:50]}" if first_violation else ""))
    all_results[sz["id"]] = {"titel": sz["titel"], "runs": results}

# Auswertung
with REPORT.open("w") as f:
    f.write(f"""# W10-Schwellen-Runtime-Verifikation V3 (Statistisch)

**Datum:** {time.strftime('%Y-%m-%d %H:%M')}
**Modell:** {MODEL}
**Masterprompt-Version:** v4.2.6 nach PR #2955 + Buff-Patch (kompaktiert)
**N Runs pro Szenario:** {N_RUNS}

## Zusammenfassung

| Szenario | Titel | Pass-Rate | Verdict |
|----------|-------|-----------|---------|
""")
    for sz_id, data in all_results.items():
        passed = sum(1 for r in data["runs"] if r["pass"])
        rate = passed / N_RUNS
        if rate == 1.0: verdict = "Perfekt"
        elif rate >= 0.8: verdict = "Robust"
        elif rate >= 0.5: verdict = "Instabil"
        else: verdict = "Nicht behoben"
        f.write(f"| {sz_id} | {data['titel']} | {passed}/{N_RUNS} ({int(rate*100)}%) | {verdict} |\n")
    f.write("\n---\n\n## Details pro Szenario\n\n")
    for sz_id, data in all_results.items():
        passed = sum(1 for r in data["runs"] if r["pass"])
        f.write(f"### {data['titel']}\n\n**{passed}/{N_RUNS} Runs bestanden.**\n\n")
        # Histogramm der Verstoesse
        violation_types = Counter()
        for r in data["runs"]:
            for v_type, _ in r["verstoesse"]:
                violation_types[v_type] += 1
        if violation_types:
            f.write("**Verstoesse-Verteilung:**\n\n")
            for v_type, count in violation_types.most_common():
                f.write(f"- `{v_type}`: {count}/{N_RUNS}\n")
            f.write("\n")
        # Runs-Liste
        f.write("**Run-Details:**\n\n")
        for r in data["runs"]:
            mark = "✅" if r["pass"] else "❌"
            verstoss_short = ", ".join(v[0] for v in r["verstoesse"]) or "—"
            f.write(f"- Run {r['run']}: {mark} · {verstoss_short}\n")
        f.write("\n")
        # Exemplarischer Fail-Log
        first_fail = next((r for r in data["runs"] if not r["pass"]), None)
        if first_fail:
            f.write("<details><summary>Beispiel-Fail (Run " + str(first_fail["run"]) + ", finaler SL-Output)</summary>\n\n```\n")
            f.write(first_fail["final"][:2500] + ("\n[...gekuerzt...]" if len(first_fail["final"]) > 2500 else ""))
            f.write("\n```\n\n</details>\n\n")
    f.write("\n---\n\n## Interpretation\n\n")
    f.write("Pass-Rate ab 90% = Patch wirkt zuverlaessig fuer Produktions-Einsatz.\n")
    f.write("Pass-Rate 50-89% = Patch reduziert Bug, aber nicht zuverlaessig.\n")
    f.write("Pass-Rate unter 50% = Patch wirkt nicht. Neuer Ansatz noetig.\n")

print(f"\n=== BERICHT ===")
for sz_id, data in all_results.items():
    passed = sum(1 for r in data["runs"] if r["pass"])
    print(f"  {sz_id}: {passed}/{N_RUNS}")
print(f"Bericht: {REPORT}")
