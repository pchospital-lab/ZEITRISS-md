#!/usr/bin/env python3
"""
ZEITRISS CoreOps Playtest Harness v2.1 (Verification Run — PSI-Kim)
==================================================================

**Zweck (2026-04-23):** Verifikation der PR #2963-Patches live:
  1. Level-Up-Exklusivitäts-Pflichtgate (Anti-Stacking)
  2. Mission-Transition-Pflichtgate (Anti-Skip: Exfil→Debrief→LvlUp→!save)
  3. HUD-Gate-Policy + Kodex-Typ-A/B/C/D

**Änderungen gegenüber v2.0:**
  - Kim baut PSI-Char (Telepathie + Prekognition), um psi-pp-Metric zu
    aktivieren (war 0% im 80-Turn-Run).
  - Default 40 Turns (statt 80) — fokussierter Verification-Run.
  - MP-Section-Regexen korrigiert (v1 hatte 0% bei probe-formel gemeldet,
    real 50%). Siehe _mp-sections-v2.csv Generator.
  - Status-Progress in Log alle 5 Turns explizit (`--- Progress N/X ---`).

**Original-Ziel (v2.0):** Messen welche MP-Abschnitte in einer CoreOps-
Mission aktiv gebraucht werden, welche silent bleiben, und welche von der
KB geliefert werden.
Ziel: Messen welche MP-Abschnitte in einer CoreOps-Mission aktiv gebraucht
werden, welche silent bleiben, und welche von der KB geliefert werden.

Zwei-KI-Architektur:
  - SL: ZEITRISS-Preset in OpenWebUI (Masterprompt + KB)
  - Spieler: Persona-Sub-Agents (Sonnet 4.6, stateless)

Differenz zu group-harness.py:
  - Port 8080 (OpenWebUI 0.9.1)
  - KB `bb266c62...` (22.04. Recovery-Build)
  - CoreOps-Szenario ohne vordefinierte Mission (frei interpretiert)
  - MP-Usage-Tracking: pro Turn markieren welche Regeln/Abschnitte triggern
  - Timeout-Guards + PID-File

Aufruf:
  python3 coreops-harness.py --turns 60

Env: OPENWEBUI_URL (default :8080), OPENWEBUI_API_KEY
"""
from __future__ import annotations
import argparse, json, os, sys, time, re, textwrap, atexit, signal
from pathlib import Path
import urllib.request, urllib.error

# ─── Config ───────────────────────────────────────────────────────────────────
BASE_URL = os.environ.get("OPENWEBUI_URL", "http://127.0.0.1:8080")
API_KEY  = os.environ["OPENWEBUI_API_KEY"]
SL_MODEL = "zeitriss-v426-uncut"
PLAYER_MODEL = "anthropic/claude-sonnet-4.6"
KB_ID = "bb266c62-31c4-4fbd-b332-fd991dd8aaba"  # 22.04. Recovery-KB, 19 Files, Canary 4/4

STAMP = time.strftime("%Y-%m-%d")
# --- Pfade (2026-04-27 Cleanup: env-überschreibbar, Default = neue Workspace-Struktur) ---
_PLAYTESTS_ROOT = Path(os.environ.get(
    "ZEITRISS_PLAYTEST_OUT_ROOT",
    str(Path.home() / ".openclaw" / "workspace-cloud" / "playtests" / "zeitriss"),
))
# Pro-Run-Ordner: runs/YYYY-MM-DD-<scenario-name>/ (scenario["name"] vom Scenario-Dict)
OUT_ROOT = _PLAYTESTS_ROOT / "runs"
PID_FILE = Path("/home/altair/.openclaw/workspace-cloud/tmp/running/coreops-harness.pid")

# Timeout-Guards (Lektion 22.04. Zombie)
SL_TIMEOUT = 420  # 7 Min — SL kann bei langen Szenen dauern
PLAYER_TIMEOUT = 60

