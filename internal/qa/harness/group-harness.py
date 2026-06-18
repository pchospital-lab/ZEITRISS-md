#!/usr/bin/env python3
"""
ZEITRISS Group Playtest Harness v1.0
=====================================
Zwei-KI-Architektur:
  - SL: ZEITRISS-Preset in OpenWebUI (Masterprompt + KB)
  - Spieler: Persona-Sub-Agents (Sonnet 4.6, stateless, reine Eingaben)

Aufruf:
  python3 group-harness.py --phase 1   # Solo-Canary: Sarah/Mara (3 Szenen)
  python3 group-harness.py --phase 2   # Gruppen-Canary: 3 Personas, 1 Mission

Env: OPENWEBUI_URL, OPENWEBUI_API_KEY
"""
from __future__ import annotations
import argparse, json, os, sys, time, re, textwrap
from pathlib import Path
import urllib.request, urllib.error

# ─── Config ───────────────────────────────────────────────────────────────────
BASE_URL = os.environ.get("OPENWEBUI_URL", "http://127.0.0.1:8080")
API_KEY  = os.environ["OPENWEBUI_API_KEY"]
SL_MODEL = "zeitriss-v426-uncut"          # OpenWebUI-Preset
PLAYER_MODEL = "anthropic/claude-sonnet-4.6"  # Direkt via OpenWebUI-Router
KB_ID    = "a56706c9-e427-4c6c-9dcb-0eb7cea095c0"  # ZEITRISS 4.2.6 Regelwerk (live Preset-KB, verifiziert 2026-06-15; alt ed01c39c war 404)

# --- Pfade (2026-04-27 Cleanup: env-überschreibbar, Default = neue Workspace-Struktur) ---
# Default: ~/.openclaw/workspace-cloud/playtests/runs/   (pro Run ein Unter-Ordner)
# Override via Env: ZEITRISS_PLAYTEST_OUT_ROOT
_PLAYTESTS_ROOT = Path(os.environ.get(
    "ZEITRISS_PLAYTEST_OUT_ROOT",
    str(Path.home() / ".openclaw" / "workspace-cloud" / "playtests" / "zeitriss"),
))
OUT_ROOT = _PLAYTESTS_ROOT / "runs"

# Fixture-Save für Mara (nach HQ-Erkundung). Kopie aus
# runs/2026-04-19-episode1-mini-solo-sarah-v3-verify/save-after-hq.json.
MARA_SAVE_PATH = _PLAYTESTS_ROOT / "fixtures" / "save-after-hq.json"

