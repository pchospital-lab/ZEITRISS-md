#!/usr/bin/env python3
"""
faithful_section.py — treuer EIN-Abschnitt-Orchestrator (2026-09-17).

Bildet den echten Koop-Flow aus docs/koop-online-spielen.md dateigestützt ab,
OHNE heiße OpenClaw-Subs (die könnten nicht detached im Hintergrund laufen —
DESIGN.md §1). Das Lernen der Personas lebt in den mitgeschleppten Dateien:
Persona-State-JSON (v2) + sich entwickelnder v7-Chrononaut-Save.

Unterschied zu group_table.py (dem billigen Koordinations-BEWEIS):
  - Leader ist FIX pro Abschnitt (= Anker), keine Turn-Rotation.
  - KEIN Mid-Mission-Save (nur HQ).
  - Abschnittsende: Wrap → Debrief (Level-Up VOR dem Speichern) → HQ-`!save`
    → N getrennte v7-Blöcke pro Figur (saves.extract_personal_saves) deponiert.
  - Persona-State wird aus dem SL-RUNDENERGEBNIS gespeist (nicht aus dem
    eigenen ZUG) + eine persona-authored Reflexion am Abschnittsende
    (LERNSATZ/BEZIEHUNG) fließt in learnings/relationships.
  - Carry-Forward: aktualisierte Saves + States wandern nach roster-current/
    bzw. state-current/ (kanonische Ordner bleiben unangetastet).
  - Harter Stopp am Anker: Abschnitt gilt erst als fertig, wenn JEDE Persona
    BEIDE JSONs (v7-Save + Persona-State) aktualisiert + abgelegt hat.

Aufruf:
    set -a; . ~/.openwebui_env; set +a
    python3 faithful_section.py --players cqb,sniper,face,pyro,tech --mode tell \
        --turns 10 --wrap 6 --carry
"""
from __future__ import annotations
import argparse, json, os, re, sys, time
from pathlib import Path

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(_HERE, "agent_mp"))
from owui_client import OWUIChat, stateless_completion
import sl_client
import solo_journey as sj
import persona_state as ps
import saves as save_lib

PLAYTESTS = Path.home() / ".openclaw/workspace-cloud/playtests/zeitriss"
PERSONAS_DIR = PLAYTESTS / "personas"
DEFAULT_ROSTER = PERSONAS_DIR / "roster-2026-09-16"
DEFAULT_STATE = PERSONAS_DIR / "state-2026-09-16"
PLAYER_MODEL = "anthropic/claude-sonnet-4.6"


# ── kleine Helfer ───────────────────────────────────────────────────────────

def load_save(roster_dir: Path, pk: str) -> dict:
    return json.load(open(roster_dir / f"{pk}.json"))


def compact(save: dict) -> str:
    return json.dumps(save, ensure_ascii=False)


def char_name(save: dict) -> str:
    c = save["characters"][0]
    return f'{c.get("name","?")} "{c.get("callsign","")}"'


def phase_of(sl_text: str) -> str:
    """PHASE aus der HUD-Zeile (`… · PHASE Infil · …`). '' wenn keine da."""
    m = re.search(r"PHASE\s+([A-Za-zÄÖÜäöü]+)", sl_text)
    return m.group(1) if m else ""


def scene_of(sl_text: str) -> int:
    """Höchste Szenennummer aus `SC NN/12`. 0 wenn keine/`--`."""
    best = 0
    for m in re.finditer(r"SC\s+(\d+)\s*/", sl_text):
        best = max(best, int(m.group(1)))
    return best


LEVELUP_HINT = (
    "Wenn die Spielleitung beim Debrief einen Aufstieg/Level-Up anbietet, nenne im ZUG "
    "deine EINE Wahl (+1 Attribut ODER Talent/Upgrade ODER +1 SYS). "
)


