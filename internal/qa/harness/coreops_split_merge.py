#!/usr/bin/env python3
"""
ZEITRISS CoreOps-Split/Merge-Harness (2026-06-17)
=================================================
ORGANISCHER Lauf über echte CoreOps-Missionen hinweg — testet die
Split/Merge-Speichermechanik im Spielfluss, NICHT nur als gescripteten
Mechanik-Canary (das ist split_merge.py).

Roter Faden (Flos Vorgabe 2026-06-17):
  - 5er-Crew spielt EINE CoreOps-Mission zusammen.
  - Teilt sich danach am HQ-Sync-Punkt 3/2 auf.
  - 3er und 2er spielen JE eine eigene CoreOps-Mission (getrennte Chats).
  - Treffen sich wieder im HQ (Merge) — KEINE weitere Mission, nur Merge prüfen.
  - KEIN Rift, KEIN Chronopolis, KEINE Arena (bewusst rausgehalten).

Architektur-Trick (warum Tokens unkritisch sind):
  Jeder Spielabschnitt ist ein FRISCHER OWUIChat -> eigenes SL-Token-Fenster.
  Der Save wird zwischen Abschnitten als JSON gepastet (Browser-Handover).
  Nur die Personas sind stateless (eigener Call je Turn) -> kein Fenster-Druck.

Validierung:
  - merge_assert.validate_export auf jeden !save
  - merge_assert.assert_merge auf das Merge-Ergebnis (Anker-Priorität,
    Echo-Dedup, Seed-Cap, Wallet-Konservierung)
  - Pflichtbeats (Split-Beat, Rejoin-Beat, Kontinuitätsrückblick) via Heuristik

Aufruf:
  set -a; . ~/.openwebui_env; set +a
  python3 harness/coreops_split_merge.py [--smoke] [--max-turns-mission 30]

  --smoke: nur Pipeline-Struktur prüfen (Load -> 1 Mission-Turn -> Save-Zwang
           im 5er-Abschnitt), KEIN voller Lauf. Billig, ~1-2 SL-Turns.

Env: OPENWEBUI_URL, OPENWEBUI_API_KEY
"""
from __future__ import annotations
import argparse
import json
import os
import re
import signal
import sys
import textwrap
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from owui_client import OWUIChat, stateless_completion  # noqa: E402
import merge_assert as MA  # noqa: E402

# ─── Config ───────────────────────────────────────────────────────────────────
BASE_URL = os.environ.get("OPENWEBUI_URL", "http://127.0.0.1:8080")
API_KEY = os.environ.get("OPENWEBUI_API_KEY", "")
SL_MODEL = "zeitriss-v426-uncut"
PLAYER_MODEL = "anthropic/claude-sonnet-4.6"
KB_ID = "a56706c9-e427-4c6c-9dcb-0eb7cea095c0"
TIMEOUT_SL = 420
TIMEOUT_PERSONA = 60
SL_TEXT_CAP = 16000
ROLL_SUMMARY_TURNS = 6

REPO = Path("/mnt/agent_share/cloud/repos/ZEITRISS-md-git")
ANCHOR_FIXTURE = REPO / "internal" / "qa" / "fixtures" / "savegame_v7_5er_hq_highlevel.json"

HOME = Path(os.path.expanduser("~"))
PLAYTESTS = HOME / ".openclaw" / "workspace-cloud" / "playtests" / "zeitriss"
RUNNING_DIR = HOME / ".openclaw" / "workspace-cloud" / "tmp" / "running"
RUNNING_DIR.mkdir(parents=True, exist_ok=True)

# Partition: welche Anker-Char-IDs in welcher Branch-Gruppe.
# A=Astra/ECHO, B=Blitz/STORM, C=Cipher/GHOST, D=Dusk/VEIL, E=Echo/RELAY
GROUP_3ER = ["AGENT-A", "AGENT-B", "AGENT-C"]   # Astra(Lead)/Blitz(Front)/Cipher(Hack)
GROUP_2ER = ["AGENT-D", "AGENT-E"]              # Dusk(Recon)/Echo(Support)

