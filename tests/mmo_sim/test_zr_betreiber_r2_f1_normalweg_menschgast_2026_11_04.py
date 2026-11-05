#!/usr/bin/env python3
"""
tests/mmo_sim/test_zr_betreiber_r2_f1_normalweg_menschgast_2026_11_04.py --
ZR-BETREIBER-GASTERSCHAFFUNG-20261103-R2-NACHZUG, F1 (GENERAL-REVIEW.md B1,
GUEST-OPERATOR.md): der ECHTE normale Angebots-/Annahme-/Startweg
(`tisch-anbieten`/`tisch-anfragen`/`tisch-annehmen`/`tisch-start`) muss einen
Betreiber OHNE eigene Figur UND einen menschlichen Gast ALS spielenden
Leader tragen -- OHNE Pflicht zu 'lead:persona:<id>' (R1 deckte nur den
Persona-Shortcut, s. `test_zr_betreiber_o1_operator_rollenentkopplung_
2026_11_03.py`).

Modellrand-Double (EHRLICH gekennzeichnet): `_OneShotGuestDebriefGm`
liefert im ERSTEN Turn bereits den vollstaendigen Debrief (Prosa + v7-Save-
Block + Abschluss-Marker) fuer den menschlichen Gast -- die Runde durchlaeuft
GENAU einen Turn, derselbe Aufbau wie O1s `_OneShotDebriefGm`.

Deckt (F1 §1-§5 aus F1-F3a-BRIEF.md):
1. Betreiber ohne Figur wird weder Leader noch Dummy/Gast, belegt keinen
   Spielerplatz (nicht in tokens/members/chrononaut_ids, nur
   `operator_meta['operator_id']`).
2. Spielender Leader kommt aus dem angenommenen Roster (hier: der
   menschliche Gast, KEINE Persona beteiligt).
3. Oeffentliche Spektator-Ausgabe erscheint auch ohne Betreiber-Spielprompt.
4. Eindeutiges Eingaberouting: der Gast beantwortet SEINEN EIGENEN
   Spielzug-Prompt ueber SEINE EIGENE Session (`register_guest_terminal`,
   bereits bestehender, in `test_r3_f1_guest_table_service.py` getesteter
   In-Process-Mechanismus) -- NIE ueber die Hostsession/deren stdin, die der
   Betreiber-Kontrollthread (`/stop`) beansprucht. Eine zweite Probe
   belegt, dass der Rundenstart OHNE diese eindeutige Zuordnung kontrolliert
   abgelehnt wird (0 Modellaufrufe), statt eine stille Eingabekollision zu
   riskieren.
5. Stop bleibt erreichbar: nach Rundenende laesst sich `request_table_stop`
   fuer GENAU diesen Betreiber/Tisch weiterhin autorisiert aufrufen (dieselbe
   Admission-Bindung wie O2/O3/O4 nutzen es bereits live)."""
from __future__ import annotations

import json
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save  # noqa: E402

from mmo_sim.core import table_admission  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER, ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402


class _SpyFactory:
    """Wirft SOFORT bei Aufruf -- Nachweis Providerfreiheit (gleiches
    Muster wie `test_stage4_capability_gate_2026_11_02.py._SpyFactory`)."""

    def __init__(self, label: str):
        self.label = label
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        raise AssertionError(f"Spy-Factory '{self.label}' wurde aufgerufen (Gate-/Routing-Bruch).")


class _OneShotGuestDebriefGm:
    """Modellrand-Double (EHRLICH gekennzeichnet, Muster O1
    `_OneShotDebriefGm`): liefert im ERSTEN Turn bereits den vollstaendigen
    Debrief (Prosa + v7-Save-Block + Abschluss-Marker) fuer den
    menschlichen Gast-Leader -- die Runde durchlaeuft GENAU einen Turn."""

    def __init__(self, guest_save: dict):
        self._save = guest_save
        self.calls = 0

    def turn(self, turn_idx: int, user_text: str, **kw) -> dict:
        self.calls += 1
        content = (
            "Szene 1: Der Gast erkundet die verlassene Ruine.\n"
            f"```json\n{json.dumps(self._save)}\n```\n"
            f"{COMPLETION_MARKER}"
        )
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "f1-fake"}


def _register_private_figure(onboarding_dir: Path, catalog_dir: Path, participant_id: str, char_id: str) -> dict:
    """Gast-seitig: NUR die eigene private Wurzel (kein `run_dir`, keine
    Current-Publikation) -- dieselbe Vorbereitung wie `test_r3_f1_guest_
    table_service.py:_register_private_figure`."""
    save = full_v7_save(char_id, name=participant_id, save_id=f"fixture-{participant_id}-001", level=1)
    onboarding.start_or_resume(onboarding_dir, participant_id)
    onboarding.complete_with_save(onboarding_dir, participant_id, save, ZeitrissHarvestValidator(), char_id)
    catalog.register(catalog_dir, catalog.CatalogEntry(
        participant_id=participant_id, chrononaut_id=char_id, persona_key=participant_id,
    ))
    return save


