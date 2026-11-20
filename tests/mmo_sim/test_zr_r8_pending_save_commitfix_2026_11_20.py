#!/usr/bin/env python3
"""
tests/mmo_sim/test_zr_r8_pending_save_commitfix_2026_11_20.py —
ZR-R8-STRUKTURTEST-TERMINAL-RAG-20261120-R1 Stage 3 (03_FIXAUFTRAG.md §4,
Kernbug H1 aus `run/preserve/M12-BINDING-MAP.md`).

Belegte Ursache (M12, Section `local-pe14d9b7bc5c84709__15`, Turns 6->7->8):
die SL gibt auf eine normale freie Aktion einen bindbaren eigenen HQ-Export
aus (KEIN begleitendes `!save`). Der Leader tippt erst einen Turn SPAETER
`!save` -- die SL/SaveGuard antwortet mit einer ausdruecklichen Verweigerung
OHNE neuen Export. Vor diesem Fix blieb der bereits gueltige Export fuer
immer unerreichbar: `completion_hit` sah nur die Reject-Antwort DIESES
Turns (P3 unterdrueckt den expliziten-Kommando-Zweig bei einer SaveGuard-
Verweigerung), der Abschnitt blieb offen, ein `!save` wurde als neuer
bezahlter `gm_turn` verbraten.

Fix: `core/runtime.py:SectionRuntime.run_full_section`s `completion_hit`/
`finalize` erkennen jetzt zusaetzlich (`_pending_export_candidate`, baut auf
der neuen `core/_section_completion_recovery.find_pending_leader_export`),
wenn ein alleinstehendes, SaveGuard-verweigertes `!save` trotzdem einen
bereits VOR diesem Turn vorliegenden, vollstaendig gueltigen eigenen Export
uebernehmen darf -- UEBER DENSELBEN vorhandenen `finalize`-/`complete_
section`-Weg, OHNE einen dritten (zusaetzlichen) GM-/Correction-Call.

Testet am ECHTEN Verzweigungsort (`TuiSession._cmd_local_round` ->
`app_service.run_play_session` -> `core.runtime.SectionRuntime.run_full_
section`, derselbe Call-Pfad wie `test_zr_spiel_s1_fixd_save_integrity_
gate_2026_11_11.py`), KEIN isolierter Nachbau der Gate-/Recovery-Logik. Das
gescriptete GM-Fake wirft bei einem UNERWARTETEN (ueberzaehligen) Call --
das ist der direkte Beleg fuer "0 zusaetzliche GM-/Correction-Calls".

Pure Python, nur `assert`, echter Exitcode, synthetische Daten/Temp-Dirs."""
from __future__ import annotations

import json
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _full_v7_fixture import full_v7_save  # noqa: E402

from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.ui.tui import EndOfInput, TuiSession  # noqa: E402

_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
_FIX = _REPO_ROOT / "internal" / "qa" / "harness" / "lobby" / "fixtures" / "saves"

_CHAR_ID = "CHR-SNIPER-001"
_GATE_CORE_LINE = "der Stand wurde noch NICHT uebernommen"
_SAVEGUARD_REJECT = "SaveGuard: Speichern nur im HQ - HQ-Save gesperrt."


def _queued_input(values: list[str]):
    q = list(values)

    def _fn(prompt: str = "") -> str:
        if not q:
            raise EOFError()
        return q.pop(0)
    return _fn


def _save_block_text(save_id: str, level: int = 2) -> str:
    block = full_v7_save(_CHAR_ID, name="Yael", callsign="SNIPER", level=level, save_id=save_id)
    return "```json\n" + json.dumps(block, ensure_ascii=False) + "\n```"


class _ScriptedTableGm:
    """Wie `test_zr_spiel_s1_fixd_save_integrity_gate_2026_11_11.py`s
    `_ScriptedTableGm`: wirft bei einem ueberzaehligen Call -- der direkte
    Beleg, dass ein abgewiesener/rekonstruierter Abschluss KEINEN weiteren
    GM-Call ausloest."""

    def __init__(self, contents: list[str]):
        self._contents = list(contents)
        self.calls: list[str] = []

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls.append(text)
        if not self._contents:
            raise AssertionError(
                f"_ScriptedTableGm: unerwarteter {len(self.calls)}. GM-Call (Skript erschoepft) "
                f"mit text={text!r} -- die Pending-Save-Commitfix-Uebernahme darf KEINEN "
                "zusaetzlichen GM-/Correction-Call ausloesen (03_FIXAUFTRAG.md §4/§5)."
            )
        content = self._contents.pop(0)
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "table"}