# ─── Personas (5 Anker-Crew, missions-getunt) ─────────────────────────────────
# Mappen auf die fixen Anker-Charaktere. Anders als group-harness PHASE3 sind
# sie hier NICHT wallet-geflavored, sondern auf Missionsspiel + Save-/Split-
# Compliance getunt. Jede Persona kennt ihren Char + ihre Rolle.
_COMMON = (
    "\n\nWICHTIG: Antworte NUR mit dem, was du in den Chat tippst — keine Regie, "
    "kein Meta-Kommentar, keine Anführungszeichen drumrum. 1-3 Sätze, in-character.\n"
    "Wenn du gerade NICHTS beizutragen hast, antworte exakt mit: (hört zu)\n"
    "Wenn die KI-SL zum Speichern (!save) oder Chat-Wechsel auffordert, folgst du dem prompt."
)
PERSONAS: dict[str, dict] = {
    "astra": {
        "real_name": "Petra", "char_name": "Astra", "callsign": "ECHO", "char_id": "AGENT-A",
        "system": "Du bist Petra, erfahrene P&P-Spielerin und inoffizielle Anführerin. "
                  "Du spielst Astra (ECHO), Analytik & Spurensicherung — ruhig, taktisch, "
                  "denkst ans Team, triffst Entscheidungen wenn die Gruppe zögert. Du gibst "
                  "Astra eine ruhige, bestimmte Stimme." + _COMMON,
    },
    "blitz": {
        "real_name": "Marco", "char_name": "Blitz", "callsign": "STORM", "char_id": "AGENT-B",
        "system": "Du bist Marco, spielst offensiv. Du spielst Blitz (STORM), CQB & "
                  "Sturmangriff — der Frontkämpfer. Du gehst voran, suchst die direkte "
                  "Lösung, drängst aufs Handeln. Raue, direkte Stimme." + _COMMON,
    },
    "cipher": {
        "real_name": "Lena", "char_name": "Cipher", "callsign": "GHOST", "char_id": "AGENT-C",
        "system": "Du bist Lena, detailverliebt. Du spielst Cipher (GHOST), Infiltration & "
                  "Hacking — du behältst den Überblick, scoutest, knackst Systeme, denkst "
                  "einen Zug voraus. Trockene, präzise Stimme." + _COMMON,
    },
    "dusk": {
        "real_name": "Tarek", "char_name": "Dusk", "callsign": "VEIL", "char_id": "AGENT-D",
        "system": "Du bist Tarek, vorsichtiger Taktiker. Du spielst Dusk (VEIL), Verdeckte "
                  "Aufklärung — erst Lage checken, dann handeln, ruhige Einschätzungen. "
                  "Leise, bedachte Stimme." + _COMMON,
    },
    "echo_p": {
        "real_name": "Sven", "char_name": "Echo", "callsign": "RELAY", "char_id": "AGENT-E",
        "system": "Du bist Sven, Teamplayer. Du spielst Echo (RELAY), Support & Feldtechnik — "
                  "Logistik, Verbrauchsmaterial, hältst die Gruppe zusammen, sicherst ab. "
                  "Warme, sachliche Stimme." + _COMMON,
    },
}
ID2KEY = {p["char_id"]: k for k, p in PERSONAS.items()}

# ─── Save-Extraktion ──────────────────────────────────────────────────────────
def extract_all_saves(text: str) -> list[dict]:
    out: list[dict] = []
    seen: set[str] = set()
    for m in re.finditer(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL):
        obj = _try_v7(m.group(1))
        if obj is not None:
            key = obj.get("save_id") or json.dumps(obj, sort_keys=True)[:80]
            if key not in seen:
                seen.add(key)
                out.append(obj)
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


# ─── Save-Zwang (Prosa-statt-JSON eskalieren) ─────────────────────────────────
_SAVE_PROSE_RE = re.compile(
    r"(gespeichert|speicherstand|speicher-stand|save\s+erstellt|abgespeichert|"
    r"stand gesichert|gesichert\b|!save ausgef|saved)", re.IGNORECASE)
_SAVE_ESCALATION = [
    "!save",
    ("Bitte gib den Speicherstand JETZT als vollständigen v7-JSON-Block aus, "
     "eingefasst in ```json ... ```. Kein Fließtext, nur der JSON-Block."),
    ("SYSTEM/Testharness: Der vorige Output enthielt KEINEN maschinenlesbaren "
     "Speicherstand. Gib ausschließlich den kompletten v7-Save als EINEN "
     "```json-Codeblock aus. Beginne direkt mit ```json."),
]


def claims_save_in_prose(text: str) -> bool:
    return bool(_SAVE_PROSE_RE.search(text)) and not extract_all_saves(text)


# ─── Level-Up-Sperre (Reihenfolge-Pflicht: Wahl vor !save) ─────────────────────
# Die SL verweigert den Save korrekt (SaveGuard/§F/§I), solange Charaktere offene
# Level-Up-Wahlen ("AUSSTEHEND") haben. Der Harness muss diese Wahlen beantworten,
# bevor er den Save erneut fordert — sonst rennt jeder Save-Zwang ins Leere.
_LEVELUP_BLOCK_RE = re.compile(
    r"(level-?up-?wahl|level-?up-?wahlen|wahl(en)? (noch )?(aus|ausstehend)|"
    r"ausstehend|save (ist )?gesperrt|reihenfolge-?pflicht)", re.IGNORECASE)
# Callsigns + zugehöriges Level aus dem Sperrtext ziehen, z.B. "ECHO (Lvl 914)"
# oder "ECHO/STORM/GHOST" oder "**ECHO / Astra** — wähle".
_CALLSIGN_LVL_RE = re.compile(r"\b([A-ZÄÖÜ]{3,8})\b(?:[^\n]{0,30}?Lvl\s*(\d+))?")


def pending_levelup_resolution(text: str, known_callsigns: set[str]) -> str | None:
    """Erkennt eine Level-Up-Sperre und baut eine Antwort, die für jeden betroffenen
    Charakter eine sinnvolle Default-Wahl (+1 SYS, in jeder Option-Liste angeboten)
    einträgt. Gibt None zurück, wenn keine Sperre erkennbar ist."""
    if not _LEVELUP_BLOCK_RE.search(text):
        return None
    # Betroffene Callsigns: alle bekannten, die im Sperr-Text auftauchen.
    hits: list[tuple[str, str]] = []
    seen: set[str] = set()
    for m in _CALLSIGN_LVL_RE.finditer(text):
        cs, lvl = m.group(1), m.group(2)
        if cs in known_callsigns and cs not in seen:
            seen.add(cs)
            hits.append((cs, lvl or ""))
    if not hits:
        return None
    lines = []
    for cs, lvl in hits:
        tag = f"{cs} (Lvl {lvl})" if lvl else cs
        # +1 SYS ist in den Option-Listen aller Chargen-Klassen vertreten und ein
        # neutraler, schema-konformer Default für einen Testharness.
        lines.append(f"> {tag}: +1 SYS")
    body = "\n".join(lines)
    return (
        "Trage für jeden Charakter mit offener Level-Up-Wahl die folgende Wahl ein "
        "(Testharness-Default, schema-konform), dann gib den vollständigen v7-JSON-"
        "Save aus:\n\n" + body +
        "\n\nDanach: vollständiger !save als EIN ```json-Codeblock, ohne weiteren Fließtext."
    )