def _counting_input(label: str):
    calls = {"n": 0}

    def _fn(prompt: str = "") -> str:
        if "[j/n]" in prompt:
            return "j"
        calls["n"] += 1
        return f"{label}-Zug {calls['n']}."
    return _fn, calls


def _build_sessions(root: Path, *, operator_id: str, guest_id: str, char_id: str):
    run_dir, states_dir = root / "run", root / "states"
    host_onboarding, host_catalog = root / "host_onboarding", root / "host_catalog"
    guest_onboarding, guest_catalog = root / "guest_onboarding", root / "guest_catalog"
    write_test_profile(run_dir, max_turns=200)

    # Betreiber hat bewusst KEINE eigene Figur -- kein onboarding-Datensatz,
    # keine Katalogregistrierung. `_resolve_member(operator_id)` auf der
    # Hostsession muss dadurch strukturell `None` liefern (F1-Erkennung).
    guest_save = _register_private_figure(guest_onboarding, guest_catalog, guest_id, char_id)

    guest_input, guest_calls = _counting_input("gast")
    guest_printed: list[str] = []
    guest_session = TuiSession(
        onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id=guest_id,
        input_fn=guest_input, print_fn=guest_printed.append,
        run_dir=run_dir, host_capable=False,
        # Der Gast macht STRUKTURELL null eigene Provider-/Modellaufrufe.
        gm_transport_factory=_SpyFactory("guest_gm"), persona_driver_factory=_SpyFactory("guest_persona"),
    )

    host_printed: list[str] = []
    host_fake_gm = _OneShotGuestDebriefGm(guest_save)
    host_session = TuiSession(
        onboarding_dir=host_onboarding, catalog_dir=host_catalog, participant_id=operator_id,
        print_fn=host_printed.append,
        run_dir=run_dir, states_dir=states_dir,
        schema_path=_REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json",
        gm_transport_factory=lambda: host_fake_gm, persona_driver_factory=_SpyFactory("host_persona"),
        host_capable=True,
    )
    return host_session, guest_session, host_printed, guest_printed, guest_calls, run_dir, host_fake_gm


