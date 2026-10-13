#!/usr/bin/env python3
"""
tests/mmo_sim/test_w11_r01_r04_eingabe_und_write_grenzen_2026_10_05.py — W11
(ZEITRISS Terminal-UX1 R3-Abschluss, 05.10.2026), dauerhafte Regressionen fuer
die fuenf vom neuen REVIEW.md (§R01/§R04) konkret belegten Reste Q01/Q02/
Q05B/Q06/Q08 (FINDINGS.json "R01"/"R04", CASE-REVIEW.json UX04/UX05/UX18/
UX21).

Jeder Testname beschreibt den EHEMALIGEN Fehler (negative Altprobe) UND
belegt die jetzt korrekte, positive Regression -- ein bloss rc0 liefernder
Gegenprobenlauf ist KEIN Reparatur-PASS, deshalb echte `assert`s auf
Produktzustand (Registrydateien, GM-Aufrufzaehler, Druckzeilen), nicht nur
Exitcodes.

Q01 (`_cmd_register_new_person`, vormals `tui.py:386-389`): '/abbrechen' an
  der Frage "Als bestehende Person fortsetzen? [j/n]" wurde VOR dem Fix
  woertlich als (ungueltige) j/n-Antwort behandelt und fiel in den
  "sonst neu registrieren"-Zweig durch -- zweiter gleichnamiger Datensatz.
Q02 (`_cmd_new_or_switch_character:_human_get_reply`, vormals `tui.py:
  1070-1077`): '/hilfe'/'/abbrechen' an der tatsaechlichen Erschaffungs-
  antwort ("Deine Antwort:") gingen VOR dem Fix als woertliche Antwort an
  den Onboardingzustand UND an den synthetischen GM.
Q06 (`_cmd_register_new_person`, Owner-Guard): ein WAEHREND der Namens-
  eingabe (nach dem fruehen Guard am Funktionsanfang) aktiv werdender
  fremder Lab-Lock wurde VOR dem Fix fuer den tatsaechlichen Registry-Write
  nicht erneut geprueft.
Q08 (`registry/participants.py:find_by_display_name`/`load_participant`):
  ein Registry-Objekt mit passendem `display_name`, aber OHNE
  `participant_id`, wirft VOR dem Fix weiterhin `KeyError` (der
  `isinstance(dict)`-Schutz allein reicht nicht).
Q05B (`_opaque_boundary_error`): dieselbe Meldung behauptete VOR dem Fix
  auch nach einem TATSAECHLICH versuchten `request_admitted_decision`-
  Aufruf (Fabrik gebaut, `driver.decide()` real gerufen, Requestledger-
  Reservierung begonnen) weiterhin "kein Modellaufruf".

Isolationsdisziplin identisch zu `test_g05_error_redaction_and_guards.py`
(eigenes temporaeres HOME/XDG, Netzwerk-Guard VOR Produktimport aktiv, zwei
bewusst geblockte Negativaufrufe als Wirkungsbeleg, Provider-Env-Allowlist,
keine echten Keys/Subprozesse ausser dem einen lokalen `time.sleep`-
Fremdprozess fuer den Q06-Locktest). Pure Python, nur `assert`, echter
Exitcode, synthetische Daten/Temp-Dirs."""
from __future__ import annotations

import http.client
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]

# --- Testumgebungsisolation: temporaeres HOME/XDG VOR jedem Produktimport ---
_ISOLATED_HOME_DIR = tempfile.TemporaryDirectory(prefix="w11-isolated-home-")
_ORIGINAL_ENV_SNAPSHOT = {
    k: os.environ.get(k) for k in ("HOME", "XDG_DATA_HOME", "XDG_CONFIG_HOME", "XDG_CACHE_HOME")
}
os.environ["HOME"] = _ISOLATED_HOME_DIR.name
os.environ["XDG_DATA_HOME"] = str(Path(_ISOLATED_HOME_DIR.name) / "xdg-data")
os.environ["XDG_CONFIG_HOME"] = str(Path(_ISOLATED_HOME_DIR.name) / "xdg-config")
os.environ["XDG_CACHE_HOME"] = str(Path(_ISOLATED_HOME_DIR.name) / "xdg-cache")
for _leaky_key in list(os.environ):
    if _leaky_key.startswith("MMO_SIM_PERSONA_") or _leaky_key.startswith("OPENWEBUI_"):
        os.environ.pop(_leaky_key, None)

# --- Netzwerk-Guard: VOR jedem Produktimport aktiv (auch in Kindern, s.u.) ---
_REAL_SOCKET = socket.socket