def sl_gist(sl_text: str, limit: int = 220) -> str:
    """Narrativer Kern des SL-Turns: HUD-/Kodex-Backtick-Zeilen raus, erster
    echter Absatz, auf eine Zeile geglättet."""
    lines = []
    for ln in sl_text.splitlines():
        s = ln.strip()
        if not s or s.startswith("`") or s.startswith("#") or s == "---":
            continue
        lines.append(s)
    gist = " ".join(" ".join(lines).split())
    return gist[:limit] if gist else " ".join(sl_text.split())[:limit]


def parse_two(text: str) -> tuple[str, str]:
    zug = re.search(r"ZUG\s*:\s*(.+?)(?:\n\s*NOTIZ\s*:|\Z)", text, re.DOTALL | re.IGNORECASE)
    notiz = re.search(r"NOTIZ\s*:\s*(.+)", text, re.DOTALL | re.IGNORECASE)
    z = zug.group(1).strip() if zug else text.strip()
    n = notiz.group(1).strip() if notiz else z
    return " ".join(z.split()), " ".join(n.split())


def parse_reflection(text: str) -> tuple[str | None, dict[str, str]]:
    """LERNSATZ: <x>  +  BEZIEHUNG <pk>: <y> aus der Abschnitts-Reflexion."""
    lern = re.search(r"LERNSATZ\s*:\s*(.+)", text, re.IGNORECASE)
    learning = " ".join(lern.group(1).split()) if lern else None
    rels: dict[str, str] = {}
    for m in re.finditer(r"BEZIEHUNG\s+([a-z]+)\s*:\s*(.+)", text, re.IGNORECASE):
        rels[m.group(1).lower()] = " ".join(m.group(2).split())
    return learning, rels


# ── Kern ────────────────────────────────────────────────────────────────────