# ─── Pflichtbeat-Heuristik ────────────────────────────────────────────────────
def detect_beats(text: str) -> dict[str, bool]:
    t = text.lower()
    return {
        "split_beat": bool(re.search(
            r"\b(teilt? euch|aufteil|split|getrennte wege|trennt euch|"
            r"zwei (gruppen|teams|threads|branches)|spaltet|family_id)", t)),
        "rejoin_beat": bool(re.search(
            r"\b(wieder (zusammen|vereint)|rückkehr|kehrt? zurück|treffen euch|"
            r"zusammenführ|rejoin|andocken|heimkehr|konvergenz|vereint)", t)),
        "continuity_recap": bool(re.search(
            r"\b(session-?anker|kontinuität|rückblick|rückkehrer|nachwirkung|"
            r"konvergenz)", t)),
    }


# HQ/Debrief-Marker: Mission gilt als bei einem savebaren HQ-Zustand angekommen.
_HQ_SAVE_RE = re.compile(
    r"(hq-stand stabil|deepsave möglich|deepsave moeglich|mission abgeschlossen|"
    r"debrief|!save für|!save fuer|sync vor übergang|hq-menü|hq-menu|sync empfohlen)",
    re.IGNORECASE)


def at_hq_savepoint(text: str) -> bool:
    return bool(_HQ_SAVE_RE.search(text))


# ─── Run-Logging ──────────────────────────────────────────────────────────────
class Run:
    def __init__(self, tag: str):
        stamp = time.strftime("%Y-%m-%d-%H%M")
        self.out = PLAYTESTS / "runs" / f"{stamp}-coreops-split-merge{('-' + tag) if tag else ''}"
        self.out.mkdir(parents=True, exist_ok=True)
        self.saves_dir = self.out / "saves"
        self.saves_dir.mkdir(exist_ok=True)
        self.log_path = self.out / "_live.log"
        self.report = self.out / "_transkript.md"
        self.jsonl = self.out / "turns.jsonl"
        self.cum_cost = 0.0
        self.peak_prompt = 0
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
        self.peak_prompt = max(self.peak_prompt, ptok)
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

    def finding(self, code: str, severity: str, msg: str, phase: str = ""):
        f = MA.Finding(code, severity, msg)
        self.findings.append(f)
        sev = {"FAIL": "❌", "SOFT": "⚠️", "INFO": "ℹ️"}.get(severity, "·")
        self.log(f"  {sev} [{phase}] {code}: {msg}")
        self.rep(f"> {sev} **[{phase}] {code}:** {msg}")


# ─── SL-Turn ──────────────────────────────────────────────────────────────────
def sl_say(run: Run, sl: OWUIChat, user_text: str, phase: str, label: str) -> str:
    run.turn += 1
    run.log(f">>> [{phase}] {label}")
    run.rep(f"**Eingabe [{phase}]:** {label}")
    res = sl.say(user_text)
    txt = res["content"]
    run.account(res["usage"])
    src = sl.source_files()
    cache = run.cache_hits[-1] if run.cache_hits else 0
    run.log(f"<<< [{phase}] SL ({len(txt)} chars, {res['usage'].get('prompt_tokens',0)} ptok, "
            f"cache {cache:.0%}, RAG={len(src)}, cum ${run.cum_cost:.4f})")
    run.rep(f"### [{phase}] SL\n\n{txt}")
    run.jlog({"turn": run.turn, "phase": phase, "label": label, "sl": txt,
              "usage": res["usage"], "rag": src})
    return txt


def persona_turn(persona: dict, sl_text: str, roll_summary: str) -> str:
    ctx = ("Die KI-Spielleitung schreibt gerade folgendes in den Chat:\n\n"
           f"---\n{sl_text[:SL_TEXT_CAP]}\n---\n\n")
    if roll_summary:
        ctx += f"Was bisher in dieser Mission geschah (Kurzverlauf):\n{roll_summary}\n\n"
    ctx += "Was tippst du jetzt in den Chat?"
    return stateless_completion(
        BASE_URL, API_KEY, PLAYER_MODEL,
        system=persona["system"], user=ctx,
        temperature=0.9, max_tokens=300, timeout=TIMEOUT_PERSONA)


_ALL_CALLSIGNS = {p["callsign"] for p in PERSONAS.values()}
_MAX_LEVELUP_RESOLVE = 2  # gegen Endlos-Schleife bei hartnäckiger Sperre


