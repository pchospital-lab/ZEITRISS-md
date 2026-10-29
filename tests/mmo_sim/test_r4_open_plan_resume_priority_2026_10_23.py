#!/usr/bin/env python3
"""
tests/mmo_sim/test_r4_open_plan_resume_priority_2026_10_23.py — FIX 1
(IMPLEMENTATION-SPEC-BETA.md, 01-CODE-REVIEW.md §1 Hauptblocker,
01-LIVE-BEFUNDE.md §2): ein Tisch mit bereits GEPINNTEM, aber noch NICHT
finalisiertem Abschluss-Auftrag (`__plan.json` ohne `__final.json`) wird vom
ECHTEN Lobby-Normalpfad (`core.lobby_flow.run_lobby_window`, derselbe Weg,
den `core.catchup`/`ui.tui`/`lab` verwenden) VORRANGIG vor weiterem Mid-Play
eines ANDEREN Tisches an den bereits bestehenden idempotenten
`core.runtime.SectionRuntime.run_full_section`-Resume dispatcht.

Reproduziert GENAU das belegte Live-Muster: Trio schliesst Ernte+Reflexion
ab, die letzte (dritte) Admission-Gate-Pruefung NACH der letzten Reflexion
("Wall-Clock endet") blockt die Finalisierung -- der Tisch bleibt `active`
mit gepinntem Plan, OHNE `__final.json`. EIN zweiter, gleichzeitig aktiver
(Duo-)Tisch OHNE eigenen offenen Plan darf die faellige Finalisierung des
Trios nicht laenger verdraengen (vorher: `find_bound_active_continuable_
table` schloss den Tisch mit offenem Plan aus und waehlte stattdessen den
anderen -- die beobachteten 81 Fremdrequests).

KEIN isolierter `finalize_*`-Aufruf als Beleg (01-CODE-REVIEW.md §1,
ausdruecklich verlangt) -- jede Assertion hier geht ueber den echten
Aufrufer `lobby_flow.run_lobby_window`."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import test_l01_l10_lobby_initiative as l01  # noqa: E402
from _section_completion_resume_fixtures import write_lab_stop, clear_lab_stop  # noqa: E402

from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core import lobby_flow  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402

_TRIO = ("sniper", "tech", "cqb")
_DUO = ("face", "medic")
_TRIO_ID = "lobby-" + "-".join(sorted(_TRIO))
_DUO_ID = "lobby-" + "-".join(sorted(_DUO))
_INITIATIVE_MARKER = "begrenztes eigenes Lobby-Initiativfenster"


class _FlexDriver:
    """Entscheidet anhand des TATSAECHLICHEN Kontrollvertrags (Muster:
    `test_s2_lobby_resume_pre_plan_completion_recovery.py:_ChildDriver`),
    NICHT anhand einer festen Antwortreihenfolge -- robust gegenueber der
    genauen Zahl/Reihenfolge der Aufrufe ueber mehrere `run_lobby_window`-
    Fenster hinweg. `propose` (optional, nur einmal verwendet) loest im
    ERSTEN Initiativfenster dieser Persona einen Tischvorschlag aus,
    danach pausiert sie in jedem weiteren Initiativfenster. `on_reflection`
    (optional) wird NACH dem Bauen der Reflexionsantwort als Seiteneffekt
    aufgerufen (hier: fuer den gezielten Wall-Clock-Stop-Repro)."""

    def __init__(self, pk: str, propose: dict | None = None, on_reflection=None):
        self.pk = pk
        self._propose = propose
        self._proposed = False
        self._on_reflection = on_reflection
        self.calls: list[dict] = []

    def decide(self, ctx: dict) -> ParticipantDecision:
        self.calls.append(ctx)
        if ctx.get("system") == "PRIVATE_REFLECTION_SENTINEL":
            text = f"Ich nehme mit, dass der Abschnitt fuer {self.pk} gut lief."
            if self._on_reflection is not None:
                self._on_reflection()
            return ParticipantDecision(text=text, origin_source=f"fake:{self.pk}")
        if "decision_contract" in ctx:
            c = ctx["decision_contract"]
            text = f"ENTSCHEIDUNG offer_id={c['offer_id']} participant_id={self.pk} decision=accept"
            return ParticipantDecision(text=text, origin_source=f"fake:{self.pk}")
        if _INITIATIVE_MARKER in ctx.get("user", ""):
            if self._propose is not None and not self._proposed:
                self._proposed = True
                return ParticipantDecision(
                    text=json.dumps({"action": "propose", **self._propose}), origin_source=f"fake:{self.pk}",
                )
            return ParticipantDecision(text=json.dumps({"action": "pause"}), origin_source=f"fake:{self.pk}")
        # Normaler Spielzug (Leader-Anker/-Debrief, Gast-Import/-Poll).
        return ParticipantDecision(text=f"'{self.pk}' spielt weiter.", origin_source=f"fake:{self.pk}")


def _bootstrap(root: Path):
    keys = [*_TRIO, *_DUO]
    schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = l01._bootstrap_community(
        root, "community-op", keys,
    )
    write_test_profile(run_dir)
    for pk in keys:
        l01._make_ready(onboarding_dir, states_dir, run_dir, pk)
    return schema_path, states_dir, run_dir, onboarding_dir, catalog_dir


def _session_and_drivers(run_dir: Path, states_dir: Path, schema_path: Path, onboarding_dir: Path, catalog_dir: Path):
    gms: dict[str, l01._TableGM] = {}

    def gm_transport_factory(tid: str):
        if tid not in gms:
            if tid == _TRIO_ID:
                saves = {pk: l01._load_fixture_save(pk) for pk in _TRIO}
                for pk, s in saves.items():
                    s["save_id"] = f"r4-open-plan-{tid}-{pk}"
                # turns_before_marker=1: der Leader-Anker-Turn selbst trifft
                # bereits den Marker (alle final_saves werden unabhaengig
                # davon ausgegeben, wessen Zug es gerade ist) -- die Gaeste
                # bekommen dadurch in DIESEM Lauf planmaessig KEINEN
                # eigenen Import-Turn (Ernte liest nur den Debrief-Text).
                gms[tid] = l01._TableGM(tid, f"{tid}-section", saves, turns_before_marker=1)
            else:
                saves = {pk: l01._load_fixture_save(pk) for pk in _DUO}
                for pk, s in saves.items():
                    s["save_id"] = f"r4-open-plan-{tid}-{pk}"
                # Unerreichbar hoch -- der Duo-Tisch bleibt in diesem Test
                # bewusst aktiv/unfertig (zweiter gleichzeitig aktiver
                # Tisch OHNE eigenen offenen Plan, s. Moduldocstring).
                gms[tid] = l01._TableGM(tid, f"{tid}-section", saves, turns_before_marker=999)
        return gms[tid]

    stop_state = {"armed": False}

    def _arm_stop_after_last_trio_reflection():
        # table.members ist sortiert ["cqb", "sniper", "tech"] -- "tech" ist
        # damit die LETZTE Reflexion in `_collect_reflections`s Schleife.
        # Alle drei Reflexionen werden dadurch VOLLSTAENDIG committet/
        # archiviert (der Stop wirkt erst auf den NAECHSTEN Gate-Check,
        # s. `core/runtime.py:_collect_reflections`s dritten Check NACH der
        # Schleife) -- exakt das belegte "drei Reflexionsaufrufe erfolgreich
        # abgerechnet, danach blockt das Wall-Clock-Fenster" Muster.
        stop_state["armed"] = True
        write_lab_stop(run_dir, "Fake-Wall-Clock-Fenster abgelaufen (R4-Fix-OffenerPlan-Repro).")

    drivers = {
        "sniper": _FlexDriver("sniper", propose={"wants": ["tech", "cqb"]}),
        "cqb": _FlexDriver("cqb"),
        "tech": _FlexDriver("tech", on_reflection=_arm_stop_after_last_trio_reflection),
        "face": _FlexDriver("face", propose={"wants": ["medic"]}),
        "medic": _FlexDriver("medic"),
    }

    printed: list[str] = []
    session = l01._session(
        "op", onboarding_dir, catalog_dir, run_dir, states_dir, schema_path,
        gm_transport_factory=gm_transport_factory,
        persona_driver_factory=lambda pk: drivers[pk],
        printed=printed,
    )
    return session, drivers, gms, stop_state, printed


def test_r4_open_plan_wins_priority_over_other_tables_mid_play():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _bootstrap(root)
        session, drivers, gms, stop_state, printed = _session_and_drivers(
            run_dir, states_dir, schema_path, onboarding_dir, catalog_dir,
        )

        # === Fenster 1: Trio bildet sich, spielt bis zur Ernte+Reflexion --
        # die DRITTE Gate-Pruefung (NACH der letzten Reflexion) wird durch
        # den Seiteneffekt der letzten Reflexionsantwort ("tech") blockiert,
        # bevor sie zurueckkehrt -- das reproduziert "Wall-Clock-Fenster
        # endet genau nach der letzten Reflexionsantwort". ===
        out1 = lobby_flow.run_lobby_window(session, ai_personas=None)
        assert out1.table_id == _TRIO_ID, out1
        assert stop_state["armed"], "tech's Reflexion haette den Stop-Seiteneffekt ausloesen muessen"

        trio_after_w1 = core_store.Table.load(run_dir, _TRIO_ID)
        assert trio_after_w1.status == "active", f"Trio darf nach Fenster 1 NOCH NICHT geschlossen sein: {trio_after_w1}"
        completion_dir = run_dir / "completion"
        plan_files = list(completion_dir.glob(f"{_TRIO_ID}-section__plan.json"))
        assert len(plan_files) == 1, f"Trio muss einen gepinnten, aber unfertigen Abschluss-Auftrag haben: {plan_files}"
        final_files = list(completion_dir.glob(f"{_TRIO_ID}-section__final.json"))
        assert not final_files, "Trio darf noch KEIN __final.json haben"
        assert out1.kind == lobby_flow.LobbyOutcomeKind.OPEN_WITH_REASON, out1
        gm_calls_trio_after_w1 = len(gms[_TRIO_ID].calls)
        assert gm_calls_trio_after_w1 == 1, gms[_TRIO_ID].calls
        reflection_calls_before = {pk: len(drivers[pk].calls) for pk in _TRIO}

        # Die Wall-Clock-Sperre betrifft ausdruecklich nur die FAELLIGE
        # Trio-Finalisierung in Fenster 1 -- sie ist KEIN dauerhafter
        # Betreiber-Stop fuer den Rest des Laufs (sonst koennte gar kein
        # weiteres Fenster, auch kein freies/anderes, je wieder etwas tun).
        # Realistisch: die Wall-Clock-Grenze wird je Lab-Aufruf NEU gesetzt;
        # hier reicht das kontrollierte Aufheben zwischen den Fenstern.
        clear_lab_stop(run_dir)

        # === Fenster 2: Duo bildet sich UND spielt mehrere echte Zuege, OHNE
        # den Trio-Tisch zu beruehren -- bewusst mit `ai_personas` auf
        # {face, medic} verengt (derselbe Verengungsvertrag wie `core.
        # catchup.py`s "remaining"-Pool), damit der noch WALL-CLOCK-
        # blockierte Trio-Tisch dieses Fenster nicht erneut (erfolglos)
        # konsumiert, bevor der Duo-Tisch ueberhaupt entstehen konnte. ===
        out2 = lobby_flow.run_lobby_window(session, ai_personas=frozenset(_DUO))
        assert out2.table_id == _DUO_ID, out2
        duo_after_w2 = core_store.Table.load(run_dir, _DUO_ID)
        assert duo_after_w2.status == "active", duo_after_w2
        assert duo_after_w2.sl_log, "Duo sollte nach Fenster 2 bereits echte Zuege haben"
        assert not list(completion_dir.glob(f"{_DUO_ID}-section__plan.json")), (
            "Duo darf (noch) KEINEN eigenen Abschluss-Auftrag haben -- zweiter aktiver Tisch OHNE Plan"
        )
        duo_sl_len_before_w3 = len(duo_after_w2.sl_log)
        duo_gm_calls_before_w3 = len(gms[_DUO_ID].calls)

        # Trio unveraendert durch Fenster 2.
        trio_after_w2 = core_store.Table.load(run_dir, _TRIO_ID)
        assert trio_after_w2.status == "active"
        assert len(gms[_TRIO_ID].calls) == gm_calls_trio_after_w1, "Fenster 2 darf keinen neuen Trio-GM-Turn ausloesen"

        # === Fenster 3 (DER PRUEFGEGENSTAND): Wall-Clock-Sperre wird
        # aufgehoben (naechstes normales Fenster), volle Roster-Sicht
        # (`ai_personas=None`, wie ein normaler TUI-/Catchup-Aufruf ohne
        # Teilauswahl). ZWEI aktive Tische sind gleichzeitig gebunden: Trio
        # (offener Plan) UND Duo (Mid-Play, kein Plan). Der Fix MUSS den
        # Trio-Tisch VORRANGIG ueber den echten Resume abschliessen --
        # OHNE neuen GM-Turn, OHNE die bereits archivierten Reflexionen
        # erneut anzufragen, UND OHNE den Duo-Tisch in diesem Fenster
        # anzufassen. ===
        clear_lab_stop(run_dir)
        out3 = lobby_flow.run_lobby_window(session, ai_personas=None)

        assert out3.table_id == _TRIO_ID, (
            f"Fenster 3 MUSS den Trio-Tisch mit offenem Plan vorrangig abschliessen, bekam aber {out3}"
        )
        assert out3.kind == lobby_flow.LobbyOutcomeKind.SECTION_COMPLETED, out3

        trio_after_w3 = core_store.Table.load(run_dir, _TRIO_ID)
        assert trio_after_w3.status == "closed", f"Trio muss nach Fenster 3 real finalisiert sein: {trio_after_w3}"
        assert list(completion_dir.glob(f"{_TRIO_ID}-section__final.json")), "Trio muss jetzt ein __final.json haben"

        # KEIN GM-Replay: derselbe EINE GM-Aufruf wie nach Fenster 1.
        assert len(gms[_TRIO_ID].calls) == gm_calls_trio_after_w1, (
            f"Fenster 3 darf KEINEN neuen GM-Turn fuer das Trio ausloesen: {gms[_TRIO_ID].calls}"
        )
        # KEINE doppelte Reflexionsverarbeitung: alle drei bereits
        # archivierten Reflexionen wurden NICHT erneut angefragt.
        for pk in _TRIO:
            assert len(drivers[pk].calls) == reflection_calls_before[pk], (
                f"'{pk}' durfte in Fenster 3 NICHT erneut befragt werden (bereits archivierte "
                f"Pflicht-Reflexion) -- calls vorher={reflection_calls_before[pk]}, "
                f"jetzt={len(drivers[pk].calls)}"
            )
        # Locks des Trios sind freigegeben.
        locks_after_w3 = core_store._read_locks(run_dir)
        for pk in _TRIO:
            assert locks_after_w3.get(trio_after_w3.chrononaut_ids[pk]) is None, (
                f"Lock von '{pk}' haette nach Finalisierung freigegeben werden muessen"
            )

        # Duo bleibt durch Fenster 3 UNBERUEHRT (weder GM-Turn noch sl_log-
        # Wachstum, noch Statuswechsel) -- "der andere Tisch bleibt danach
        # spielbar" bedeutet hier zunaechst: er wurde nicht verdraengt UND
        # nicht in Mitleidenschaft gezogen.
        duo_after_w3 = core_store.Table.load(run_dir, _DUO_ID)
        assert duo_after_w3.status == "active"
        assert len(duo_after_w3.sl_log) == duo_sl_len_before_w3, "Fenster 3 darf den Duo-sl_log nicht veraendern"
        assert len(gms[_DUO_ID].calls) == duo_gm_calls_before_w3, "Fenster 3 darf keinen Duo-GM-Turn ausloesen"

        # === Fenster 4: der Duo-Tisch bleibt regulaer spielbar/fortsetzbar
        # (jetzt als einziger gebundener Tisch, Trio-Locks bereits frei). ===
        out4 = lobby_flow.run_lobby_window(session, ai_personas=None)
        assert out4.table_id == _DUO_ID, out4
        duo_after_w4 = core_store.Table.load(run_dir, _DUO_ID)
        assert duo_after_w4.status == "active"
        assert len(duo_after_w4.sl_log) > duo_sl_len_before_w3, (
            "Duo muss in Fenster 4 tatsaechlich einen weiteren echten Zug bekommen haben "
            "(weiterhin spielbar nach der Trio-Finalisierung)"
        )


def test_r4_foreign_inconsistent_bound_plan_stays_controlled_open():
    """NEGATIVKONTROLLE (01-CODE-REVIEW.md §1/02-AUFTRAG.md §1 "ein fremd/
    inkonsistent gebundener Plan bleibt kontrolliert offen"): ein Tisch mit
    gepinntem, offenem Plan, dessen `bound_table_ids`-Zuordnung NICHT zu
    seinen tatsaechlichen `chrononaut_ids` passt (fremde/veraltete Bindung),
    darf `find_bound_active_open_plan_table` NIEMALS liefern -- kein Raten,
    kein automatischer Resume auf Verdacht."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        (run_dir / "tables").mkdir(parents=True)
        (run_dir / "completion").mkdir(parents=True)
        table = core_store.Table(
            table_id="lobby-sniper-tech", leader="sniper", members=["sniper", "tech"],
            chrononaut_ids={"sniper": "CHR-SNIPER-001", "tech": "CHR-TECH-001"},
            run_dir=run_dir, status="active", sl_log=[{"turn": 1}],
        )
        table.persist()
        (run_dir / "completion" / "lobby-sniper-tech-section__plan.json").write_text(
            json.dumps({"table_id": "lobby-sniper-tech"}), encoding="utf-8",
        )

        # (a) fremde/veraltete Figuren-Bindung: ready_chrononaut_ids weicht
        # fuer 'tech' von der am Tisch hinterlegten Figur ab.
        found_a = core_store.find_bound_active_open_plan_table(
            run_dir,
            {"sniper": "CHR-SNIPER-001", "tech": "CHR-TECH-999-FREMD"},
            {"sniper": "lobby-sniper-tech", "tech": "lobby-sniper-tech"},
        )
        assert found_a is None, "fremde Figuren-Bindung darf den offenen Plan NICHT automatisch resumen"

        # (b) widersprechende Tisch-Bindung: 'tech' ist laut Roster an einen
        # ANDEREN Tisch gebunden.
        found_b = core_store.find_bound_active_open_plan_table(
            run_dir,
            {"sniper": "CHR-SNIPER-001", "tech": "CHR-TECH-001"},
            {"sniper": "lobby-sniper-tech", "tech": "lobby-sniper-tech__ANDERER"},
        )
        assert found_b is None, "widersprechende Tisch-Bindung darf den offenen Plan NICHT automatisch resumen"

        # (c) Kontrolle: konsistente Bindung liefert den Tisch sehr wohl.
        found_c = core_store.find_bound_active_open_plan_table(
            run_dir,
            {"sniper": "CHR-SNIPER-001", "tech": "CHR-TECH-001"},
            {"sniper": "lobby-sniper-tech", "tech": "lobby-sniper-tech"},
        )
        assert found_c is not None and found_c.table_id == "lobby-sniper-tech"


if __name__ == "__main__":
    import traceback

    failures = []
    for name, fn in sorted(list(globals().items())):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"OK   {name}")
            except Exception as exc:  # noqa: BLE001
                failures.append(name)
                print(f"FAIL {name}: {exc}")
                traceback.print_exc()
    total = len([n for n in globals() if n.startswith("test_")])
    print(f"\n{total - len(failures)}/{total} Tests bestanden.")
    raise SystemExit(0 if not failures else 1)