# ─── Personas ─────────────────────────────────────────────────────────────────
PERSONAS: dict[str, dict] = {
    "sarah": {
        "real_name": "Sarah",
        "char_name": "Mara Voss",
        "callsign": "SPLINTER",
        "skill": "pro",   # war gestern dabei, kennt die Basics
        "system": textwrap.dedent("""\
            Du bist Sarah, 34, Marketing-Angestellte. Du spielst ZEITRISS — gestern hattest
            du deine erste Session und weißt wie Proben funktionieren.

            CHARAKTER: Mara Voss, Callsign SPLINTER. Infiltration & Spurenanalyse.
            Attribute: GES 5, INT 5 (die anderen 2). Talent: Tatortanalyse (+2 auf INT-Proben).
            Ausrüstung: Dienstpistole, Kevlarweste, Handscanner, Multitool, Comlink, 2x Rauchgranate.

            SPIELVERHALTEN:
            - Du kennst die Mechanik, nutzt sie aber nicht übermäßig taktisch
            - Du fragst gelegentlich nach Regel-Details ("war das nicht +2 auf INT?")
            - Du benutzt Callsigns und Regel-Begriffe, weil du sie vom Vortag kennst
            - Du nimmst die Story ernst, planst aber nicht 5 Züge voraus
            - Beim Kämpfen: taktisch aber nicht perfekt ("ich flankiere und mach INT-Probe")
            - Du gibst dem Charakter eine Stimme ("Voss sagt ruhig: …")
            - Du speicherst ab wenn die KI-SL sagt dass es sinnvoll ist ("!save")
            - Gelegentlich: "Stimmt das mit der W10-Regel, wenn GES auf 11 geht?"

            Antworte NUR mit dem was Sarah in den Chat tippt.
            Kurz bis mittel (1-4 Sätze). Kein Meta-Kommentar. Keine Anführungszeichen drumrum.
        """),
    },
    "jonas": {
        "real_name": "Jonas",
        "char_name": None,   # baut in der Gruppe frisch
        "callsign": None,
        "skill": "normalo",
        "system": textwrap.dedent("""\
            Du bist Jonas, 29, Softwareentwickler. Du hast DSA und Shadowrun gespielt,
            kennst P&P-Systeme aber nicht ZEITRISS. Heute erste Session.

            SPIELVERHALTEN:
            - Du willst das System verstehen, fragst einmal pro Runde was Regeltech-artiges
            - Du liest Texte gründlich, antwortest strukturiert
            - Beim Erstellen: überlegst du deinen Char, fragst nach Optionen
            - Im Spiel: solide, nutzt Regeln korrekt wenn du sie verstanden hast
            - Du machst manchmal Shadowrun-Vergleiche ("ah, wie Würfelpool bei SR?")
            - Beim Kämpfen: fragst nach Modifikatoren, dann führst du aus
            - Du vertraust Sarah bei Unklarheiten ("Sarah, wie läuft das nochmal?")
            - Mittel-lange Antworten (2-5 Sätze)
            - Du spielst einen Nahkampf-orientierten Char (STR 5, GES 4)

            Dein Charakter entsteht in der Gruppe — noch keinen Namen.
            Antworte NUR mit dem was Jonas in den Chat tippt. Kein Meta-Kommentar.
        """),
    },
    "kim": {
        "real_name": "Kim",
        "char_name": None,
        "callsign": None,
        "skill": "noob",
        "system": textwrap.dedent("""\
            Du bist Kim, 26, Barista. ZEITRISS ist dein erstes Rollenspiel überhaupt.
            Deine Freundin Sarah hat dich überredet mitzumachen.

            SPIELVERHALTEN:
            - Du weißt buchstäblich nichts über Rollenspiel-Mechaniken
            - Du fragst nach allem: "Was ist ein Save?", "Muss ich würfeln?", "Was ist TEMP?"
            - Du bist neugierig und enthusiastisch, nicht frustriert
            - Story und Atmosphäre fesselnd dich mehr als Mechanik
            - Dein Char wird zufällig/intuitiv erstellt ("ich will jemanden der gut redet")
            - Im Spiel: impulsive Aktionen, manchmal total falsch für die Situation
            - "Ich geh einfach rein und rede mit dem" (ohne Proben-Plan)
            - Wenn KI-SL viel Text schreibt: "puh, okay. Was soll ich jetzt machen?"
            - Du lachst wenn was schiefgeht, nimmst es locker
            - Kurze Antworten (1-3 Sätze)

            Antworte NUR mit dem was Kim in den Chat tippt. Kein Meta-Kommentar.
        """),
    },

    # ── PHASE 3: 5er-HQ-Anker-Crew (Wallet-SSOT-Spielgefühl) ──────────────────
    # Diese 5 Personas spielen die fixen Anker-Charaktere aus
    # savegame_v7_5er_hq_highlevel.json. Motivationen sind so gewählt, dass
    # Kauf / Unterdeckung / CU-Übergabe / Σ-View ORGANISCH zünden — gebrieft als
    # Motivation, NICHT als Skript. Wallet-Stände im Anker:
    #   Astra 60.400 (reich) | Blitz 6.900 (klamm) | Cipher 8.100 | Dusk 7.600 | Echo 7.050
    "astra": {
        "real_name": "Petra",
        "char_name": "Astra",
        "callsign": "ECHO",
        "skill": "pro",
        "system": textwrap.dedent("""\
            Du bist Petra, 41, erfahrene P&P-Spielerin und inoffizielle Anführerin
            der Crew. Du spielst Astra (Callsign ECHO), Analytik & Spurensicherung.

            CHARAKTER & HALTUNG:
            - Astra ist die Veteranin: ruhig, taktisch, denkt ans Team.
            - Du hast mit ABSTAND am meisten CU im Wallet — du bist finanziell
              komfortabel und weißt das.
            - Du bist großzügig: Wenn ein Crew-Mitglied vor der Mission knapp bei
              Kasse ist und gutes Gear braucht, bietest du von dir aus an, ihm
              CU rüberzuschieben. Du sagst das in deinen eigenen Worten.
            - Du gibst Astra eine ruhige, bestimmte Stimme.

            Antworte NUR mit dem was Petra in den Chat tippt. Kurz bis mittel
            (1-4 Sätze). Kein Meta-Kommentar, keine Anführungszeichen drumrum.
            Wenn du gerade NICHTS beizutragen hast, antworte exakt mit: (hört zu)
        """),
    },
    "blitz": {
        "real_name": "Marco",
        "char_name": "Blitz",
        "callsign": "STORM",
        "skill": "normalo",
        "system": textwrap.dedent("""\
            Du bist Marco, 31, spielst gern offensiv. Du spielst Blitz (Callsign
            STORM), CQB & Sturmangriff — der Frontkämpfer der Crew.

            CHARAKTER & HALTUNG:
            - Blitz will vor der nächsten Mission UNBEDINGT besser ausgerüstet sein:
              eine stärkere Waffe oder bessere Panzerung. Sicherheit geht vor.
            - ABER du bist ziemlich knapp bei Kasse (wenig CU im Wallet). Das weißt
              du nicht genau — du schaust im Markt/beim ITI-Quartiermeister, was
              etwas Gutes kostet, und versuchst es zu kaufen.
            - Wenn dein Geld nicht reicht, ärgerst du dich kurz und überlegst laut,
              ob du anders rankommst (sparen, billigeres Modell, oder jemand hilft aus).
            - Du drängst auch mal aufs Losziehen, bist aber nicht dumm-stürmisch.
            - Du gibst Blitz eine raue, direkte Stimme.

            Antworte NUR mit dem was Marco in den Chat tippt. Kurz (1-3 Sätze).
            Kein Meta-Kommentar. Wenn du gerade NICHTS beizutragen hast, antworte
            exakt mit: (hört zu)
        """),
    },
    "cipher": {
        "real_name": "Lena",
        "char_name": "Cipher",
        "callsign": "GHOST",
        "skill": "pro",
        "system": textwrap.dedent("""\
            Du bist Lena, 27, detailverliebte Spielerin. Du spielst Cipher (Callsign
            GHOST), Infiltration & Hacking.

            CHARAKTER & HALTUNG:
            - Cipher behält gern den Überblick — auch über die Finanzen der Crew.
            - Vor Anschaffungen fragst du schon mal nach: "Wie viel haben wir
              eigentlich zusammen?" oder willst die Gruppenkasse / Wallet-Stände sehen.
            - Pragmatisch, plant, mag saubere Zahlen.
            - Du gibst Cipher eine trockene, präzise Stimme.

            Antworte NUR mit dem was Lena in den Chat tippt. Kurz (1-3 Sätze).
            Kein Meta-Kommentar. Wenn du gerade NICHTS beizutragen hast, antworte
            exakt mit: (hört zu)
        """),
    },
    "dusk": {
        "real_name": "Tarek",
        "char_name": "Dusk",
        "callsign": "VEIL",
        "skill": "pro",
        "system": textwrap.dedent("""\
            Du bist Tarek, 35, vorsichtiger Taktiker. Du spielst Dusk (Callsign
            VEIL), Verdeckte Aufklärung.

            CHARAKTER & HALTUNG:
            - Dusk ist sparsam und besonnen: erst Lage checken, dann Geld ausgeben.
            - Du gibst dein CU nicht leichtfertig aus, hältst dich beim Shoppen zurück.
            - Du achtest auf die Crew und gibst ruhige Einschätzungen.
            - Du gibst Dusk eine leise, bedachte Stimme.

            Antworte NUR mit dem was Tarek in den Chat tippt. Kurz (1-3 Sätze).
            Kein Meta-Kommentar. Wenn du gerade NICHTS beizutragen hast, antworte
            exakt mit: (hört zu)
        """),
    },
    "echo_p": {
        "real_name": "Sven",
        "char_name": "Echo",
        "callsign": "RELAY",
        "skill": "normalo",
        "system": textwrap.dedent("""\
            Du bist Sven, 33, Teamplayer. Du spielst Echo (Callsign RELAY),
            Support & Feldtechnik.

            CHARAKTER & HALTUNG:
            - Echo kümmert sich um Logistik und Verbrauchsmaterial (Med-Patches,
              Granaten) für die ganze Crew.
            - Du kaufst auch mal kleinere Sachen für den Einsatz aus deinem Wallet.
            - Du bist verbindlich, hältst die Gruppe zusammen.
            - Du gibst Echo eine warme, sachliche Stimme.

            Antworte NUR mit dem was Sven in den Chat tippt. Kurz (1-3 Sätze).
            Kein Meta-Kommentar. Wenn du gerade NICHTS beizutragen hast, antworte
            exakt mit: (hört zu)
        """),
    },
}