class _NetworkBlockedInTest(RuntimeError):
    pass


def _blocked_socket(*_a, **_k):
    raise _NetworkBlockedInTest("Netzwerk-Socket in isoliertem W11-Testlauf blockiert (kein Live-/Providercall).")


socket.socket = _blocked_socket  # type: ignore[assignment]

if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import catalog  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding  # noqa: E402
from mmo_sim.registry.participants import ParticipantRegistry  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
_SECRET_MARKER = "SYNTHETIC_SECRET_DO_NOT_PRINT_W11"


def _scripted_input(lines: list[str]):
    it = iter(lines)

    def _fn(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration:
            raise EOFError()
    return _fn


def _scripted_input_with_side_effect(lines: list[str], side_effects: dict[int, "callable"]):
    """Wie `_scripted_input`, ruft aber VOR Rueckgabe der Zeile mit Index
    `i` (0-basiert) eine optionale Nebenwirkung auf -- modelliert einen
    Zustandswechsel (hier: ein fremder Lab-Lock wird aktiv), der WAEHREND
    der laufenden Eingabe passiert, nicht erst davor."""
    state = {"idx": 0}

    def _fn(prompt: str = "") -> str:
        i = state["idx"]
        if i in side_effects:
            side_effects[i]()
        if i >= len(lines):
            raise EOFError()
        state["idx"] += 1
        return lines[i]
    return _fn


class _FakeCreationGm:
    def __init__(self, content: str = "Wie beginnt deine Zeitreise?"):
        self.calls: list[tuple[int, str]] = []
        self._content = content

    def turn(self, idx, text, **_kw):
        self.calls.append((idx, text))
        return {"content": self._content}


class _FlakyDecideDriver:
    """Baut erfolgreich (Factory-Aufruf wirft NICHT), aber `.decide()`
    selbst -- der tatsaechliche admission-gated Request-Call innerhalb
    `lobby_service.request_admitted_decision` -- wirft NACH der Reservierung
    (Q05B: 'Anfrage versucht, Ergebnis unklar', nicht 'kein Modellaufruf')."""

    is_dollar_billed = False

    def decide(self, _ctx):
        raise RuntimeError(_SECRET_MARKER)


# ---------------------------------------------------------------------------
# Netzwerk-Guard-Beleg (zwei bewusst geblockte Negativaufrufe)
# ---------------------------------------------------------------------------

def test_network_guard_blocks_raw_socket_creation():
    try:
        socket.socket()
    except _NetworkBlockedInTest:
        pass
    else:
        raise AssertionError("socket.socket() haette im isolierten Testprozess blockiert werden muessen")


def test_network_guard_blocks_http_client_connection():
    conn = http.client.HTTPConnection("127.0.0.1", 1, timeout=1)
    try:
        conn.connect()
    except _NetworkBlockedInTest:
        pass
    else:
        raise AssertionError("http.client-Verbindung haette ueber denselben Socket-Guard blockiert werden muessen")
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Q01 -- '/abbrechen' an "Als bestehende Person fortsetzen?" dupliziert nicht
# ---------------------------------------------------------------------------

def test_q01_abbrechen_at_existing_person_confirm_does_not_duplicate():
    """Altprobe (REVIEW.md Q01): eine bereits registrierte 'Alice' plus
    '/abbrechen' an der Bestaetigungsfrage erzeugte vorher einen ZWEITEN
    Datensatz unter demselben Namen. Regression: genau EIN Datensatz bleibt
    bestehen, kein 'Neu registriert' erscheint, die Steuerzeile selbst wird
    nicht als Name/Antwort gespeichert."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        registry = ParticipantRegistry(d / "registry")
        registry.register_participant(kind="human", display_name="Alice")

        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="original-human",
            input_fn=_scripted_input(["Alice", "/abbrechen"]),
            print_fn=printed.append,
        )
        session._cmd_register_new_person()

        assert not any("Neu registriert" in p for p in printed), printed
        assert any("Registrierung abgebrochen" in p for p in printed), printed
        matches = registry.find_by_display_name("Alice")
        assert len(matches) == 1, f"Erwartet genau 1 Datensatz fuer 'Alice', gefunden: {matches}"
        # Fokus bleibt beim urspruenglichen Teilnehmer -- kein stiller Wechsel.
        assert session.participant_id == "original-human"


def test_q01_zurueck_and_pause_at_existing_person_confirm_also_abort_cleanly():
    """Ergaenzend zu '/abbrechen': '/zurueck' und '/pause' sind ebenfalls
    Steuerzeilen an diesem Prompt (nicht nur der eine im Review belegte
    String) und duerfen ebenso wenig zu einer Dublette fuehren."""
    for control_token in ("/zurueck", "/pause"):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            registry = ParticipantRegistry(d / "registry")
            registry.register_participant(kind="human", display_name="Bob")
            printed: list[str] = []
            session = TuiSession(
                onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="original-human",
                input_fn=_scripted_input(["Bob", control_token]),
                print_fn=printed.append,
            )
            session._cmd_register_new_person()
            assert not any("Neu registriert" in p for p in printed), (control_token, printed)
            matches = registry.find_by_display_name("Bob")
            assert len(matches) == 1, (control_token, matches)


def test_q01_plain_j_still_continues_as_existing_person_regression_guard():
    """Gegenprobe: eine GEWOEHNLICHE 'j'-Antwort (kein Steuerwort) muss nach
    der Verdrahtung auf den zentralen Leser unveraendert als Zustimmung
    wirken -- sonst waere der bestehende, bereits gruene W10-Testpfad
    (`test_ux1_w10_figur_prompt_steuervertrag_2026_10_05.py`) beschaedigt."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        registry = ParticipantRegistry(d / "registry")
        registry.register_participant(kind="human", display_name="Carol")
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="original-human",
            # "Carol" -> Name; "j" -> bestehende Person fortsetzen; "j" ->
            # Fokusuebernahme bestaetigen (_local_round_handoff); "/abbrechen"
            # -> am anschliessenden Figur-Prompt kontrolliert abbrechen
            # (derselbe Eingabestil wie `test_ux1_w10_figur_prompt_
            # steuervertrag_2026_10_05.py`).
            input_fn=_scripted_input(["Carol", "j", "j", "/abbrechen"]),
            print_fn=printed.append,
        )
        session._cmd_register_new_person()
        assert any("Fortsetzung als bestehende Person 'Carol' bestaetigt" in p for p in printed), printed
        assert any("Fokus uebernommen" in p for p in printed), printed
        assert any("Fokus zurueck bei 'original-human'" in p for p in printed), printed
        assert session.participant_id == "original-human"
        matches = registry.find_by_display_name("Carol")
        assert len(matches) == 1, matches