def request_save(run: Run, sl: OWUIChat, phase: str, want: int = 1,
                 seed_text: str = "") -> list[dict]:
    last = sl.history[-1]["content"] if sl.history else ""
    acc = (seed_text + "\n" + last) if seed_text else last
    saves = extract_all_saves(acc)
    prose_seen = False
    levelup_resolved = 0
    for stage, prompt in enumerate(_SAVE_ESCALATION, start=1):
        if len(saves) >= want:
            break
        # Vor der nächsten Eskalation: blockt eine Level-Up-Sperre den Save?
        # Dann erst die Wahlen auflösen, sonst läuft jede Eskalation ins Leere.
        if levelup_resolved < _MAX_LEVELUP_RESOLVE:
            resolution = pending_levelup_resolution(acc, _ALL_CALLSIGNS)
            if resolution:
                levelup_resolved += 1
                run.log(f"  🎓 [{phase}] Level-Up-Sperre erkannt -> Default-Wahlen "
                        f"eintragen (Auflösung {levelup_resolved})")
                txt = sl_say(run, sl, resolution, phase,
                             f"[Level-Up-Wahl {levelup_resolved}]")
                acc += "\n" + txt
                saves = extract_all_saves(acc)
                if len(saves) >= want:
                    break
        if claims_save_in_prose(acc):
            prose_seen = True
            run.log(f"  ⚠️ [{phase}] Save in Prosa, kein JSON -> Eskalation {stage}")
        txt = sl_say(run, sl, prompt, phase, f"[Save-Zwang {stage}/{len(_SAVE_ESCALATION)}]")
        acc += "\n" + txt
        saves = extract_all_saves(acc)
    if prose_seen and saves:
        run.finding("SAVE-PROSE", "SOFT", f"{phase}: Save erst nach Eskalation als JSON", phase)
    elif prose_seen and not saves:
        run.finding("SAVE-PROSE", "FAIL", f"{phase}: kein JSON trotz Eskalation", phase)
    return saves


def validate_and_store(run: Run, save: dict, name: str, phase: str) -> MA.Result:
    sp = run.saves_dir / f"{name}.json"
    sp.write_text(json.dumps(save, ensure_ascii=False, indent=2))
    run.log(f"  💾 Save '{name}' (mode={save_mode(save)}, "
            f"{len(save.get('characters', []))} chars) -> {sp.name}")
    res = MA.validate_export(save, name)
    res.merge(MA.check_echo_formats(save, name))
    res.merge(MA.check_seed_cap(save, name))
    run.add_findings(res, phase)
    return res


# ─── Eine CoreOps-Mission organisch spielen ───────────────────────────────────
def play_mission(run: Run, load_save: dict, persona_keys: list[str], section: str,
                 max_turns: int, briefing_steer: str) -> dict | None:
    """Lädt einen Save in einen frischen Chat, fährt eine CoreOps-Mission mit den
    angegebenen Personas bis zu einem savebaren HQ-Zustand, gibt den Ergebnis-Save
    zurück (oder None). Eigenes Token-Fenster pro Mission (frischer OWUIChat)."""
    chat = OWUIChat(BASE_URL, API_KEY, SL_MODEL, kb_id=KB_ID, timeout=TIMEOUT_SL)
    run.log(f"=== {section} — Chat {chat.chat_id} ({len(persona_keys)} Personas: "
            f"{[PERSONAS[k]['callsign'] for k in persona_keys]}) ===")
    run.rep(f"## 🗂 {section} — Chat {chat.chat_id}\n")

    load_msg = "Spiel laden:\n\n```json\n" + json.dumps(load_save, ensure_ascii=False) + "\n```"
    txt = sl_say(run, chat, load_msg, section, "[Save laden]")

    # Briefing/Mission anstoßen
    txt = sl_say(run, chat, briefing_steer, section, "[Briefing -> Mission starten]")

    history_lines: list[str] = []

    def roll_summary() -> str:
        return "\n".join(history_lines[-ROLL_SUMMARY_TURNS:])

    # Schwelle, ab der die Crew aktiv Richtung Exfil/Abschluss geschubst wird,
    # damit die Mission verlässlich einen HQ-Savepoint erreicht (Save geht NUR
    # im HQ — Mid-Mission-Save blockt der SaveGuard korrekt).
    push_from = max(4, int(max_turns * 0.6))
    reached_hq = False
    for i in range(max_turns):
        # HQ-Savepoint erreicht? (kommt erst ab Exfil -> Debrief -> HQ)
        if at_hq_savepoint(txt) and run.turn > 3:
            run.log(f"  🏁 [{section}] HQ-Savepoint-Marker erkannt -> Mission-Ende-Save")
            reached_hq = True
            break

        nudge = ""
        if i >= push_from:
            nudge = ("\n\n(Spielleitung-Hinweis vom Testrahmen an die Crew: Bringt die "
                     "Mission jetzt zum Abschluss — Ziel sichern, Exfil einleiten und "
                     "zurück ins HQ, damit der Einsatz sauber im Debrief endet.)")

        # Personas antworten (gebündelt)
        parts = []
        for k in persona_keys:
            try:
                pt = persona_turn(PERSONAS[k], txt + nudge, roll_summary())
            except Exception as e:  # noqa: BLE001
                run.finding("PERSONA-ERROR", "SOFT", f"{k}: {str(e)[:120]}", section)
                pt = "(hört zu)"
            cn = PERSONAS[k]["char_name"]
            stripped = pt.strip().lower()
            run.rep(f"**{cn} [{PERSONAS[k]['real_name']}]:** {pt}")
            history_lines.append(f"{cn}: {pt}")
            if stripped in ("(hört zu)", "(hoert zu)", "(keine eingabe)", ""):
                continue
            parts.append(f"**{cn} [{PERSONAS[k]['real_name']}]**: {pt}")
        if not parts:
            parts.append("(Die Crew wartet ab — mach weiter.)")
        combined = "\n\n".join(parts)
        if i >= push_from:
            combined += ("\n\n(Die Crew strebt jetzt zum Exfil und zurück ins HQ, "
                         "um den Einsatz abzuschließen.)")
        run.jlog({"turn": run.turn, "phase": section, "players": combined})

        try:
            txt = sl_say(run, chat, combined, section, "[Crew-Eingaben]")
        except Exception as e:  # noqa: BLE001
            run.finding("SL-ERROR", "FAIL", f"{section}: {str(e)[:160]}", section)
            return None
        time.sleep(0.5)

    if not reached_hq:
        # KEIN Save erzwingen ohne HQ — der SaveGuard würde (korrekt) blocken.
        # Das ist ein Mission-Pacing-/Budget-Problem, kein Save-Bug.
        run.finding("MISSION-INCOMPLETE", "FAIL",
                    f"{section}: kein HQ-Savepoint nach {max_turns} Turns "
                    f"(Mission nicht bis Debrief/HQ gespielt — mehr Turn-Budget nötig)", section)
        return None

    # Am HQ-Savepoint: jetzt greift !save sauber.
    saves = request_save(run, chat, section, want=1)
    if not saves:
        run.finding("SECTION-SAVE", "FAIL", f"{section}: kein Ergebnis-Save am HQ", section)
        return None
    result = saves[0]
    validate_and_store(run, result, f"{section.lower().replace(' ', '-')}-result", section)
    return result