# ─── Playtest-Szenarien ────────────────────────────────────────────────────────
# Stop-Hints müssen präzise sein — generisches "DEBRIEF" matchte früher
# falsch auf Regel-Erklärungen der SL. Phase-Tags + HUD-Marker sind eindeutig.
STOP_HINTS_MISSION_END = [
    "PHASE Debrief",
    "PHASE debrief",
    "Mission abgeschlossen",
    "SC 13/12",
    "SC 12/12",
    "Episode endet",
    "Save empfohlen",
    "!save\n",
]

PHASE1_SCENARIO = {
    "name": "phase1-canary-sarah-solo",
    "description": "Sarah importiert Mara Voss, spielt 3 Szenen solo CoreOps",
    "players": ["sarah"],
    "max_turns": 20,  # ca. 3 Szenen
    "opening": (
        "Spiel laden:\n\n"
        + MARA_SAVE_PATH.read_text(encoding="utf-8")
        if MARA_SAVE_PATH.exists()
        else "Spiel starten (solo klassisch)"
    ),
    "stop_hints": ["SC 3/12", "SC 4/12"] + STOP_HINTS_MISSION_END,
    # out_dir: beim Start per _STAMP datiert (runs/YYYY-MM-DD-<name>/)
    "out_dir": OUT_ROOT / f"{time.strftime('%Y-%m-%d')}-phase1-canary",
}