# ---------------------------------------------------------------------------
# Q02 -- Steuerzeilen an der tatsaechlichen Erschaffungsantwort
# ---------------------------------------------------------------------------

def test_q02_abbrechen_at_creation_answer_not_forwarded_to_gm():
    """Altprobe (REVIEW.md Q02): '/abbrechen' an 'Deine Antwort:' ging vorher
    als woertliche Antwort an den synthetischen GM (zweiter, ungewollter
    Fake-GM-Aufruf). Regression: der GM-Aufrufzaehler bleibt bei 1 (nur der
    initiale Erschaffungsstart), '/abbrechen' erscheint in KEINEM an den GM
    gesendeten Text."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        write_test_profile(d / "run")
        gm = _FakeCreationGm()
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input(["/abbrechen"]),
            print_fn=printed.append,
            run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: gm,
        )
        session._cmd_new_or_switch_character()

        assert len(gm.calls) == 1, gm.calls
        assert not any("/abbrechen" in text for _idx, text in gm.calls), gm.calls
        assert any("wird NICHT als Antwort an die SL gesendet" in p for p in printed), printed

        # Der offene Schritt bleibt unveraendert fortsetzbar -- kein Verlust.
        pending = onboarding.peek(d / "onboarding", "p1")
        assert pending is not None and pending.pending_step is not None
        assert pending.pending_step.get("persona_answer") is None


def test_q02_hilfe_at_creation_answer_handled_locally_not_forwarded():
    """Altprobe (REVIEW.md Q02): '/hilfe' an 'Deine Antwort:' ging vorher
    GENAUSO woertlich an den GM (insgesamt drei Fake-GM-Aufrufe fuer eine
    einzige wirkliche Absicht laut Review). Regression: '/hilfe' wird
    VOLLSTAENDIG lokal durch den zentralen Leser beantwortet (Kontexthilfe),
    OHNE je `_human_get_reply` mit diesem Text zu verlassen -- der
    GM-Aufrufzaehler bleibt bei 1, bis eine echte Steuerzeile (hier
    '/abbrechen') die Eingabe beendet."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        write_test_profile(d / "run")
        gm = _FakeCreationGm()
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input(["/hilfe", "/abbrechen"]),
            print_fn=printed.append,
            run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: gm,
        )
        session._cmd_new_or_switch_character()

        assert len(gm.calls) == 1, gm.calls
        assert not any("/hilfe" in text for _idx, text in gm.calls), gm.calls
        assert any("Hilfe (Erschaffungsantwort)" in p for p in printed), printed