def _env(root: Path):
    states_dir, run_dir = root / "states", root / "run"
    onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
    states_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    return states_dir, run_dir, onboarding_dir, catalog_dir


def _make_ready(onboarding_dir, states_dir, run_dir, catalog_dir, persona_key: str) -> dict:
    save = json.loads((_FIX / f"{persona_key}.json").read_text(encoding="utf-8"))
    from _full_v7_fixture import upgrade_narrow_save
    save = upgrade_narrow_save(save)
    ps_store = PersonaStateStore(schema_path=_SCHEMA)
    chrono_id = save["characters"][0]["id"]
    onboarding.start_or_resume(onboarding_dir, persona_key)
    onboarding.complete_with_save(onboarding_dir, persona_key, save, ZeitrissHarvestValidator(), chrono_id)
    onboarding.ensure_participant_persona_state(ps_store, states_dir, persona_key, chrono_id, save)
    core_store.publish_current_save(run_dir, persona_key, save, ps_store, states_dir)
    catalog.register(catalog_dir, catalog.CatalogEntry(
        participant_id=persona_key, chrononaut_id=chrono_id, persona_key=persona_key,
    ))
    catalog.bind_for_section(catalog_dir, persona_key, chrono_id, has_open_section=False)
    return save


def _assert_calls(calls: list[str], expected_texts: list[str]) -> None:
    assert len(calls) == len(expected_texts), (calls, expected_texts)
    for actual, expected in zip(calls, expected_texts):
        assert actual == expected or actual.startswith(expected + "\n"), (actual, expected)