# ─── MP-Section-Tracker ──────────────────────────────────────────────────────
# Regex pro MP-Abschnitt: wenn ein Pattern matched, zählt der Abschnitt als "aktiv"
# Das ist Proxy-Messung, nicht perfekt — aber billig und empirisch sinnvoll.
MP_SECTIONS = {
    # v2.1: Regexen auf reale SL-Outputs kalibriert (v1 hatte 0% bei probe-formel
    # gemeldet, real 50% — SL schreibt "W6: [5] + ⌊…", nicht "1W6 + ⌊…").
    "probe-formel": [
        r"Probe:\s+\w", r"W6:\s*\[\d", r"vs\s+SG\s*\d",
        r"\bERFOLG\b", r"\bMISS\b",
    ],
    "w10-schwelle": [
        r"W10:\s*\[\d", r"W10-Schwelle", r"Attribut.*≥\s*11",
    ],
    "heldenwuerfel": [
        r"Heldenw(ü|ue)rfel", r"\bBurst\b", r"Exploding:\s*\[\d",
        r"Attribut\s*≥\s*14",
    ],
    "sys-mechanik": [
        r"\bSYS\b", r"System-Strain", r"SYS-Kosten", r"SYS\s*\+?\d+",
    ],
    "psi-pp": [
        r"\bPP\b(?!\w)", r"Psi-Punkte", r"\d+\s*PP\b", r"Psi-Reserve",
        r"Telepathie", r"Prekognition", r"Psionik", r"Psi-Probe",
    ],
    "lp-verletzung": [
        r"\bLP\b", r"Lebenspunkte", r"Verletzungsstufe",
        r"\b\d+/\d+\s*LP", r"leichte Wunde", r"schwere Wunde",
        r"kritisch verletzt",
    ],
    "hud-format": [
        r"`EP\s+\d+", r"`SC\s+\d+/\d+", r"PHASE\s+\w+\s+·\s+MODE",
    ],
    "save-template": [
        r'"v":\s*7', r"!save", r"Save-Template", r'"missions_completed"',
        r"Chargen-Save",
    ],
    "nullzeit-hub": [
        r"Briefing", r"Debrief", r"Nullzeit", r"HQ-Phase",
        r"PHASE\s+Briefing", r"PHASE\s+Debrief", r"Briefingraum",
    ],
    "px-progression": [
        r"\bPx\s*\d", r"Lvl\s*\d", r"Level-Up", r"Levelup",
    ],
    "kampfrunde": [
        r"Initiative", r"Kampfrunde", r"Angriffsprobe", r"Schaden\s+\d+",
        r"Aktionstempo", r"Trefferzone",
    ],
    "fraktionen": [
        r"Chronopolis", r"Tempocom", r"Arcana", r"Symbios",
        r"Dissident", r"Orbit-Konglomerat", r"IA-Transfer",
    ],
    "kb-retrieval": [
        # Proxy: Wenn SL NSC-Namen, Ort-Details, spezifische Jahres-Fakten
        # nennt, die nicht im Core-MP stehen — spricht für KB-Hit
        r"im Jahr\s+\d{4}", r"Straßenlaterne", r"rieche nach",
    ],
}


# ─── Personas (fokussierter CoreOps-Squad) ───────────────────────────────────
PERSONAS: dict[str, dict] = {
    "sarah": {
        "real_name": "Sarah", "char_name": "Mara Voss", "callsign": "SPLINTER",
        "system": textwrap.dedent("""\
            Du bist Sarah, 34, Marketing-Angestellte. Zweite ZEITRISS-Session.

            CHARAKTER: Mara Voss, Callsign SPLINTER. Infiltration & Spurenanalyse.
            Attribute: GES 5, INT 5, TEMP 4, SOC 3, STR 3, WIS 3.
            Talent: Tatortanalyse (+2 auf INT-Proben).
            Ausrüstung: Dienstpistole, Kevlarweste, Handscanner, Multitool,
            Comlink, 2x Rauchgranate.

            SPIELVERHALTEN:
            - Kennst Mechanik, fragst bei Unklarheit ("war das +2 auf INT?")
            - Ernste Rolle, gelegentlich trockener Humor
            - Taktisch, aber nicht optimiert
            - Gibst Voss eine Stimme ("Voss sagt ruhig: …")
            - Speicherst nach Debrief (!save)

            Antworte NUR mit dem was Sarah tippt (1-4 Sätze). Kein Meta.
        """),
    },
    "jonas": {
        "real_name": "Jonas", "char_name": None, "callsign": None,
        "system": textwrap.dedent("""\
            Du bist Jonas, 29, Softwareentwickler. Zweite ZEITRISS-Session
            (Squad hat 1 Mission hinter sich — du spielst jetzt fortgesetzt).

            CHARAKTER: Dein Char vom letzten Mal. Wenn nicht gegeben: Nahkampf-
            orientiert (STR 5, GES 4, TEMP 4, INT 3, SOC 2, WIS 3), Talent
            "Nahkampf-Taktik".

            SPIELVERHALTEN:
            - Kennst P&P (DSA, SR), vergleichst manchmal
            - Spielst regelkonform, fragst bei Modifikatoren nach
            - Vertraust Sarah bei Unklarheiten
            - Mittel-lange Antworten (2-5 Sätze)

            Antworte NUR mit dem was Jonas tippt.
        """),
    },
    "kim": {
        "real_name": "Kim", "char_name": "Ines Delacroix", "callsign": "MOTH",
        "system": textwrap.dedent("""\
            Du bist Kim, 26, Barista. Zweite ZEITRISS-Session.

            CHARAKTER: Ines Delacroix, Callsign MOTH. **Psioniker-Build.**
            Attribute: TEMP 5 (wichtig für PP-Pool!), INT 5, CHA 4, GES 3, STR 2, WIS 4.
            Talente: Telepathie (Basis), Prekognition (Basis).
            PP-Pool: TEMP 5 -> ca. 4-5 PP.
            Ausrüstung: Comlink, Neuralnet-Kontaktlinsen, Multitool, Adrenalin-
            Regulator, kein Schwergewehr (Glaskanone).

            SPIELVERHALTEN:
            - Anfänger, aber hast Basics mitgenommen
            - Fragst bei Mechanik nach ("wieviel PP kostet das?", "war das TEMP oder INT?")
            - NUTZT AKTIV Psi-Talente! Mindestens 1x pro Szene eine Telepathie-
              oder Prekognition-Probe anbieten, wenn situativ sinnvoll ("kann ich
              mental seine Stimmung lesen?", "kurze Prekog auf die Tür?").
            - SYS-bewusst (Psi-Last ist relevant).
            - Impulsive Aktionen, Story wichtiger als Mechanik
            - Lachst wenn was schiefgeht
            - Kurze Antworten (1-3 Sätze)

            Antworte NUR mit dem was Kim tippt.
        """),
    },
}