# ---------------------------------------------------------------------------
# Q06 -- Owner-Guard unmittelbar vor dem gemeinsamen Registry-Write
# ---------------------------------------------------------------------------

def test_q06_registration_write_blocked_by_lock_activated_during_name_input():
    """Altprobe (REVIEW.md Q06): der fruehe Guard am Funktionsanfang sieht
    noch KEINEN fremden Lock; aktiviert ein lebender Fremdprozess seinen
    Lock WAEHREND der Namenseingabe (nach dem fruehen Check, vor dem
    tatsaechlichen Write), schrieb die Funktion vorher trotzdem eine neue
    Person. Regression: der Guard wird UNMITTELBAR vor dem Write erneut
    angewandt -- kein Write, keine Teilnehmerdatei entsteht."""
    foreign = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(30)"],
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        deadline = time.monotonic() + 5.0
        while foreign.poll() is not None and time.monotonic() < deadline:
            time.sleep(0.05)
        assert foreign.poll() is None, "Fremdprozess fuer den Lock-Test ist nicht am Leben"

        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            run_dir = d / "run"
            run_dir.mkdir(parents=True, exist_ok=True)
            registry_dir = d / "registry"

            def _activate_foreign_lock():
                (run_dir / "lab.lock.json").write_text(
                    json.dumps({"pid": foreign.pid}), encoding="utf-8",
                )

            printed: list[str] = []
            session = TuiSession(
                onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="original-human",
                # Index 0 ist die Namensantwort selbst -- die Nebenwirkung
                # (Lock wird aktiv) feuert, WAEHREND diese Eingabe "laeuft",
                # also NACH dem fruehen Guard am Funktionsanfang, aber VOR
                # dem Write weiter unten.
                input_fn=_scripted_input_with_side_effect(
                    ["Zwischenzeitlich gesperrte Person"], {0: _activate_foreign_lock},
                ),
                print_fn=printed.append,
                run_dir=run_dir, states_dir=d / "states", schema_path=_SCHEMA_PATH,
            )
            session._cmd_register_new_person()

            assert any("aktiver Lab-Lauf" in p and f"pid={foreign.pid}" in p for p in printed), printed
            assert not any("Neu registriert" in p for p in printed), printed
            written = list(registry_dir.glob("participant__*.json")) if registry_dir.exists() else []
            assert written == [], f"Registrierungswrite trotz waehrend der Eingabe aktivem Fremdlock: {written}"
    finally:
        foreign.terminate()
        try:
            foreign.wait(timeout=5)
        except subprocess.TimeoutExpired:
            foreign.kill()
            foreign.wait(timeout=5)


# ---------------------------------------------------------------------------
# Q08 -- Registry-Strukturvalidierung (display_name ohne participant_id)
# ---------------------------------------------------------------------------

def test_q08_find_by_display_name_skips_entry_missing_participant_id_no_keyerror():
    """Altprobe (REVIEW.md Q08): ein Objekt (`isinstance(dict)` TRUE) mit
    passendem `display_name`, aber OHNE `participant_id`, wirft vorher
    weiterhin `KeyError` beim Aufbau von `Participant(...)`. Regression:
    der Scan ueberspringt den strukturell unvollstaendigen Treffer lesend,
    findet aber weiterhin den validen Treffer; die defekte Datei bleibt
    unveraendert (kein Reparaturwrite)."""
    with tempfile.TemporaryDirectory() as td:
        registry_dir = Path(td) / "registry"
        registry = ParticipantRegistry(registry_dir)
        registry.register_participant(kind="human", display_name="Dora")

        broken_path = registry_dir / "participant__zz-missing-id.json"
        broken_payload = {"display_name": "Dora", "kind": "human"}  # kein participant_id
        broken_path.write_text(json.dumps(broken_payload), encoding="utf-8")
        before = broken_path.read_bytes()

        # Darf NICHT raisen (vorher: KeyError auf data["participant_id"]).
        matches = registry.find_by_display_name("Dora")
        assert len(matches) == 1, matches
        assert matches[0].display_name == "Dora"

        after = broken_path.read_bytes()
        assert before == after, "Q08-Reader darf die defekte Datei nicht veraendern (rein lesend)"