def test_f1_betreiber_ohne_figur_menschlicher_gast_wird_spielender_leader():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        operator_id, guest_id, char_id, table_key = "betreiber_f1", "gast_f1", "CHR-GASTF1", "mesaF1"
        host_session, guest_session, host_printed, guest_printed, guest_calls, run_dir, fake_gm = _build_sessions(
            root, operator_id=operator_id, guest_id=guest_id, char_id=char_id,
        )

        # Echter Angebot-/Anfrage-/Annahme-/Startweg (Produktbefehle, kein
        # Direktaufruf des Spielkerns).
        host_session._cmd_table_offer([table_key])
        guest_session._cmd_table_request_join([table_key])
        host_session._cmd_table_accept([table_key, guest_id])

        # Eindeutiges Eingaberouting (F1 §5): der Gast bekommt einen EIGENEN
        # Teilnehmeranschluss, bevor der Tisch startet.
        host_session.register_guest_terminal(guest_id, guest_session)

        host_session._cmd_table_start([table_key])
        record = table_admission.load_record(run_dir, table_key)
        section_id = record.get("section_id")
        assert section_id is not None, f"Betreibertisch haette entstehen muessen. host_printed={host_printed}"
        assert fake_gm.calls == 1, f"genau ein Turn erwartet, calls={fake_gm.calls}"

        table = core_store.Table.load(run_dir, section_id)

        # (1) Betreiber weder Leader noch Dummy/Gast, kein Spielerplatz.
        assert operator_id not in table.members, table.members
        assert operator_id not in table.chrononaut_ids, table.chrononaut_ids
        assert table.operator_meta.get("operator_id") == operator_id, table.operator_meta

        # (2) Spielender Leader kommt aus dem angenommenen Roster -- hier
        # der menschliche Gast, KEINE Persona, KEIN 'lead:persona:'-Zwang.
        assert table.leader == guest_id, table.leader
        assert table.members == [guest_id], table.members
        assert table.chrononaut_ids.get(guest_id) == char_id, table.chrononaut_ids

        # (3) Oeffentliche Spektator-Ausgabe erscheint auf dem Betreiber-
        # Terminal, auch OHNE eigenen Betreiber-Spielprompt.
        zuschauer_lines = [p for p in host_printed if p.startswith("[Zuschauer]")]
        assert zuschauer_lines, f"Spektator-Ausgabe haette erscheinen muessen. host_printed={host_printed}"

        # (4) Eindeutiges Eingaberouting: der Gast hat TATSAECHLICH selbst
        # getippt und SL-Antworten auf SEINEM EIGENEN Terminal gesehen --
        # der Host-Bildschirm hat NIE einen Spielzug-Prompt fuer den Gast
        # gezeigt (kein Host-Fake, keine verlorene/verwechselte Steuerzeile).
        assert guest_calls["n"] > 0, "Der Gast haette selbst tatsaechlich eingeben muessen."
        assert any(p.startswith("[SL]") for p in guest_printed), (
            f"Der Gast haette SL-Antworten auf seinem EIGENEN Terminal sehen muessen: {guest_printed}"
        )
        assert not any("Deine Aktion" in p for p in host_printed), (
            f"Der Host-Bildschirm haette NIE einen Spielzug-Prompt zeigen duerfen: {host_printed}"
        )

        # Admission-Record real geschlossen (echter Abschluss durchgelaufen).
        record = table_admission.load_record(run_dir, table_key)
        assert record["state"] == table_admission.STATE_CLOSED, record
        assert record["roster"] == [operator_id, guest_id], record

        # Kein Operator-Save/-Harvest/-Phantomspieler.
        assert not (run_dir / "current_saves" / f"{operator_id}.json").exists()
        assert onboarding.peek(host_session.onboarding_dir, operator_id) is None, (
            "kein Onboarding-Datensatz fuer den Betreiber -- er hat nie eine Figur erschaffen."
        )
        assert (run_dir / "current_saves" / f"{guest_id}.json").exists(), (
            "die Gastfigur haette real geerntet werden muessen."
        )

        # (5) Stop bleibt erreichbar: dieselbe Betreiber-/Tisch-Bindung, die
        # O2/O3/O4 live nutzen, ist auch fuer DIESEN neuen Leader-Weg real
        # aufgebaut (bind_section bereits waehrend `_cmd_table_start`).
        payload = table_admission.request_table_stop(
            run_dir, table_key=table_key, operator_id=operator_id, table_id=section_id,
            reason="Nachweis: Stop bleibt nach Rundenende erreichbar.",
        )
        assert payload["operator_id"] == operator_id, payload


def test_f1_eingaberouting_kollision_wird_kontrolliert_abgelehnt_ohne_registrierten_anschluss():
    """F1 §5 Gegenprobe: OHNE `register_guest_terminal` fuer den
    menschlichen Leader UND OHNE eigene `operator_control_line_source`
    wird der Rundenstart kontrolliert VERWEIGERT (0 Modellaufrufe) --
    keine stille Eingabekollision zwischen Betreiber-Kontrollthread und
    Gast-Spielzug am geteilten Terminal."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        operator_id, guest_id, char_id, table_key = "betreiber_f1b", "gast_f1b", "CHR-GASTF1B", "mesaF1b"
        host_session, guest_session, host_printed, guest_printed, guest_calls, run_dir, fake_gm = _build_sessions(
            root, operator_id=operator_id, guest_id=guest_id, char_id=char_id,
        )
        # Die Host-GM-Factory wird durch einen Spy ersetzt -- ein
        # tatsaechlicher Modellaufruf bei verweigertem Start waere ein
        # Routing-Bruch.
        host_session.gm_transport_factory = _SpyFactory("host_gm_should_not_be_called")

        host_session._cmd_table_offer([table_key])
        guest_session._cmd_table_request_join([table_key])
        host_session._cmd_table_accept([table_key, guest_id])
        # BEWUSST: kein `register_guest_terminal`, kein `operator_control_
        # line_source` -- der Gast wuerde sonst dieselbe (hier: Host-)
        # Eingabequelle wie der Betreiber-Kontrollthread teilen.

        section_id = host_session._cmd_table_start([table_key])
        assert section_id is None, (
            f"Rundenstart haette abgelehnt werden muessen (keine eindeutige Eingabezuordnung). "
            f"host_printed={host_printed}"
        )
        assert any("Eingaberouting-Kollision" in p for p in host_printed), host_printed
        assert guest_calls["n"] == 0, "Der Gast darf bei verweigertem Start NIE zur Eingabe aufgefordert worden sein."

        # Tisch bleibt real bedienbar (kein eingefrorener 'started'-Zustand).
        record = table_admission.load_record(run_dir, table_key)
        assert record["state"] == table_admission.STATE_OPEN, record


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
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