PHASE2_SCENARIO = {
    "name": "phase2-group-canary-3p",
    "description": "3 Personas starten gemeinsam: Sarah importiert Mara, Jonas+Kim bauen frisch. Mission 1 komplett.",
    "players": ["jonas", "kim", "sarah"],  # Jonas+Kim tippen zuerst beim Gruppenstart
    "max_turns": 60,
    "opening": "Spiel starten (gruppe klassisch)",
    "stop_hints": STOP_HINTS_MISSION_END,
    "out_dir": OUT_ROOT / f"{time.strftime('%Y-%m-%d')}-phase2-group",
}

# Phase 2C: Wiederholung von Phase 2 mit präzisem Stop-Hint + Token-Profiling.
# Ziel: Mission 1 komplett durchspielen bis inkl. !save, messen wo der Context
# realistisch landet. Baseline für den 8K-MP-A/B-Test.
PHASE2C_SCENARIO = {
    "name": "phase2c-group-mission1-full",
    "description": "Phase 2 Wiederholung: Mission 1 komplett mit präzisen Stop-Hints + Token-Profiling",
    "players": ["jonas", "kim", "sarah"],
    "max_turns": 80,  # 12 Szenen à ~5 Turns + Buffer
    "opening": "Spiel starten (gruppe klassisch)",
    "stop_hints": STOP_HINTS_MISSION_END,
    "out_dir": OUT_ROOT / f"{time.strftime('%Y-%m-%d')}-phase2c-group-mission1",
}