def test_q08_load_participant_reports_missing_fields_controlled_not_keyerror():
    """Derselbe Strukturschutz fuer den direkten ID-Zugriffsweg
    (`load_participant`) -- eine kontrollierte `ValueError` mit klarer
    Ursache statt eines rohen `KeyError` auf ein beliebiges fehlendes
    Feld, weiterhin keine automatische Reparatur."""
    with tempfile.TemporaryDirectory() as td:
        registry_dir = Path(td) / "registry"
        registry = ParticipantRegistry(registry_dir)
        broken_path = registry_dir / "participant__zz-direct.json"
        broken_path.write_text(json.dumps({"display_name": "Erik", "kind": "human"}), encoding="utf-8")

        try:
            registry.load_participant("zz-direct")
        except KeyError:
            raise AssertionError("load_participant darf hier nicht mehr mit rohem KeyError abbrechen")
        except ValueError as e:
            assert "participant_id" in str(e) or "Pflichtfelder" in str(e), str(e)
        else:
            raise AssertionError("load_participant haette den strukturell unvollstaendigen Datensatz melden muessen")


# ---------------------------------------------------------------------------
# Q05B -- ehrlicher Fehlerstatus vor/nach tatsaechlich versuchter Anfrage
# ---------------------------------------------------------------------------

def test_q05b_opaque_boundary_error_distinguishes_preflight_vs_attempted():
    """Reine Vertragsprobe der Textbausteine selbst: der Default
    (`attempted=False`, unveraendertes Verhalten jeder Fabrikbau-
    Aufrufstelle) behauptet weiterhin ehrlich 'kein Modellaufruf';
    `attempted=True` (die nach `request_admitted_decision` genutzten
    Aufrufstellen) behauptet das NICHT mehr, verspricht aber auch keine
    Kosten/keinen automatischen Retry und leckt in beiden Faellen keine
    Interndetails."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        session = TuiSession(onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1")
        preflight = session._opaque_boundary_error("Kontext A nicht moeglich")
        attempted = session._opaque_boundary_error("Kontext B fehlgeschlagen", attempted=True)

        assert "kein Modellaufruf" in preflight, preflight
        assert "kein Modellaufruf" not in attempted, attempted
        assert "bereits versuchten Aufruf" in attempted, attempted
        assert "kein automatischer" in attempted, attempted
        for text in (preflight, attempted):
            assert _SECRET_MARKER not in text
            assert "Traceback" not in text


def test_q05b_fresh_start_invite_after_attempted_decide_call_does_not_claim_zero_calls():
    """Altprobe (REVIEW.md Q05B, End-to-End): die Persona-Fabrik baut
    erfolgreich (kein 'kein Modellaufruf'-Fall), aber `driver.decide()`
    wirft NACH einer bereits begonnenen Requestledger-Reservierung -- ein
    tatsaechlich versuchter Aufruf mit unklarem Ergebnis. Vorher behauptete
    die Meldung an dieser Stelle trotzdem faelschlich 'kein Modellaufruf'.
    Regression: die Meldung nennt den versuchten Aufruf ehrlich, OHNE
    Secret-/Traceback-Leck und OHNE automatischen Retry (Funktion kehrt
    nach genau einem Versuch zurueck)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        write_test_profile(d / "run")
        catalog.register(
            d / "catalog",
            catalog.CatalogEntry(
                participant_id="flaky_persona", chrononaut_id="CHR-FLAKY", persona_key="flaky_persona",
            ),
        )
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input(["flaky_persona"]),
            print_fn=printed.append,
            run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: _FakeCreationGm(),
            persona_driver_factory=lambda _pid: _FlakyDecideDriver(),
        )
        session._invite_persona_fresh_start()

        assert not any(_SECRET_MARKER in p for p in printed), printed
        assert not any("Traceback" in p for p in printed), printed
        target = [p for p in printed if "zum gemeinsamen Frischstart nicht zustande gekommen" in p]
        assert target, printed
        assert not any("kein Modellaufruf" in p for p in target), target
        assert any("bereits versuchten Aufruf" in p for p in target), target


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
    rc = main()
    socket.socket = _REAL_SOCKET  # type: ignore[assignment]
    for _k, _v in _ORIGINAL_ENV_SNAPSHOT.items():
        if _v is None:
            os.environ.pop(_k, None)
        else:
            os.environ[_k] = _v
    _ISOLATED_HOME_DIR.cleanup()
    raise SystemExit(rc)