# ─── Split am Sync-Punkt: aus 5er-Save zwei Branch-Saves erzeugen ─────────────
def do_split(run: Run, group_save: dict, max_turns: int) -> tuple[dict | None, dict | None]:
    chat = OWUIChat(BASE_URL, API_KEY, SL_MODEL, kb_id=KB_ID, timeout=TIMEOUT_SL)
    run.log(f"=== SPLIT — Chat {chat.chat_id} ===")
    run.rep("## 🗂 Split (5er teilt sich 3/2 am HQ-Sync-Punkt)\n")

    load_msg = "Spiel laden:\n\n```json\n" + json.dumps(group_save, ensure_ascii=False) + "\n```"
    txt = sl_say(run, chat, load_msg, "SPLIT", "[5er-Stand laden]")
    if not detect_beats(txt)["continuity_recap"]:
        run.finding("RECAP", "SOFT", "Kein Kontinuitätsrückblick beim 5er-Load", "SPLIT")

    cs_3er = [PERSONAS[ID2KEY[i]]["callsign"] for i in GROUP_3ER]
    cs_2er = [PERSONAS[ID2KEY[i]]["callsign"] for i in GROUP_2ER]
    split_req = (
        f"Die Crew teilt sich am Sync-Punkt auf zwei Spuren auf: "
        f"Team Alpha ({'+'.join(cs_3er)}) verfolgt die eine Spur, "
        f"Team Bravo ({'+'.join(cs_2er)}) die andere. "
        "Leite den Split inworld ein und erstelle für JEDES Team einen eigenen "
        "Speicherstand (!save) mit gesetztem continuity.split (family_id, thread_id, "
        "expected_threads), damit wir sie in getrennten Chats weiterspielen. "
        "Gib beide Speicherstände als getrennte ```json-Blöcke aus."
    )
    txt2 = sl_say(run, chat, split_req, "SPLIT", "[3/2-Split + !save je Team]")
    if not detect_beats(txt2)["split_beat"]:
        run.finding("SPLIT-BEAT", "SOFT", "Kein expliziter Split-Beat erkannt", "SPLIT")

    saves = extract_all_saves(txt2)
    if len(saves) < 2:
        run.log(f"  … {len(saves)}/2 Branch-Saves, fordere getrennt nach")
        saves = request_save(run, chat, "SPLIT", want=2, seed_text=txt2)

    if len(saves) < 2:
        run.finding("SPLIT-SAVES", "FAIL", f"Split erzeugte {len(saves)}/2 Branch-Saves", "SPLIT")
        return None, None

    # größere Gruppe = 3er
    saves = sorted(saves, key=lambda s: -len(s.get("characters", [])))
    s3 = saves[0]
    s2 = saves[1]
    validate_and_store(run, s3, "split-team-alpha-3er", "SPLIT")
    validate_and_store(run, s2, "split-team-bravo-2er", "SPLIT")
    # Sanity: Char-Zahlen
    if len(s3.get("characters", [])) != 3:
        run.finding("SPLIT-PARTITION", "SOFT",
                    f"Team Alpha hat {len(s3.get('characters', []))} statt 3 Chars", "SPLIT")
    if len(s2.get("characters", [])) != 2:
        run.finding("SPLIT-PARTITION", "SOFT",
                    f"Team Bravo hat {len(s2.get('characters', []))} statt 2 Chars", "SPLIT")
    return s3, s2