# Phase 3: Organischer 5er-Lauf aus dem vollständigen HQ-Anker (Wallet-SSOT).
# Ziel: Kauf-aus-Wallet, Unterdeckungs-Scheitern, CU-Übergabe (Befehl + nat.
# Sprache), Gruppenkasse-Σ-View ORGANISCH erleben. Start im HQ, damit die
# Geld-Beats sofort zünden (Aufrüsten vor der Mission), dann in die Mission.
ANCHOR_5ER = Path(
    "/mnt/agent_share/cloud/repos/ZEITRISS-md-git/internal/qa/fixtures/savegame_v7_5er_hq_highlevel.json"
)
PHASE3_SCENARIO = {
    "name": "phase3-5er-wallet-organisch",
    "description": (
        "5er-Anker-Crew (Astra/Blitz/Cipher/Dusk/Echo) lädt HQ-Save, rüstet "
        "organisch auf (Kauf/Unterdeckung/Übergabe/Σ-View), dann eine Mission."
    ),
    "players": ["astra", "blitz", "cipher", "dusk", "echo_p"],
    "max_turns": 70,
    "opening": (
        "Spiel laden:\n\n" + ANCHOR_5ER.read_text(encoding="utf-8")
        if ANCHOR_5ER.exists()
        else "Spiel starten (gruppe klassisch)"
    ),
    "stop_hints": STOP_HINTS_MISSION_END,
    "out_dir": OUT_ROOT / f"{time.strftime('%Y-%m-%d-%H%M')}-phase3-5er-wallet",
}

# ─── API helpers ──────────────────────────────────────────────────────────────
def _post(path: str, body: dict, timeout: int = 420) -> dict:
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        BASE_URL + path,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()
        raise RuntimeError(f"HTTP {e.code}: {body_text[:500]}") from e


def sl_turn(messages: list[dict]) -> tuple[str, int, int, float]:
    """Send turn to SL (ZEITRISS preset).
    Returns (reply, prompt_tokens, completion_tokens, latency_seconds).
    """
    t0 = time.time()
    resp = _post(
        "/api/chat/completions",
        {
            "model": SL_MODEL,
            "messages": messages,
            "stream": False,
            "files": [{"type": "collection", "id": KB_ID}],
        },
    )
    latency = time.time() - t0
    choice = resp["choices"][0]["message"]["content"]
    usage  = resp.get("usage") or {}
    return choice, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0), latency


def player_turn(persona_key: str, sl_text: str, history_hint: str = "") -> str:
    """Ask persona agent for their input given the SL's last message."""
    p = PERSONAS[persona_key]
    context = (
        f"Die KI-Spielleitung schreibt gerade folgendes in den Chat:\n\n"
        f"---\n{sl_text[:4000]}\n---\n\n"
    )
    if history_hint:
        context += f"Bisherige Runde kurz:\n{history_hint[:500]}\n\n"
    context += "Was tippst du jetzt in den Chat? (kurz, als dein Charakter)"

    resp = _post(
        "/api/chat/completions",
        {
            "model": PLAYER_MODEL,
            "messages": [
                {"role": "system", "content": p["system"]},
                {"role": "user",   "content": context},
            ],
            "temperature": 0.92,
            "max_tokens": 300,
            "stream": False,
        },
        timeout=60,
    )
    return resp["choices"][0]["message"]["content"].strip()