def test_m12_saveguard_reject_after_unadopted_export_is_rescued_zero_extra_calls():
    """M12-Kernfall (positiv, 03 §5 "Expliziter Commit, Kandidat vollstaendig
    gueltig" UND "Bereits vorhandene Folge-Rejectantwort"): eine normale
    freie Aktion zeigt einen bindbaren, nicht uebernommenen eigenen Export
    (KEIN `!save` dabei) -> der Leader wird vom bestehenden Fix-D-Gate auf
    `!save` verwiesen -> `!save` wird (wie am echten Host beobachtet) mit
    einer SaveGuard-Verweigerung OHNE neuen Export beantwortet -> der
    Abschnitt muss TROTZDEM GENAU den frueher gezeigten Export uebernehmen,
    OHNE einen dritten GM-Call (das Skript haelt exakt zwei Eintraege bereit
    -- ein dritter wuerde das Fake werfen lassen)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        states_dir, run_dir, onboarding_dir, catalog_dir = _env(root)
        write_test_profile(run_dir)
        _make_ready(onboarding_dir, states_dir, run_dir, catalog_dir, "sniper")

        gm = _ScriptedTableGm([
            _save_block_text("m12-hq03-candidate-001", level=5),  # Turn 7: Deepsave auf freie Aktion.
            _SAVEGUARD_REJECT,  # Turn 8: '!save' wird verweigert, KEIN neuer Export.
        ])
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="sniper",
            input_fn=_queued_input([
                "Ich frage Halvorsen nach dem offenen Rift.",  # Turn 7 (normale Aktion).
                "!save",  # Turn 8 (vom Fix-D-Gate erzwungen).
                "",  # Pflicht-Abschlussnotiz -- leer = ueberspringen.
            ]),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            gm_transport_factory=lambda *_a, **_kw: gm,
        )
        try:
            session._cmd_local_round()
        except EndOfInput:
            pass  # nach Abschluss endet die Runde regulaer.

        _assert_calls(gm.calls, ["Ich frage Halvorsen nach dem offenen Rift.", "!save"])
        # (Das Fix-D-Gate selbst zeigt seine Warnzeile nur vor einer
        # ABGEWIESENEN NORMALEN Folgeaktion -- hier ist der Export bereits
        # die allererste (Anker-)Antwort und die zweite Eingabe ist schon
        # das echte '!save', das am Gate vorbeikommt, s. `is_save_command`-
        # Ausnahme in `ui/tui.py`s Warn-Schleife. Kein `_GATE_CORE_LINE`-
        # Treffer erwartet; der eigentliche Beweis ist die Call-Zahl oben
        # (exakt 2, kein dritter Call) plus der Abschluss unten.)
        assert any("Abschnitt abgeschlossen" in p for p in printed), (
            "trotz SaveGuard-Reject auf '!save' musste der Abschnitt ueber den frueher gezeigten "
            f"Export abgeschlossen werden: {printed}"
        )

        ps_store = PersonaStateStore(schema_path=_SCHEMA)
        current_after = core_store.load_current_save(run_dir, "sniper", ps_store, states_dir=states_dir)
        assert current_after is not None and current_after.get("save_id") == "m12-hq03-candidate-001", (
            "Current muss GENAU den Inhalt des frueher gezeigten Exports tragen (03 §5 "
            f"'Uebernahme genau dieses Inhalts'), nicht aus der Reject-Antwort: {current_after}"
        )
        assert current_after["characters"][0].get("lvl") == 5, current_after


def test_m12_saveguard_reject_without_any_prior_export_stays_open_no_silent_success():
    """Negativfall (03 §5 "echte Mission-/City-/Arena-SaveGuard-
    Verweigerung"/"kein Export"): `!save` ohne JEDEN vorherigen bindbaren
    Export -> SaveGuard-Verweigerung bleibt eine ehrliche Verweigerung,
    KEINE stillschweigende Uebernahme irgendeines anderen Inhalts, Current
    bleibt unveraendert, kein 'Abschnitt abgeschlossen'."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        states_dir, run_dir, onboarding_dir, catalog_dir = _env(root)
        write_test_profile(run_dir)
        save_sniper = _make_ready(onboarding_dir, states_dir, run_dir, catalog_dir, "sniper")

        gm = _ScriptedTableGm([
            "Ihr steht noch mitten im Einsatz.",  # normale Aktion, KEIN Export.
            _SAVEGUARD_REJECT,  # '!save' ausserhalb des HQ -- echte Verweigerung.
        ])
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="sniper",
            input_fn=_queued_input([
                "Ich sichere die Position.",
                "!save",
            ]),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            gm_transport_factory=lambda *_a, **_kw: gm,
        )
        try:
            session._cmd_local_round()
        except EndOfInput:
            pass  # kontrollierte Fortsetzung der laufenden Runde -- Eingabequeue erschoepft.

        _assert_calls(gm.calls, ["Ich sichere die Position.", "!save"])
        assert not any("Abschnitt abgeschlossen" in p for p in printed), (
            f"eine echte SaveGuard-Verweigerung ohne jeden Export darf NICHT als Erfolg "
            f"umgedeutet werden: {printed}"
        )
        ps_store = PersonaStateStore(schema_path=_SCHEMA)
        current_after = core_store.load_current_save(run_dir, "sniper", ps_store, states_dir=states_dir)
        assert current_after == save_sniper, (
            "Current darf durch eine ehrliche SaveGuard-Verweigerung NICHT veraendert worden "
            f"sein: {current_after}"
        )


def _is_save_command(text: str | None) -> bool:
    return (text or "").strip().casefold() in {"!save", "!speichern"}


def test_unit_find_pending_leader_export_picks_latest_valid_non_save_entry():
    """Reine Einheitenpruefung der neuen `core/_section_completion_
    recovery.find_pending_leader_export` (03 §4): findet den JUENGSTEN
    leader-eigenen, nicht-Save-Kommando-Eintrag dieser Section, dessen
    `harvest_own_export` True liefert -- bei mehreren gueltigen Treffern den
    AKTUELLSTEN (anders als `ui/tui.py`s Warn-Gate, das bewusst beim ERSTEN
    Fund stehenbleibt)."""
    from mmo_sim.core import _section_completion_recovery as recovery

    _snap = {"expected_prev_ref_by_member": {"leader": None}}
    sl_log = [
        {"origin_persona_key": "leader", "section_id": "s1", "origin_raw_input": "Aktion A", "content": "alt-export", **_snap},
        {"origin_persona_key": "leader", "section_id": "s1", "origin_raw_input": "Aktion B", "content": "neu-export", **_snap},
        {"origin_persona_key": "leader", "section_id": "s1", "origin_raw_input": "!save", "content": "reject", **_snap},
    ]
    exportable = {"neu-export", "alt-export"}
    candidate, hold_reason = recovery.find_pending_leader_export(
        sl_log, "s1", "leader",
        harvest_own_export=lambda e: e.get("content") in exportable,
        is_explicit_save_command=_is_save_command,
    )
    assert hold_reason is None, hold_reason
    assert candidate is not None and candidate["content"] == "neu-export", candidate