# ─── Merge: beide Branch-Ergebnisse zurück zu 5er ─────────────────────────────
def do_merge(run: Run, branch_results: list[dict], anchor: dict) -> dict | None:
    chat = OWUIChat(BASE_URL, API_KEY, SL_MODEL, kb_id=KB_ID, timeout=TIMEOUT_SL)
    run.log(f"=== MERGE — Chat {chat.chat_id} ===")
    run.rep("## 🗂 Merge (beide Teams wieder zusammen im HQ — KEINE Mission)\n")
    blocks = "\n\n".join("```json\n" + json.dumps(s, ensure_ascii=False) + "\n```"
                         for s in branch_results)
    merge_msg = ("Spiel laden (Gruppe wieder zusammen):\n\n" + blocks +
                 "\n\nBeide Teams treffen sich wieder im HQ. Bitte führe die Stände "
                 "zusammen (Kontinuitätsrückblick beider Spuren) und erstelle danach "
                 "einen gemeinsamen Speicherstand (!save). Keine neue Mission.")
    txt = sl_say(run, chat, merge_msg, "MERGE", "[beide Branch-Saves laden + Merge]")
    beats = detect_beats(txt)
    if not beats["rejoin_beat"]:
        run.finding("REJOIN-BEAT", "SOFT", "Kein Rejoin-HQ-Beat erkannt", "MERGE")
    if not beats["continuity_recap"]:
        run.finding("MERGE-RECAP", "SOFT", "Kein Kontinuitätsrückblick beim Merge", "MERGE")

    saves = extract_all_saves(txt)
    if not saves:
        saves = request_save(run, chat, "MERGE", want=1)
    if not saves:
        run.finding("MERGE-SAVE", "FAIL", "Merge erzeugte keinen Save", "MERGE")
        return None
    merged = saves[0]
    validate_and_store(run, merged, "merge-result-5er", "MERGE")
    res = MA.assert_merge(merged, anchor, branch_results, label="merge")
    run.add_findings(res, "MERGE-ASSERT")
    analyze_thread_routing(run, merged, "ROUTING")
    return merged


# ─── Faden-Routing-Analyse (Fix #3235 Beweis) ─────────────────────────────────
# Ermittlungs-Hinweise (roter Faden) sollen NICHT als Einzel-Echos in
# shared_echoes landen, sondern in research.projects[] (scope:campaign) /
# summaries.summary_active_arcs. Rift-Seeds NICHT als shared_echo.
_INVESTIGATION_HINT_RE = re.compile(
    r"(funktion|amt|prozess|initialen|koordinate|depot|signatur|kontakt|"
    r"meridian|kairos|route|anker|verschwör|fraktion|identität)", re.IGNORECASE)


def analyze_thread_routing(run: Run, merged: dict, phase: str = "ROUTING") -> None:
    """Prüft nach dem Merge, ob der rote Faden korrekt geroutet wurde.
    Reines Reporting/Finding — kein Hard-Fail des Laufs an sich."""
    cont = merged.get("continuity", {}) or {}
    se = cont.get("shared_echoes", []) or []
    research = (merged.get("research", {}) or {}).get("projects", []) or []
    summ = (merged.get("summaries", {}) or {}).get("summary_active_arcs", "") or ""
    rift_seeds = (merged.get("campaign", {}) or {}).get("rift_seeds", []) or []

    # 1) Rift-Seed faelschlich als shared_echo?
    rift_echoes = [e for e in se if isinstance(e, dict)
                   and "rift" in str(e.get("tag", "")).lower()]
    if rift_echoes:
        run.finding("ROUTING-RIFT", "FAIL",
                    f"{len(rift_echoes)} Rift-Seed(s) faelschlich als shared_echo: "
                    f"{[e.get('tag') for e in rift_echoes]}", phase)
    else:
        run.finding("ROUTING-RIFT", "INFO", "Kein Rift-Seed in shared_echoes (korrekt)", phase)

    # 2) campaign-Echos in shared_echoes, die wie Ermittlungs-Hinweise aussehen
    #    (folgespur-* sind legitim — die bleiben laut Fix in shared_echoes).
    campaign_echoes = [e for e in se if isinstance(e, dict)
                       and e.get("scope") == "campaign"
                       and not str(e.get("tag", "")).startswith("folgespur-")]
    hint_like = [e for e in campaign_echoes
                 if _INVESTIGATION_HINT_RE.search(str(e.get("tag", "")) + " "
                                                  + str(e.get("text", "")))]
    if hint_like:
        run.finding("ROUTING-FADEN", "SOFT",
                    f"{len(hint_like)} Ermittlungs-Hinweis(e) noch als campaign-shared_echo "
                    f"(sollten in research/summary): {[e.get('tag') for e in hint_like]}", phase)
    else:
        run.finding("ROUTING-FADEN", "INFO",
                    "Keine hinweisartigen campaign-Einzel-Echos in shared_echoes", phase)

    # 3) Wurde der Faden ueberhaupt irgendwo abgelegt? (research/summary gefuellt?)
    run.log(f"  ℹ️ [{phase}] Faden-Ablage: research.projects={len(research)}, "
            f"summary_active_arcs={'gefüllt' if summ.strip() else 'leer'}, "
            f"shared_echoes={len(se)} (davon campaign-nonfolgespur={len(campaign_echoes)}), "
            f"rift_seeds={len(rift_seeds)}")
    run.rep(f"> ℹ️ **[{phase}] Faden-Ablage:** research.projects={len(research)}, "
            f"summary_active_arcs={'gefüllt' if summ.strip() else 'leer'}, "
            f"shared_echoes={len(se)} (campaign-nonfolgespur={len(campaign_echoes)}), "
            f"rift_seeds={len(rift_seeds)}")