# ─── Harness runner ───────────────────────────────────────────────────────────
class PlaytestSession:
    def __init__(self, scenario: dict):
        self.sc = scenario
        self.out: Path = scenario["out_dir"]
        self.out.mkdir(parents=True, exist_ok=True)
        self.log_path    = self.out / "_live.log"
        self.report_path = self.out / "_bericht.md"
        self.tokens_csv  = self.out / "_tokens.csv"
        self.sl_history: list[dict] = []
        self.turn = 0
        self.total_prompt = 0
        self.total_completion = 0
        self.findings: list[str] = []
        self.token_log: list[dict] = []
        # Wallet-Beat-Tracker (Phase 3) — jeweils einmalig melden
        self._w_buy = self._w_fail = self._w_transfer = self._w_sigma = False
        # CSV-Header für Token-Profiling (Gnuplot-friendly)
        self.tokens_csv.write_text(
            "turn,prompt_tokens,completion_tokens,total_tokens,cum_tokens,latency_s,sl_reply_chars\n",
            encoding="utf-8",
        )

        # Open report
        self.report_path.write_text(
            f"# Playtest-Bericht: {scenario['name']}\n\n"
            f"**Datum:** {time.strftime('%Y-%m-%d %H:%M')}\n"
            f"**Szenario:** {scenario['description']}\n"
            f"**Modell SL:** {SL_MODEL}\n"
            f"**Modell Spieler:** {PLAYER_MODEL}\n\n"
            "---\n\n",
            encoding="utf-8",
        )

    def log(self, msg: str):
        ts = time.strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        print(line, flush=True)
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    def append_report(self, text: str):
        with self.report_path.open("a", encoding="utf-8") as f:
            f.write(text + "\n\n")

    def finding(self, tag: str, text: str):
        entry = f"[{tag}] {text}"
        self.findings.append(entry)
        self.log(f"⚠️  FINDING: {entry}")
        self.append_report(f"> **⚠️ Finding [{tag}]:** {text}")

    def _check_quality(self, sl_text: str):
        """Quick automated quality checks on SL output."""
        # Check save schema
        if '"v":' in sl_text and '"v": 7' not in sl_text and '"v":7' not in sl_text:
            self.finding("SAVE-SCHEMA", f"Save ohne v:7 in Ausgabe gefunden")
        # Check HP vs LP
        if re.search(r'\bHP\b', sl_text) and 'LP' not in sl_text:
            self.finding("TERMINOLOGIE", "SL nutzt 'HP' statt 'LP'")
        # Check W10-Schwelle hallucination (attributes < 11 triggering W10)
        m = re.search(r'W10.*Attribut\s+(\d+)', sl_text, re.IGNORECASE)
        if m and int(m.group(1)) < 11:
            self.finding("W10-SCHWELLE", f"Mögliche W10-Halluzination bei Attribut {m.group(1)}")
        # Psi cost check (2 PP / 2 SYS for Mentale Maskierung)
        if 'Mentale Maskierung' in sl_text:
            if '1 SYS' in sl_text and '2 SYS' not in sl_text:
                self.finding("PSI-KOSTEN", "Mentale Maskierung zeigt 1 SYS statt 2 SYS")
        # --- Wallet-SSOT-Beat-Detektoren (Phase 3) ---
        low = sl_text.lower()
        if not self._w_buy and re.search(r'(gekauft|erworben|kauf\s+verbucht|wallet\s+\w+:?\s*-?\d|abgebucht)', low):
            self._w_buy = True
            self.finding("WALLET-KAUF", "Kauf aus Wallet erkannt — Beat (a) gezündet (manuell prüfen)")
        if not self._w_fail and re.search(r'nicht genug cu|deckt\b.*nicht|übergabe abgebrochen|kauf.*gescheitert|reicht.*nicht', low):
            self._w_fail = True
            self.finding("WALLET-UNTERDECKUNG", "Unterdeckungs-Scheitern erkannt — Beat (a-fail) gezündet (manuell prüfen)")
        if not self._w_transfer and re.search(r'cu-übergabe|cu_transfer|übergabe verbucht|\u2192.*cu', low):
            self._w_transfer = True
            self.finding("WALLET-UEBERGABE", "CU-Übergabe erkannt — Beat (b) gezündet (manuell prüfen)")
        if not self._w_sigma and 'gruppenkasse' in low:
            self._w_sigma = True
            self.finding("WALLET-SIGMA", "Gruppenkasse-Σ-View angezeigt — Beat (c) gezündet (manuell prüfen)")

    def run(self):
        sc = self.sc
        players = sc["players"]
        self.log(f"=== PHASE START: {sc['name']} ===")
        self.log(f"Spieler: {players}")
        self.log(f"Max turns: {sc['max_turns']}")

        # --- Opening ---
        if len(players) == 1:
            # Solo: direkt mit Opening-Nachricht
            opening_msg = sc["opening"]
            self.log(f">>> {players[0].upper()}: {opening_msg[:80]}")
            self.append_report(f"## Turn 0 — Start\n\n**{players[0].upper()}:** {opening_msg[:200]}")
            self.sl_history.append({"role": "user", "content": opening_msg})
        else:
            # Gruppe: Gemeinsam starten
            opening_msg = sc["opening"]
            self.log(f">>> GRUPPE: {opening_msg}")
            self.append_report(f"## Turn 0 — Gruppenstart\n\n**GRUPPE:** {opening_msg}")
            self.sl_history.append({"role": "user", "content": opening_msg})

        # --- Main loop ---
        for turn_num in range(sc["max_turns"]):
            self.turn = turn_num + 1
            self.log(f"\n--- Turn {self.turn} ---")

            # SL responds
            try:
                sl_text, pt, ct, latency = sl_turn(self.sl_history)
            except Exception as e:
                self.finding("SL-ERROR", str(e)[:200])
                self.log(f"❌ SL-Fehler: {e}")
                break

            self.total_prompt += pt
            self.total_completion += ct
            cum_total = self.total_prompt + self.total_completion
            self.log(
                f"<<< SL ({pt}p/{ct}c/{latency:.1f}s, cum={cum_total}): "
                f"{sl_text[:100].replace(chr(10),' ')}"
            )
            # Token-Profile: pro Turn + kumulativ in CSV
            with self.tokens_csv.open("a", encoding="utf-8") as f:
                f.write(f"{self.turn},{pt},{ct},{pt + ct},{cum_total},{latency:.2f},{len(sl_text)}\n")
            self.token_log.append({
                "turn": self.turn, "prompt": pt, "completion": ct,
                "cum": cum_total, "latency_s": round(latency, 2),
            })
            # Context-Window-Druck (Sonnet 4.6 = 256k Kontext, KORRIGIERT 2026-06-16)
            if pt > 180_000 and not any("CTX-WARN" in fi for fi in self.findings):
                self.finding("CTX-WARN", f"Prompt {pt} tokens — über 70% des 256k-Kontextfensters (Sonnet 4.6)")
            if pt > 230_000 and not any("CTX-LIMIT" in fi for fi in self.findings):
                self.finding("CTX-LIMIT", f"Prompt {pt} tokens — nähert sich 256k Limit (Sonnet 4.6)")
            self.sl_history.append({"role": "assistant", "content": sl_text})

            # Quality check
            self._check_quality(sl_text)

            # Save SL turn
            turn_file = self.out / f"turn-{self.turn:03d}-sl.md"
            turn_file.write_text(f"# Turn {self.turn} — SL\n\n{sl_text}\n", encoding="utf-8")
            self.append_report(f"### Turn {self.turn} — SL\n\n{sl_text[:2000]}")

            # Stop condition
            for hint in sc["stop_hints"]:
                if hint.lower() in sl_text.lower():
                    self.log(f"🛑 Stop-Hint erkannt: '{hint}' — Phase beendet")
                    self._finalize(reason=f"Stop-Hint: {hint}")
                    return

            # Players respond
            if len(players) == 1:
                # Solo
                p = players[0]
                try:
                    p_text = player_turn(p, sl_text)
                except Exception as e:
                    self.finding("PLAYER-ERROR", f"{p}: {e}")
                    p_text = "!save"  # Fallback

                self.log(f">>> {p.upper()}: {p_text[:100]}")
                pfile = self.out / f"turn-{self.turn:03d}-{p}.md"
                pfile.write_text(f"# Turn {self.turn} — {p}\n\n{p_text}\n", encoding="utf-8")
                self.append_report(f"**{p.upper()} ({PERSONAS[p]['char_name'] or p}):** {p_text}")
                self.sl_history.append({"role": "user", "content": p_text})

            else:
                # Gruppe: Alle Spieler antworten, gebündelt an SL
                combined_parts = []
                history_hint = sl_text[:300]
                for p in players:
                    try:
                        p_text = player_turn(p, sl_text, history_hint)
                    except Exception as e:
                        self.finding("PLAYER-ERROR", f"{p}: {e}")
                        p_text = "(keine Eingabe)"

                    char = PERSONAS[p].get("char_name") or PERSONAS[p]["real_name"]
                    self.log(f">>> {p.upper()} ({char}): {p_text[:80]}")
                    pfile = self.out / f"turn-{self.turn:03d}-{p}.md"
                    pfile.write_text(f"# Turn {self.turn} — {p}\n\n{p_text}\n", encoding="utf-8")
                    # Passiv-Filter: "(hört zu)"/(keine Eingabe) NICHT an die SL
                    # bündeln — sonst rauscht jeder Beat mit 5 Pflicht-Eingaben zu.
                    stripped = p_text.strip().lower()
                    if stripped in ("(hört zu)", "(hoert zu)", "(keine eingabe)", ""):
                        continue
                    combined_parts.append(f"**{char}** [{PERSONAS[p]['real_name']}]: {p_text}")

                # Bundle all player inputs (mind. 1 — sonst neutraler Fortschritts-Prompt)
                if not combined_parts:
                    combined_parts.append("(Die Crew wartet ab — mach weiter.)")
                combined = "\n\n".join(combined_parts)
                self.append_report(f"**SPIELER-EINGABEN:**\n\n{combined}")
                self.sl_history.append({"role": "user", "content": combined})

            time.sleep(1)  # Rate limiting

        self._finalize(reason="max_turns erreicht")

    def _finalize(self, reason: str = ""):
        self.log(f"\n=== PHASE ENDE: {reason} ===")
        # Token-Profil-Zusammenfassung
        peak_prompt = max((t["prompt"] for t in self.token_log), default=0)
        avg_latency = (
            sum(t["latency_s"] for t in self.token_log) / len(self.token_log)
            if self.token_log else 0.0
        )
        # Write summary
        summary = (
            f"## Zusammenfassung\n\n"
            f"**Ende-Grund:** {reason}\n"
            f"**Turns:** {self.turn}\n"
            f"**Tokens gesamt:** {self.total_prompt + self.total_completion} "
            f"(Prompt: {self.total_prompt}, Completion: {self.total_completion})\n"
            f"**Peak Prompt:** {peak_prompt} tokens "
            f"({peak_prompt / 256_000:.1%} von Sonnet-4.6-256k)\n"
            f"**Ø Latenz pro Turn:** {avg_latency:.1f}s\n"
            f"**CSV:** `{self.tokens_csv.name}` (turn,prompt,completion,total,cum,latency,chars)\n\n"
            f"**Findings ({len(self.findings)}):**\n"
        )
        for f in self.findings:
            summary += f"- {f}\n"
        if not self.findings:
            summary += "- keine\n"
        self.append_report(summary)
        self.log(f"Report: {self.report_path}")
        self.log(f"Tokens: {self.total_prompt + self.total_completion} (peak prompt: {peak_prompt})")
        self.log(f"Findings: {len(self.findings)}")


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="ZEITRISS Group Playtest Harness")
    parser.add_argument("--phase", choices=["1", "2", "2c", "3"], required=True)
    args = parser.parse_args()

    if args.phase == "1":
        scenario = PHASE1_SCENARIO
    elif args.phase == "2":
        scenario = PHASE2_SCENARIO
    elif args.phase == "2c":
        scenario = PHASE2C_SCENARIO
    else:  # 3
        scenario = PHASE3_SCENARIO

    print(f"\n🎮 ZEITRISS Playtest-Harness v1.0")
    print(f"Phase {args.phase}: {scenario['description']}\n")

    session = PlaytestSession(scenario)
    try:
        session.run()
    except KeyboardInterrupt:
        session._finalize(reason="Abgebrochen (Ctrl+C)")
        sys.exit(0)


if __name__ == "__main__":
    main()