def test_unit_find_pending_leader_export_blocks_on_real_story_progress_after_candidate():
    """Negativfall (03 §4 'keine versteckte Eskalation'/§5 'zwischen-
    zeitlicher Storyfortschritt'): eine ECHTE weitere freie Aktion des
    Leaders NACH dem Kandidaten (kein Save-Kommando, kein neuer Export)
    macht den Kandidaten nicht mehr aktuell -- `(None, None)`, der normale
    Weg bleibt unveraendert (keine stillschweigende Uebernahme eines
    veralteten Exports)."""
    from mmo_sim.core import _section_completion_recovery as recovery

    sl_log = [
        {"origin_persona_key": "leader", "section_id": "s1", "origin_raw_input": "Aktion A", "content": "export"},
        {"origin_persona_key": "leader", "section_id": "s1", "origin_raw_input": "Echte neue Aktion", "content": "story weiter"},
        {"origin_persona_key": "leader", "section_id": "s1", "origin_raw_input": "!save", "content": "reject"},
    ]
    candidate, hold_reason = recovery.find_pending_leader_export(
        sl_log, "s1", "leader",
        harvest_own_export=lambda e: e.get("content") == "export",
        is_explicit_save_command=_is_save_command,
    )
    assert candidate is None and hold_reason is None, (candidate, hold_reason)


def test_unit_find_pending_leader_export_holds_on_missing_generation_snapshot():
    """AR2-Analogon (03 §4 Provenienz): ein sonst gueltiger Kandidat OHNE
    `expected_prev_ref_by_member` ('Legacy'/keine R12-Bindung) wird NICHT
    automatisch uebernommen, sondern als HOLD mit Begruendung gemeldet --
    dieselbe Vorsicht wie `find_recoverable_entry`."""
    from mmo_sim.core import _section_completion_recovery as recovery

    sl_log = [
        {"origin_persona_key": "leader", "section_id": "s1", "origin_raw_input": "Aktion A", "content": "export"},
    ]
    candidate, hold_reason = recovery.find_pending_leader_export(
        sl_log, "s1", "leader",
        harvest_own_export=lambda e: e.get("content") == "export",
        is_explicit_save_command=_is_save_command,
    )
    assert candidate is None, candidate
    assert hold_reason is not None and "Generations-Schnappschuss" in hold_reason, hold_reason


def test_unit_find_pending_leader_export_honors_request_binding_error():
    """03 §4 Originalprovenienz: ein injizierter `request_binding_error`-
    Treffer (z.B. fehlender/abweichender Original-Requestbeleg) wird 1:1
    als HOLD-Grund durchgereicht -- KEINE automatische Uebernahme trotz
    sonst vollstaendiger Bindung."""
    from mmo_sim.core import _section_completion_recovery as recovery

    sl_log = [
        {
            "origin_persona_key": "leader", "section_id": "s1", "origin_raw_input": "Aktion A",
            "content": "export", "expected_prev_ref_by_member": {"leader": None},
        },
    ]
    candidate, hold_reason = recovery.find_pending_leader_export(
        sl_log, "s1", "leader",
        harvest_own_export=lambda e: e.get("content") == "export",
        is_explicit_save_command=_is_save_command,
        request_binding_error=lambda entry: "kein gebundener Original-Requestbeleg",
    )
    assert candidate is None, candidate
    assert hold_reason == "kein gebundener Original-Requestbeleg", hold_reason


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"OK   {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
        except Exception:
            failed += 1
            print(f"ERROR {t.__name__}:")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} Tests bestanden.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