# ─── Finalize ─────────────────────────────────────────────────────────────────
def finalize(run: Run, merged: dict | None):
    fails = [f for f in run.findings if f.severity == "FAIL"]
    softs = [f for f in run.findings if f.severity == "SOFT"]
    avg_cache = sum(run.cache_hits) / len(run.cache_hits) if run.cache_hits else 0
    verdict = "PASS" if not fails else "FAIL"
    summary = {
        "verdict": verdict, "turns": run.turn, "cost_usd": round(run.cum_cost, 4),
        "peak_prompt_tokens": run.peak_prompt, "avg_cache_hit": round(avg_cache, 3),
        "merge_save_captured": merged is not None,
        "fails": [str(f) for f in fails], "softs": [str(f) for f in softs],
    }
    (run.out / "_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    run.rep(f"\n---\n\n## Verdict: {verdict}\n\n"
            f"- Turns: {run.turn}\n- Kosten (echt, OWUI usage.cost): ${run.cum_cost:.4f}\n"
            f"- Peak Prompt-Tokens: {run.peak_prompt} ({run.peak_prompt/256_000:.1%} von 256k)\n"
            f"- Ø Cache-Hit: {avg_cache:.0%}\n"
            f"- Harte Fehler: {len(fails)} | Soft: {len(softs)}\n\n"
            + ("**FAILS:**\n" + "\n".join(f"- {f}" for f in fails) + "\n\n" if fails else "")
            + ("**SOFT:**\n" + "\n".join(f"- {f}" for f in softs) if softs else ""))
    run.log(f"=== ENDE === verdict={verdict} turns={run.turn} ${run.cum_cost:.4f} "
            f"peak={run.peak_prompt} cache={avg_cache:.0%} fails={len(fails)} softs={len(softs)}")
    print(f"\nVERDICT: {verdict}")
    print(f"SUMMARY: {run.out / '_summary.json'}")
    print(f"OUT_DIR: {run.out}")


BRIEFING_5ER = (
    "Die ganze Crew (alle 5) ist im HQ. Wir wollen jetzt eine neue CoreOps-Mission "
    "angehen — bitte Briefing für die nächste Core-Mission und dann rein in den Einsatz. "
    "Los geht's."
)
BRIEFING_BRANCH = (
    "Dieses Team will jetzt seine eigene CoreOps-Mission angehen — bitte Briefing "
    "für eine Core-Mission und dann rein in den Einsatz. Los."
)


def run_full(run: Run, max_mission: int):
    anchor = json.loads(ANCHOR_FIXTURE.read_text(encoding="utf-8"))
    run.rep(f"# CoreOps-Split/Merge — organischer Lauf\n\n"
            f"**Datum:** {time.strftime('%Y-%m-%d %H:%M')}  \n"
            f"**SL:** {SL_MODEL} (OWUI-RAG)  \n**Spieler:** {PLAYER_MODEL} (5 Personas)  \n"
            f"**Anker:** `{ANCHOR_FIXTURE.name}`\n\n"
            f"Flow: 5er-Mission → Split 3/2 → 3er-Mission + 2er-Mission → Merge (keine Mission)\n\n---\n")

    # 1) 5er-Mission
    all_keys = ["astra", "blitz", "cipher", "dusk", "echo_p"]
    s5 = play_mission(run, anchor, all_keys, "M1-5er", max_mission, BRIEFING_5ER)
    if not s5:
        run.finding("ABBRUCH", "FAIL", "5er-Mission lieferte keinen Save", "M1-5er")
        return finalize(run, None)

    # 2) Split 3/2
    s3, s2 = do_split(run, s5, max_mission)
    if not s3 or not s2:
        return finalize(run, None)

    # 3) Branch-Missionen (getrennte Chats = getrennte Token-Fenster)
    keys_3er = [ID2KEY[i] for i in GROUP_3ER]
    keys_2er = [ID2KEY[i] for i in GROUP_2ER]
    r3 = play_mission(run, s3, keys_3er, "M2-Alpha-3er", max_mission, BRIEFING_BRANCH)
    r2 = play_mission(run, s2, keys_2er, "M2-Bravo-2er", max_mission, BRIEFING_BRANCH)
    branch_results = [x for x in (r3, r2) if x]
    if len(branch_results) < 2:
        run.finding("ABBRUCH", "FAIL", f"Nur {len(branch_results)}/2 Branch-Ergebnis-Saves", "MERGE")
        return finalize(run, None)

    # 4) Merge (3er zuerst = Anker), keine Mission
    merged = do_merge(run, branch_results, anchor)
    finalize(run, merged)