# ─── Szenario ──────────────────────────────────────────────────────────────────
# Stop-Hints sind gefährlich: Die SL erwähnt Regel-Begriffe auch während
# Gesprächen ("Chargen-Save", "eine Mission abgeschlossen" im Char-Sheet).
# Deshalb: HUD-Phase-Tracking. Ein Stop-Hint gilt nur als Endzeichen, wenn
# wir vorher in der Einsatz-Phase waren (SC ≥ 10 gesehen ODER PHASE Debrief
# als Abschnittsüberschrift, nicht Fließtext).
STOP_PATTERNS = [
    # HUD-Marker für Szenen-Ende (Mission Core=12, Rift=14)
    re.compile(r'^SC\s+1[2-4]/1[2-4]\s*$', re.MULTILINE),
    # PHASE Debrief nur als Abschnittsüberschrift (## oder ### am Zeilenanfang)
    re.compile(r'^#{1,3}\s+PHASE\s+Debrief\b', re.MULTILINE | re.IGNORECASE),
    # Explizite Mission-Ende-Trigger
    re.compile(r'^!save\s+nach\s+Debrief', re.MULTILINE),
]

# Kein vordefiniertes Ziel — Flo will sehen, wie KI-SL eine Core-Mission
# organisch generiert, nachdem vordefinierte Missionen aus dem MP raus sind.
SCENARIO = {
    "name": f"coreops-verify-psi-{time.strftime('%H%M')}",
    "description": "CoreOps Tier-1, Verification-Run nach PR #2963. PSI-Kim. MP-Nutzung getrackt.",
    "players": ["jonas", "kim", "sarah"],
    "opening": textwrap.dedent("""\
        Spiel starten (gruppe klassisch). Wir sind 3 Spieler:
        - Sarah bringt Mara Voss (SPLINTER): GES 5, INT 5, TEMP 4, SOC 3, STR 3, WIS 3, Talent Tatortanalyse.
        - Jonas bringt Ren Kaspar (RAMPART): STR 5, GES 4, TEMP 4, INT 3, SOC 2, WIS 3, Talent Nahkampf-Taktik.
        - Kim spielt **Psioniker-Build** Ines Delacroix (MOTH): TEMP 5, INT 5, CHA 4, GES 3, STR 2, WIS 4, Talente Telepathie + Prekognition.

        Briefing bitte. Core-Mission, Tier 1, Tempocom-Auftrag.
        Bitte keine Kürzung des Debriefs am Ende — voller Score-Screen, Level-Up-Wahl und !save wichtig.
    """).strip(),
}


# ─── API helpers ──────────────────────────────────────────────────────────────
def _post(path: str, body: dict, timeout: int = SL_TIMEOUT) -> dict:
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
    except (urllib.error.URLError, TimeoutError) as e:
        raise RuntimeError(f"Network/Timeout: {e}") from e