def run(args) -> int:
    roster_dir = Path(args.roster_dir) if args.roster_dir else DEFAULT_ROSTER
    state_dir = Path(args.state_dir) if args.state_dir else DEFAULT_STATE
    players = [p.strip() for p in args.players.split(",") if p.strip()]
    if not players:
        print("FEHLER: keine Spieler", flush=True); return 2

    saves = {pk: load_save(roster_dir, pk) for pk in players}
    names = {pk: char_name(saves[pk]) for pk in players}
    reals = {pk: sj.PERSONAS[pk]["real_name"] for pk in players}
    states = {pk: ps.load_state(pk, states_dir=state_dir) for pk in players}
    base_rounds = {pk: states[pk].get("rounds_played", 0) for pk in players}
    # char_id -> persona_key (für saves.extract_personal_saves)
    cid2pk = {}
    for pk in players:
        cid = saves[pk]["characters"][0].get("char_id") or saves[pk]["characters"][0].get("id")
        if cid:
            cid2pk[cid] = pk

    leader = players[0]  # FIX für den ganzen Abschnitt = Anker
    today = time.strftime("%Y-%m-%d")
    stamp = time.strftime("%Y-%m-%d-%H%M")
    out = PLAYTESTS / "runs" / f"{stamp}-faithful-{args.mode}-{'-'.join(players)}"
    out.mkdir(parents=True, exist_ok=True)
    (out / "state_after").mkdir(exist_ok=True)
    (out / "deposited").mkdir(exist_ok=True)
    channel = (out / "channel.md").open("w", encoding="utf-8")
    rep = (out / "run.md").open("w", encoding="utf-8")

    def chan(s): channel.write(s + "\n"); channel.flush()
    def log(s): print(s, flush=True); rep.write(s + "\n"); rep.flush()

    # Voll-Antworten der SL sichern (nie wieder Saves durch Log-Kürzung verlieren)
    sl_full = (out / "sl_full.jsonl").open("w", encoding="utf-8")
    def log_full(turn, content):
        sl_full.write(json.dumps({"turn": turn, "phase": phase_of(content),
                                  "scene": scene_of(content), "content": content},
                                 ensure_ascii=False) + "\n"); sl_full.flush()

    # v7-Saves aus JEDER SL-Antwort scannen (die SL gibt sie beim Debrief
    # automatisch aus, nicht erst auf explizites !save) und pro Figur akkumulieren.
    collected: dict[str, dict] = {}
    def scan_saves(text):
        for blk in save_lib.extract_all_saves(text):
            cid = save_lib.block_char_id(blk)
            pk = cid2pk.get(cid) if cid else None
            if pk and pk not in collected and save_lib.single_character_count(blk) == 1:
                collected[pk] = blk
                log(f"  ✓ v7-Save erhalten: {pk} ({names[pk]}) [char_id {cid}]")

    log(f"# Treuer Abschnitt — {args.mode} — Leader(FIX)={reals[leader]}/{names[leader]}")
    log(f"Spieler: {[names[p] for p in players]}\n")
    chan(f"# Absprache-Kanal — {args.mode} — Leader FIX: {reals[leader]} ({names[leader]})\n")

    sl = OWUIChat(sl_client.BASE_URL, sl_client.API_KEY, "zeitriss-v426-uncut", kb_id=sl_client.KB_ID)

    # ── Setup: Anker zuerst, dann Joins ──────────────────────────────────────
    r = sl.say("Spiel laden. Ich füge meinen Charakter-Save (Anker/Leader) ein:\n```json\n"
               + compact(saves[leader]) + "\n```")
    for pk in players[1:]:
        r = sl.say("Ein weiterer Spieler tritt als Gast bei:\n```json\n" + compact(saves[pk]) + "\n```")
    log(f"## Setup — Anker {names[leader]} + {len(players)-1} Join(s)\nSL:\n{r['content'][:400]}\n")
    # Volle Setup-Antwort ungekürzt sichern (HQ-Hub-Angebot war bisher durch [:400] unsichtbar).
    # Reine Logging-Ergänzung, kein Spielfluss-Eingriff.
    log_full("setup", r["content"])

    def one_turn(t: int) -> dict:
        """Eine Absprache-Runde: Personas schlagen vor, FIXER Leader konsolidiert,
        Post an SL. Persona-State wird aus dem SL-ERGEBNIS gespeist."""
        nonlocal r
        sl_text = r["content"]
        chan(f"## Turn {t} — Absprache")
        table = ""
        moves = {}
        for pk in players:
            state_block = ps.render_for_prompt(states[pk])
            user = (
                f"Ihr spielt ZEITRISS gemeinsam an einem Tisch. Die Spielleitung sagt gerade:\n"
                f"---\n{sl_text[:3500]}\n---\n\n"
                f"{state_block}\n\n"
                f"Bisherige Tisch-Absprache DIESER Runde:\n{table or '(du bist die/der Erste)'}\n\n"
                f"{LEVELUP_HINT}"
                f"Du bist {reals[pk]} und spielst {names[pk]}. Reagiere in-character. "
                f"Antworte GENAU in zwei Zeilen:\n"
                f"ZUG: <was deine Figur konkret tut, 1-2 Sätze>\n"
                f"NOTIZ: <ein kurzer Satz an die anderen am Tisch>"
            )
            resp = stateless_completion(sl_client.BASE_URL, sl_client.API_KEY, PLAYER_MODEL,
                                        system=sj.PERSONAS[pk]["system"], user=user, timeout=60)
            zug, notiz = parse_two(resp)
            moves[pk] = zug
            chan(f"**{reals[pk]} ({names[pk]}):** {notiz}")
            table += f"{reals[pk]} ({names[pk]}): {notiz}\n"
            log(f"  [{pk}] ZUG: {zug[:110]}")

        # FIXER Leader konsolidiert
        addend = ("Du tippst als Leader für die ganze Gruppe an die Spielleitung. "
                  "Verwebe die Züge aller Spieler zu EINER klaren Nachricht "
                  "(tell: interpretieren+koordinieren). "
                  if args.mode == "tell" else
                  "Du tippst als Leader für die Gruppe. Bündle die Züge aller Spieler "
                  "knapp und wörtlich (strict). ")
        luser = (
            f"Die Spielleitung sagt:\n---\n{sl_text[:3000]}\n---\n\n"
            f"Die Züge aller Spieler dieser Runde:\n"
            + "\n".join(f"- {reals[p]} ({names[p]}): {moves[p]}" for p in players)
            + f"\n\nTisch-Absprache:\n{table}\n"
            f"Schreib NUR die eine Nachricht an die Spielleitung, kein Meta, keine Regie."
        )
        leader_msg = stateless_completion(sl_client.BASE_URL, sl_client.API_KEY, PLAYER_MODEL,
                                          system=sj.PERSONAS[leader]["system"] + "\n\n" + addend,
                                          user=luser, timeout=60).strip()
        chan(f"\n## Turn {t} — Leader-Post ({reals[leader]})\n> " + leader_msg.replace("\n", "\n> ") + "\n")
        log(f"  ➤ LEADER {reals[leader]}: {leader_msg[:140]}")

        r = sl.say(leader_msg)
        gist = sl_gist(r["content"])
        log(f"### Turn {t} — SL ({len(r['content'])} chars, RAG={len(sl.source_files())}, "
            f"PHASE={phase_of(r['content']) or '—'}):\n{r['content'][:500]}\n")
        log_full(t, r["content"])
        scan_saves(r["content"])   # Saves können schon hier (Debrief) kommen

        # Persona-State aus dem SL-ERGEBNIS (nicht aus dem eigenen ZUG)
        for pk in players:
            round_no = base_rounds[pk] + t
            role = " [Leader]" if pk == leader else ""
            kern = f"{args.mode} R{t}{role}: SL-Ausgang: {gist}"
            states[pk] = ps.update_state(states[pk], round_no=round_no, kernereignis=kern,
                                         now=today, datum=today,
                                         mission=f"faithful-{args.mode}")
        return r

    # ── Spielen bis ALLE N v7-Saves eingesammelt sind (= Anker), nicht bis zu
    #    einem flüchtigen PHASE HQ. Die SL gibt die Saves beim Debrief automatisch
    #    aus (scan_saves läuft in jedem Turn). Sobald alle da sind → STOPP, damit
    #    die Personas nicht in die nächste Mission weiterlaufen. ──────────────
    mission_started = False
    reached_mission_end = False   # Debrief/HQ nach Missionsstart erreicht
    highest_scene = 0
    wt = 0
    for t in range(1, args.max_turns + 1):
        wt = t
        one_turn(t)   # scannt Saves via scan_saves
        ph = phase_of(r["content"]).upper()
        sc = scene_of(r["content"])
        if sc > highest_scene:
            highest_scene = sc
        if not mission_started and ((ph and not ph.startswith("HQ")) or sc >= 1):
            mission_started = True
        if mission_started and (ph.startswith("HQ") or ph.startswith("DEBRIEF") or ph.startswith("D")):
            reached_mission_end = True
        # Save-Dump = Debrief/HQ-Ende: die SL gibt die N Personal-Saves NUR im
        # HQ-Debrief aus (kein Mid-Mission-Save), also ist 5/5-Ernte der zuverlässige
        # Missionsende-Beweis — robuster als die HUD-PHASE-Zeile (die z.B. als "PHASE D"
        # abgekürzt sein kann). Behebt FINDINGS-Detektor-Lücke (MS4/MS5 False trotz Debrief).
        if mission_started and len(collected) == len(players):
            reached_mission_end = True
        if len(collected) == len(players):
            log(f"\n## Alle {len(players)} v7-Saves eingesammelt in Turn {t} → Anker erreicht.")
            break
    else:
        log(f"\n## max-turns {args.max_turns} erreicht. Saves bisher: "
            f"{sorted(collected)} / {len(players)} (Missionsende={reached_mission_end}, "
            f"höchste Szene {highest_scene}/12)")

    # ── Save-Ernte-Nachfrage: MP-Save dauert (mehrere Minuten/Nachrichten).
    #    Wenn nach dem Debrief noch Saves fehlen, fragt der LEADER aktiv nach
    #    (nur der Leader schreibt) — mehrere Runden lang, bis alle da sind. ──
    SAVE_HARVEST_RETRIES = 8
    if len(collected) < len(players) and reached_mission_end:
        for k in range(1, SAVE_HARVEST_RETRIES + 1):
            missing = [p for p in players if p not in collected]
            if not missing:
                break
            miss_names = ", ".join(names[p] for p in missing)
            nudge = (f"Wir sind nach dem Debrief im HQ und schließen den Abschnitt ab. "
                     f"Wir haben die Save-JSONs für {miss_names} noch NICHT erhalten. "
                     f"Bitte gib JETZT die vollständigen v7-Save-Blöcke — je genau eine "
                     f"Figur, als ```json ...```-Block — für diese Figuren aus. !save")
            chan(f"\n## Save-Ernte {k} — Leader-Post ({reals[leader]})\n> {nudge}")
            r = sl.say(nudge)
            log(f"### Save-Ernte {k} — SL ({len(r['content'])} chars, "
                f"PHASE={phase_of(r['content']) or '—'}):\n{r['content'][:400]}\n")
            log_full(f"harvest-{k}", r["content"])
            scan_saves(r["content"])
        log(f"  ↳ nach Ernte: {len(collected)}/{len(players)} Saves — {sorted(collected)}")

    # ── Deposit aus collected (pro Figur ein v7-Block) ───────────────────────
    (out / "saves").mkdir(exist_ok=True)
    deposited_saves: dict[str, str] = {}
    save_records = []
    for pk, blk in collected.items():
        blob = json.dumps(blk, ensure_ascii=False, indent=2)
        dep = out / "deposited" / f"{pk}.json"
        dep.write_text(blob, encoding="utf-8")
        (out / "saves" / f"{pk}.json").write_text(blob, encoding="utf-8")
        deposited_saves[pk] = str(dep)
        save_records.append({"persona_key": pk, "single_char_ok": True,
                             "block": blk, "n_characters": 1})
    all_saves = len(collected) == len(players)
    log(f"  ↳ deponiert: {sorted(deposited_saves)} ({len(collected)}/{len(players)} Saves)")

    # ── Persona-authored Reflexion → learnings/relationships ─────────────────
    for pk in players:
        others = [p for p in players if p != pk]
        ruser = (
            f"Der Abschnitt ist vorbei. SL-Debrief/letzter Stand:\n---\n{r['content'][:2500]}\n---\n\n"
            f"Du bist {reals[pk]} ({names[pk]}). Reflektiere als Spieler:in kurz über diesen Abschnitt. "
            f"Antworte in genau diesen Zeilen:\n"
            f"LERNSATZ: <eine konkrete Erkenntnis für künftige Runden>\n"
            + "".join(f"BEZIEHUNG {o}: <ein Satz zu {reals[o]}/{names[o]}>\n" for o in others)
        )
        refl = stateless_completion(sl_client.BASE_URL, sl_client.API_KEY, PLAYER_MODEL,
                                    system=sj.PERSONAS[pk]["system"], user=ruser, timeout=60)
        learning, rels = parse_reflection(refl)
        # bump round_no über den letzten Turn hinaus, damit die Reflexion greift
        states[pk] = ps.update_state(
            states[pk], round_no=base_rounds[pk] + wt + 1,
            kernereignis=f"Abschnitts-Reflexion: {learning or '(keine)'}",
            new_learnings=[learning] if learning else None,
            relationship_updates={o: rels[o] for o in others if o in rels} or None,
            now=today, datum=today, mission=f"faithful-{args.mode}-debrief")

    # ── State-Deposit (Kanon unangetastet) ──────────────────────────────────
    for pk in players:
        ps.save_state(pk, states[pk], states_dir=out / "state_after")

    # ── Carry-Forward nach -current (nur wenn Anker komplett: alle Saves da) ──
    if args.carry and all_saves:
        roster_cur = PERSONAS_DIR / "roster-current"
        state_cur = PERSONAS_DIR / "state-current"
        roster_cur.mkdir(exist_ok=True); state_cur.mkdir(exist_ok=True)
        for pk in players:
            ps.save_state(pk, states[pk], states_dir=state_cur)
            if pk in deposited_saves:
                (roster_cur / f"{pk}.json").write_text(
                    json.dumps(save_records_block(save_records, pk), ensure_ascii=False, indent=2),
                    encoding="utf-8")
        log(f"  ↳ Carry-Forward: state-current für alle, roster-current für {sorted(deposited_saves)}")

    # ── Anker-Barriere: Abschnitt fertig, wenn alle BEIDE JSONs haben ────────
    both_ready = {pk: (pk in deposited_saves and (out / "state_after" / f"{pk}.json").exists())
                  for pk in players}
    anchor_complete = all(both_ready.values())
    grown = {pk: states[pk].get("rounds_played", 0) - base_rounds[pk] for pk in players}

    report = out / "SECTION-REPORT.md"
    report.write_text(
        f"# Abschnitts-Report — {stamp} — {args.mode}\n\n"
        f"- Leader (fix): {reals[leader]} / {names[leader]}\n"
        f"- Spieler: {', '.join(names[p] for p in players)}\n"
        f"- Turns gespielt: {wt} (max-turns {args.max_turns}), höchste Szene: {highest_scene}/12\n"
        f"- Missionsende (Debrief/HQ) erreicht: **{reached_mission_end}**\n"
        f"- v7-Saves eingesammelt: **{len(collected)}/{len(players)}** → deponiert für {sorted(deposited_saves)}\n"
        f"- Persona-State-Wachstum (Runden): {grown}\n"
        f"- **Anker vollständig (alle beide JSONs bereit): {anchor_complete}**\n"
        f"- Nicht-bereit: {[pk for pk, ok in both_ready.items() if not ok]}\n",
        encoding="utf-8")

    log(f"\n## ANKER-STATUS: complete={anchor_complete} | Missionsende={reached_mission_end} | "
        f"saves={len(collected)}/{len(players)} {sorted(deposited_saves)} | growth={grown}")
    print(f"\nOUT_DIR: {out}")
    print(f"REPORT: {report}")
    print(f"ANCHOR_COMPLETE: {anchor_complete}")
    channel.close(); rep.close(); sl_full.close()

    # Lesbares Voll-Transkript erzeugen (channel.md + sl_full.jsonl gemerged →
    # TRANSCRIPT.md): eine durchgehende Datei je Session statt drei parallel.
    try:
        import make_transcript
        make_transcript.main(str(out))
    except Exception as e:  # noqa: BLE001 — Transkript ist Komfort, kein Blocker
        print(f"(TRANSCRIPT.md konnte nicht erzeugt werden: {e})", flush=True)

    return 0 if anchor_complete else 1


def save_records_block(records, pk):
    for rec in records:
        if rec.get("persona_key") == pk:
            return rec["block"]
    return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--players", default="cqb,sniper,face,pyro,tech")
    ap.add_argument("--mode", choices=["tell", "strict"], default="tell")
    ap.add_argument("--max-turns", type=int, default=48,
                    help="Runaway-Sicherheitscap (KEIN Torso-Limit); Smoke: 1")
    ap.add_argument("--roster-dir", default="")
    ap.add_argument("--state-dir", default="")
    ap.add_argument("--carry", action="store_true", help="Ergebnis nach roster-current/state-current schreiben")
    args = ap.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