def run_merge_only(run: Run, src_run_dir: Path):
    """Gezielter Merge-Fokus-Lauf (Fix #3235 Beweis): lädt vorhandene Branch-
    Result-Saves aus einem früheren Run-Ordner und fährt NUR den Merge mit dem
    gehärteten request_save (Level-Up-Auto-Wahl) + Faden-Routing-Analyse."""
    anchor = json.loads(ANCHOR_FIXTURE.read_text(encoding="utf-8"))
    saves_dir = src_run_dir / "saves"
    a_path = saves_dir / "m2-alpha-3er-result.json"
    b_path = saves_dir / "m2-bravo-2er-result.json"
    run.rep(f"# CoreOps MERGE-ONLY (Fix #3235 Beweis) — {time.strftime('%Y-%m-%d %H:%M')}\n\n"
            f"**SL:** {SL_MODEL} (frischer Preset, KB 19/19)  \n"
            f"**Quell-Saves:** `{src_run_dir.name}/saves/`\n\n---\n")
    run.log("=== MERGE-ONLY: lädt vorhandene Branch-Saves, fährt nur Merge ===")
    for p in (a_path, b_path):
        if not p.exists():
            run.finding("MERGE-ONLY-INPUT", "FAIL", f"Branch-Save fehlt: {p}", "MERGE")
            return finalize(run, None)
    r3 = json.loads(a_path.read_text(encoding="utf-8"))
    r2 = json.loads(b_path.read_text(encoding="utf-8"))
    run.log(f"  geladen: alpha-3er ({len(r3.get('characters', []))} chars), "
            f"bravo-2er ({len(r2.get('characters', []))} chars)")
    merged = do_merge(run, [r3, r2], anchor)
    finalize(run, merged)


def run_smoke(run: Run):
    """Billiger Pipeline-Test: Load -> Briefing-Steer -> 1 Crew-Turn. Prüft, dass
    Load/Kontinuitätsrückblick/RAG/Persona-Bündelung greifen. KEIN Save erwartet
    (mitten in der Mission blockt der SaveGuard korrekt — das ist Spielmechanik)."""
    anchor = json.loads(ANCHOR_FIXTURE.read_text(encoding="utf-8"))
    run.rep(f"# SMOKE — Pipeline-Struktur-Test ({time.strftime('%Y-%m-%d %H:%M')})\n\n---\n")
    run.log("=== SMOKE: Load -> Steer -> 1 Crew-Turn (kein Save erwartet) ===")
    chat = OWUIChat(BASE_URL, API_KEY, SL_MODEL, kb_id=KB_ID, timeout=TIMEOUT_SL)
    all_keys = ["astra", "blitz", "cipher", "dusk", "echo_p"]
    run.rep(f"## 🗂 SMOKE-5er — Chat {chat.chat_id}\n")

    txt = sl_say(run, chat, "Spiel laden:\n\n```json\n"
                 + json.dumps(anchor, ensure_ascii=False) + "\n```", "SMOKE", "[Save laden]")
    if detect_beats(txt)["continuity_recap"]:
        run.log("  ✅ SMOKE: Kontinuitätsrückblick beim Load erkannt")
    else:
        run.finding("RECAP", "SOFT", "Kein Kontinuitätsrückblick beim Load", "SMOKE")

    txt = sl_say(run, chat, BRIEFING_5ER, "SMOKE", "[Briefing -> Mission starten]")

    parts = []
    for k in all_keys:
        try:
            pt = persona_turn(PERSONAS[k], txt, "")
            parts.append((PERSONAS[k]["char_name"], pt))
        except Exception as e:  # noqa: BLE001
            run.finding("PERSONA-ERROR", "FAIL", f"{k}: {str(e)[:120]}", "SMOKE")
    for cn, pt in parts:
        run.rep(f"**{cn}:** {pt}")
    if len(parts) == len(all_keys):
        run.log(f"  ✅ SMOKE: alle {len(all_keys)} Personas haben geantwortet")
    else:
        run.finding("PERSONA-COUNT", "FAIL",
                    f"nur {len(parts)}/{len(all_keys)} Persona-Antworten", "SMOKE")
    run.log("  ✅ SMOKE: Pipeline strukturell ok (Load+RAG+Briefing+Personas). "
            "Save-Pfad greift erst am HQ — separat im Volllauf.")
    finalize(run, None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true",
                    help="Nur Pipeline-Struktur prüfen (billig, ~2-3 SL-Turns)")
    ap.add_argument("--max-turns-mission", type=int, default=30,
                    help="Max Crew-Turns pro Mission bis HQ-Savepoint (default 30)")
    ap.add_argument("--merge-only", type=str, default="", metavar="RUN_DIR",
                    help="Nur Merge: lädt Branch-Saves aus RUN_DIR/saves/ (Fix #3235 Beweis)")
    args = ap.parse_args()
    if not API_KEY:
        raise SystemExit("OPENWEBUI_API_KEY fehlt — erst: set -a; . ~/.openwebui_env; set +a")

    def _sigterm(*_a):
        print("[coreops-split-merge] SIGTERM — Abbruch", file=sys.stderr)
        sys.exit(143)
    signal.signal(signal.SIGTERM, _sigterm)

    tag = "smoke" if args.smoke else ("merge-only" if args.merge_only else "")
    pidname = f"coreops-split-merge{('-' + tag) if tag else ''}"
    pid = RUNNING_DIR / f"{pidname}.pid"
    pid.write_text(str(os.getpid()))
    try:
        run = Run(tag)
        if args.smoke:
            run.log("=== START CoreOps-Split/Merge SMOKE ===")
            run_smoke(run)
        elif args.merge_only:
            run.log("=== START CoreOps MERGE-ONLY (Fix #3235 Beweis) ===")
            run_merge_only(run, Path(args.merge_only))
        else:
            run.log("=== START CoreOps-Split/Merge (voller organischer Lauf) ===")
            run_full(run, args.max_turns_mission)
    finally:
        try:
            pid.unlink()
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    main()