def sl_turn(messages: list[dict]) -> tuple[str, int, int, float]:
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
    p = PERSONAS[persona_key]
    context = (
        f"Die KI-Spielleitung schreibt gerade:\n\n---\n{sl_text[:4000]}\n---\n\n"
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
        timeout=PLAYER_TIMEOUT,
    )
    return resp["choices"][0]["message"]["content"].strip()


# ─── Session ──────────────────────────────────────────────────────────────────
class PlaytestSession:
    def __init__(self, scenario: dict, max_turns: int):
        self.sc = scenario
        self.max_turns = max_turns
        self.out: Path = OUT_ROOT / f"{STAMP}-{scenario['name']}"
        self.out.mkdir(parents=True, exist_ok=True)
        self.log_path = self.out / "_live.log"
        self.report_path = self.out / "_bericht.md"
        self.tokens_csv = self.out / "_tokens.csv"
        self.mp_track_csv = self.out / "_mp-sections.csv"
        self.sl_history: list[dict] = []
        self.turn = 0
        self.total_prompt = 0
        self.total_completion = 0
        self.findings: list[str] = []
        self.token_log: list[dict] = []
        self.section_hits: dict[str, int] = {k: 0 for k in MP_SECTIONS}

        self.tokens_csv.write_text(
            "turn,prompt_tokens,completion_tokens,total_tokens,cum_tokens,latency_s,sl_reply_chars\n",
            encoding="utf-8",
        )
        self.mp_track_csv.write_text(
            "turn," + ",".join(MP_SECTIONS.keys()) + "\n",
            encoding="utf-8",
        )

        self.report_path.write_text(
            f"# CoreOps-Playtest: {scenario['name']}\n\n"
            f"**Datum:** {time.strftime('%Y-%m-%d %H:%M')}\n"
            f"**Szenario:** {scenario['description']}\n"
            f"**Modell SL:** {SL_MODEL} via KB `{KB_ID[:8]}...`\n"
            f"**Modell Spieler:** {PLAYER_MODEL}\n"
            f"**Ziel:** MP-Usage-Tracking für Straffungs-Entscheidung\n\n---\n\n",
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
        if '"v":' in sl_text and '"v": 7' not in sl_text and '"v":7' not in sl_text:
            self.finding("SAVE-SCHEMA", "Save ohne v:7")
        if re.search(r'\bHP\b', sl_text) and 'LP' not in sl_text:
            self.finding("TERMINOLOGIE", "SL nutzt 'HP' statt 'LP'")
        m = re.search(r'W10.*Attribut\s+(\d+)', sl_text, re.IGNORECASE)
        if m and int(m.group(1)) < 11:
            self.finding("W10-SCHWELLE", f"W10-Halluzination bei Attribut {m.group(1)}")

    def _track_mp_sections(self, sl_text: str) -> dict[str, int]:
        """Zähle MP-Sektion-Trigger in dieser SL-Antwort."""
        hits_this_turn = {}
        for section, patterns in MP_SECTIONS.items():
            count = sum(
                len(re.findall(p, sl_text, re.IGNORECASE)) for p in patterns
            )
            hits_this_turn[section] = count
            self.section_hits[section] += count
        return hits_this_turn

    def run(self):
        sc = self.sc
        players = sc["players"]
        self.log(f"=== START: {sc['name']} ===")
        self.log(f"Spieler: {players}, Max turns: {self.max_turns}")

        opening_msg = sc["opening"]
        self.log(f">>> GRUPPE: {opening_msg[:120]}")
        self.append_report(f"## Turn 0 — Gruppenstart\n\n**GRUPPE:** {opening_msg}")
        self.sl_history.append({"role": "user", "content": opening_msg})

        for turn_num in range(self.max_turns):
            self.turn = turn_num + 1
            self.log(f"\n--- Turn {self.turn} ---")

            # v2.1: Progress-Log alle 5 Turns — verhindert gefühlten Stillstand
            if self.turn > 1 and self.turn % 5 == 0:
                self.log(f"=== Progress {self.turn}/{self.max_turns} ({100*self.turn//self.max_turns}%) · Prompt peak {self.total_prompt//self.turn} tok/turn avg ===")

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
            with self.tokens_csv.open("a", encoding="utf-8") as f:
                f.write(f"{self.turn},{pt},{ct},{pt + ct},{cum_total},{latency:.2f},{len(sl_text)}\n")
            self.token_log.append({
                "turn": self.turn, "prompt": pt, "completion": ct,
                "cum": cum_total, "latency_s": round(latency, 2),
            })

            # MP-Tracking
            hits = self._track_mp_sections(sl_text)
            with self.mp_track_csv.open("a", encoding="utf-8") as f:
                f.write(f"{self.turn}," + ",".join(str(hits[k]) for k in MP_SECTIONS) + "\n")

            if pt > 180_000 and not any("CTX-PREMIUM" in fi for fi in self.findings):
                self.finding("CTX-PREMIUM", f"Prompt {pt} tokens — ab 200K Premium-Pricing")

            self.sl_history.append({"role": "assistant", "content": sl_text})
            self._check_quality(sl_text)

            turn_file = self.out / f"turn-{self.turn:03d}-sl.md"
            turn_file.write_text(f"# Turn {self.turn} — SL\n\n{sl_text}\n", encoding="utf-8")
            self.append_report(f"### Turn {self.turn} — SL\n\n{sl_text[:2000]}")

            # Stop-Gate: HUD-Phase-Pattern (Regex auf Zeilenanfang, nicht Fliesstext)
            for pat in STOP_PATTERNS:
                m = pat.search(sl_text)
                if m:
                    self.log(f"🛑 Stop-Pattern: '{m.group(0)[:50]}'")
                    self._finalize(reason=f"Stop-Pattern: {m.group(0)[:60]}")
                    return

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
                combined_parts.append(f"**{char}** [{PERSONAS[p]['real_name']}]: {p_text}")

            combined = "\n\n".join(combined_parts)
            self.append_report(f"**SPIELER-EINGABEN:**\n\n{combined}")
            self.sl_history.append({"role": "user", "content": combined})
            time.sleep(1)

        self._finalize(reason="max_turns erreicht")

    def _finalize(self, reason: str = ""):
        self.log(f"\n=== ENDE: {reason} ===")
        peak_prompt = max((t["prompt"] for t in self.token_log), default=0)
        avg_latency = (
            sum(t["latency_s"] for t in self.token_log) / len(self.token_log)
            if self.token_log else 0.0
        )

        # MP-Sektion-Ranking (nach Total-Hits)
        ranked = sorted(self.section_hits.items(), key=lambda x: -x[1])
        mp_summary = "\n".join(
            f"- **{name}**: {count} hits"
            + (" 🔥" if count > 10 else " ✅" if count > 0 else " 💤 (nie getriggert!)")
            for name, count in ranked
        )

        summary = (
            f"## Zusammenfassung\n\n"
            f"**Ende-Grund:** {reason}\n"
            f"**Turns:** {self.turn}\n"
            f"**Tokens gesamt:** {self.total_prompt + self.total_completion}\n"
            f"**Peak Prompt:** {peak_prompt} tokens\n"
            f"**Ø Latenz pro Turn:** {avg_latency:.1f}s\n\n"
            f"### MP-Sektion-Nutzung\n\n{mp_summary}\n\n"
            f"**CSV-Files:**\n"
            f"- Tokens: `{self.tokens_csv.name}`\n"
            f"- MP-Sections pro Turn: `{self.mp_track_csv.name}`\n\n"
            f"### Findings ({len(self.findings)})\n"
        )
        summary += "\n".join(f"- {f}" for f in self.findings) if self.findings else "- keine"
        self.append_report(summary)
        self.log(f"📊 Report: {self.report_path}")
        self.log(f"📉 Tokens peak: {peak_prompt}")
        self.log(f"🧩 MP-Sections dormant: {sum(1 for _, c in ranked if c == 0)}/{len(ranked)}")


# ─── PID + Signal handling ────────────────────────────────────────────────────
def cleanup_pid():
    try:
        if PID_FILE.exists():
            PID_FILE.unlink()
    except Exception:
        pass

def write_pid():
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(os.getpid()))
    atexit.register(cleanup_pid)
    def _sig(signum, frame):
        cleanup_pid()
        sys.exit(130)
    signal.signal(signal.SIGTERM, _sig)
    signal.signal(signal.SIGINT, _sig)


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="ZEITRISS CoreOps Harness v2.1 (PSI-Kim Verification)")
    parser.add_argument("--turns", type=int, default=40, help="Max turns (default 40 for focused verification)")
    args = parser.parse_args()

    write_pid()

    print(f"\n🎮 ZEITRISS CoreOps-Harness v2.0 (MP-Tracking)")
    print(f"Target: {BASE_URL} · KB: {KB_ID[:8]}... · SL: {SL_MODEL}")
    print(f"Szenario: {SCENARIO['description']}")
    print(f"Max Turns: {args.turns}\n")

    session = PlaytestSession(SCENARIO, args.turns)
    try:
        session.run()
    except KeyboardInterrupt:
        session._finalize(reason="Abgebrochen (Ctrl+C)")


if __name__ == "__main__":
    main()
