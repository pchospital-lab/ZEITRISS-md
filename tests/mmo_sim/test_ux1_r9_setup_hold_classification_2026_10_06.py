#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_r9_setup_hold_classification_2026_10_06.py — R9/W34
(ZEITRISS Terminal UX-1, Reparatur R9, BRIEF-W34.md): belegt F03 am ECHTEN
`manual_offline_harness.py`-Subprozess (nicht an einer Testdoppel-
Nachbildung).

Befund (R8-F03, `evidence/missing-marker-observation.json`,
`evidence/probe_missing_marker.py`): der Harness entschied Erst- vs.
Neustartlage bisher AUSSCHLIESSLICH am Marker `harness_participant.json`
(`is_fresh_setup = not marker_path.is_file()`). Fehlte der Marker, aber der
Produktbestand (Registry/Onboarding/States/Current) war bereits
fortgeschrieben, lief `write_test_profile()` trotzdem unbedingt, wurde ein
NEUER Leader registriert UND jede KI-Persona ungeprueft als "absent"
behandelt -- `sup.make_ready()` republizierte dadurch die Anfangsfixtur und
ueberschrieb die fortgeschrittenen `medic`/`sniper`/`tech`-Saves + States.

Fix (`manual_offline_harness.py`, s. dortige R9/W34-Docstring-Notiz):
`_classify_harness_root()` entscheidet den GESAMTEN Bestand (Marker +
Leaderbindung + alle KI-Personas) VOLLSTAENDIG lesend, VOR jedem Write, und
liefert eine von drei Klassen: `FRESH_EMPTY` (Erstvorbereitung bleibt
erlaubt), `EXISTING_CONSISTENT` (passiver Start) oder `SETUP_HOLD` (klarer
Abbruch, `return 3`, KEINE neue Person, KEINE Ersatz-Marker-Reparatur,
KEINE Teilwrites).

Sieben kleine, getrennte Szenarien (je eigener Tempdir):

  test_fresh_empty_prepares_leader_marker_and_ai_bestand:
  FRESH_EMPTY -> rc 0, Marker + `lab.status.json` korrekt, alle drei
  KI-Personas tischbereit (Fixture-Stand).

  test_normal_product_start_preserves_progressed_save:
  normaler, echter Produktstart (`scripts/mmo_sim.py --participant`, KEIN
  Harness) mit einem ECHT fortgeschriebenen `medic`-Save -> Fortschritt
  bleibt exakt erhalten (Positivkontrolle, kein Harness-Fix beteiligt).

  test_intact_marker_restart_preserves_progressed_save:
  passiver, echter Harness-Neustart desselben `--data-dir` (Marker bereits
  vorhanden) -> derselbe fortgeschriebene `medic`-Save bleibt erhalten
  (F01-Regression, eigener kleiner Testlauf).

  test_missing_marker_on_started_bestand_is_setup_hold_bytegleich:
  NUR die Markerdatei wird aus einem bereits fortgeschriebenen Root
  entfernt (kein Core-/Store-Write, reine Testmutation) -> SETUP_HOLD
  (rc=3), KEIN neuer Leader, KEINE Fixture-Republikation; der GESAMTE
  relevante Produktbestand (states/onboarding/catalog/registry/run, ohne
  `logs/`) bleibt BYTEGLEICH -- der R8-F03-Kernbeleg.

  test_unreadable_marker_schema_is_setup_hold:
  die Markerdatei wird durch nicht parsebares JSON ersetzt -> SETUP_HOLD,
  kein automatischer Ersatzmarker, Registry/States bleiben unveraendert.

  test_stale_leader_marker_is_setup_hold:
  die Markerdatei verweist auf eine `leader_id`, die in der Registry nicht
  (mehr) aufloesbar ist -> SETUP_HOLD, kein automatisches Neuanlegen dieser
  Identitaet.

  test_mixed_ai_bestand_holds_before_any_partial_write:
  ein Root mit `sniper` komplett unberuehrt ("absent"), `tech` vollstaendig
  ("complete") UND `medic` widerspruechlich ("inconsistent", Current-Save +
  Onboarding-Abschluss vorhanden, Persona-State fehlt) fuehrt zu
  SETUP_HOLD -- UND `sniper` bleibt dabei nachweislich VOLLSTAENDIG
  unberuehrt (kein `make_ready`-Teilwrite, bevor der Abbruch bei `medic`
  ausgeloest wird). Regressionsbeleg fuer BRIEF-W34.md Regel 3 ("nicht erst
  bei Persona 1 schreiben und bei Persona 3 HOLD").

Bestandsaufbau/-korruption nutzt ausschliesslich die bestehenden
`_a24_local_support`-Helfer (`register_human`, `bootstrap_six_persona_
community`, `make_ready`, `core_store.publish_current_save`) -- dieselben
echten Produktwege wie der Harness selbst, keine Fakes an dieser Grenze.
Pure Python, nur `assert`, echter Exitcode, synthetische Temp-Dirs."""
from __future__ import annotations

import copy
import json
import re
import subprocess
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

from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402

import _a24_local_support as sup  # noqa: E402

HARNESS = _HERE / "manual_offline_harness.py"
AI_PERSONAS = ("sniper", "tech", "medic")
_LEADER_ID_RE = re.compile(r"Deine Teilnehmer-ID: (p[0-9a-f]+)")


def _run_harness(data_dir: Path, stdin_text: str, *, extra_args=(), timeout: int = 60) -> subprocess.CompletedProcess:
    cmd = [sys.executable, "-B", str(HARNESS), "--data-dir", str(data_dir), *extra_args]
    return subprocess.run(cmd, input=stdin_text, cwd=str(_REPO_ROOT), capture_output=True, text=True, timeout=timeout)


def _snapshot(data_dir: Path) -> dict:
    """Voller Hashvergleich UEBER die gesamte relevante Produktdateimenge
    (states/onboarding/catalog/registry/run), NICHT nur ein `save_id`-
    String -- unterscheidet Current-Versionen, Persona-State, Onboarding,
    Katalog/Registry, Profil/Admission. `logs/` bewusst ausgeschlossen
    (reine Harness-Bookkeeping-Ablage, keine Spielberechtigung)."""
    merged = {}
    for name in ("states", "onboarding", "catalog", "registry", "run"):
        for relpath, digest in sup.hash_tree(data_dir / name).items():
            merged[f"{name}/{relpath}"] = digest
    return merged


def _prepare_fresh_root_with_progressed_medic(data_dir: Path) -> tuple[str, dict]:
    """Baut einen vollstaendig fortgeschriebenen Root ueber den ECHTEN
    Harness-Prozess (FRESH_EMPTY) + einen ECHT ueber `core.store.
    publish_current_save` publizierten fortgeschrittenen `medic`-Save.
    Liefert `(leader_id, progressed_medic_save)`."""
    p1 = _run_harness(data_dir, "")
    assert p1.returncode == 0, f"frische Erstvorbereitung fehlgeschlagen: rc={p1.returncode}\n{p1.stderr[-2000:]}"
    leader_match = _LEADER_ID_RE.search(p1.stdout)
    assert leader_match, p1.stdout[:500]
    leader_id = leader_match.group(1)

    run_dir = data_dir / "run"
    states_dir = data_dir / "states"
    ps_store = PersonaStateStore(schema_path=sup.SCHEMA)
    old = core_store.load_current_save_or_raise(run_dir, "medic", ps_store, states_dir=states_dir)
    progressed = copy.deepcopy(old)
    progressed["save_id"] = "TEST-UX1-R9-PROGRESSED-MEDIC-SAVE-ONLY"
    progressed["characters"][0]["level"] = 9
    progressed["_r9_progress_marker"] = "PROGRESS_MUST_SURVIVE_SETUP_DECISION"
    core_store.publish_current_save(run_dir, "medic", progressed, ps_store, states_dir)
    bound = core_store.load_current_save_or_raise(run_dir, "medic", ps_store, states_dir=states_dir)
    assert bound == progressed, "echte Publikation des fortgeschrittenen Saves fehlgeschlagen"
    return leader_id, progressed


def test_fresh_empty_prepares_leader_marker_and_ai_bestand():
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        p = _run_harness(data_dir, "")
        assert p.returncode == 0, f"FRESH_EMPTY-Lauf fehlgeschlagen: rc={p.returncode}\n{p.stderr[-2000:]}"

        marker_path = data_dir / "harness_participant.json"
        assert marker_path.is_file(), "FRESH_EMPTY muss den Marker neu anlegen"
        marker_leader_id = json.loads(marker_path.read_text(encoding="utf-8"))["leader_id"]
        leader_match = _LEADER_ID_RE.search(p.stdout)
        assert leader_match, p.stdout[:500]
        assert marker_leader_id == leader_match.group(1)

        status_path = data_dir / "run" / "lab.status.json"
        assert status_path.is_file(), "write_test_profile() muss nach FRESH_EMPTY gelaufen sein"
        status = json.loads(status_path.read_text(encoding="utf-8"))
        assert status.get("provider_free") is True, status

        run_dir = data_dir / "run"
        states_dir = data_dir / "states"
        ps_store = PersonaStateStore(schema_path=sup.SCHEMA)
        for pk in AI_PERSONAS:
            save = core_store.load_current_save_or_raise(run_dir, pk, ps_store, states_dir=states_dir)
            assert save is not None, f"FRESH_EMPTY muss {pk!r} tischbereit machen"
            assert save["save_id"] == f"fixture-{pk}-initial-001", save


def test_normal_product_start_preserves_progressed_save():
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        leader_id, progressed = _prepare_fresh_root_with_progressed_medic(data_dir)

        normal = subprocess.run(
            [sys.executable, "-B", str(sup.MMO_SIM), "--data-dir", str(data_dir), "--participant", leader_id],
            input="", text=True, capture_output=True, timeout=30, cwd=str(_REPO_ROOT),
        )
        assert normal.returncode == 0, (
            f"normaler Produktstart fehlgeschlagen: rc={normal.returncode}\n{normal.stderr[-2000:]}"
        )

        states_dir = data_dir / "states"
        ps_store = PersonaStateStore(schema_path=sup.SCHEMA)
        after = core_store.load_current_save_or_raise(data_dir / "run", "medic", ps_store, states_dir=states_dir)
        assert after == progressed, f"normaler Produktstart hat den fortgeschriebenen Save veraendert: {after}"


def test_intact_marker_restart_preserves_progressed_save():
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        leader_id, progressed = _prepare_fresh_root_with_progressed_medic(data_dir)
        marker_path = data_dir / "harness_participant.json"
        before_marker = marker_path.read_text(encoding="utf-8")

        p2 = _run_harness(data_dir, "")
        assert p2.returncode == 0, f"passiver Neustart fehlgeschlagen: rc={p2.returncode}\n{p2.stderr[-2000:]}"

        assert marker_path.read_text(encoding="utf-8") == before_marker, (
            "ein passiver Neustart mit gueltigem Marker darf keinen neuen Leader registrieren"
        )
        states_dir = data_dir / "states"
        ps_store = PersonaStateStore(schema_path=sup.SCHEMA)
        after = core_store.load_current_save_or_raise(data_dir / "run", "medic", ps_store, states_dir=states_dir)
        assert after == progressed, f"F01-Regression: passiver Neustart hat den Save zurueckgesetzt: {after}"


def test_missing_marker_on_started_bestand_is_setup_hold_bytegleich():
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        _prepare_fresh_root_with_progressed_medic(data_dir)
        marker_path = data_dir / "harness_participant.json"
        assert marker_path.is_file()

        # Explizite Testmutation: NUR die Harness-Bookkeeping-Datei
        # entfernen -- kein Core-/Store-Write, keine echte Spielhandlung.
        marker_path.unlink()
        before = _snapshot(data_dir)

        p3 = _run_harness(data_dir, "")
        assert p3.returncode == 3, (
            "fehlender Marker auf einem bereits begonnenen Bestand muss zu SETUP_HOLD fuehren, "
            f"nicht zu stillem Neuanlegen: rc={p3.returncode}\nstdout={p3.stdout[-1000:]}\n"
            f"stderr={p3.stderr[-1000:]}"
        )
        assert "SETUP-HOLD" in p3.stderr, p3.stderr[-1000:]
        assert "begonnenen Produktbestand" in p3.stderr, p3.stderr[-1000:]

        after = _snapshot(data_dir)
        assert after == before, (
            "R8-F03-Regression: ein fehlender Marker auf fortgeschriebenem Bestand hat Produktdaten "
            f"veraendert. Nur in 'after': {set(after) - set(before)}, nur in 'before': "
            f"{set(before) - set(after)}, geaenderte Hashes: "
            f"{[k for k in before if k in after and before[k] != after[k]]}"
        )
        assert not marker_path.is_file(), "SETUP_HOLD darf keinen Ersatzmarker anlegen"


def test_unreadable_marker_schema_is_setup_hold():
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        _prepare_fresh_root_with_progressed_medic(data_dir)
        marker_path = data_dir / "harness_participant.json"
        registry_dir = data_dir / "registry"
        before_registry_files = sorted(p.name for p in registry_dir.glob("participant__*.json"))

        marker_path.write_text("{dies ist kein gueltiges JSON", encoding="utf-8")
        before = _snapshot(data_dir)

        p = _run_harness(data_dir, "")
        assert p.returncode == 3, f"unlesbarer Marker muss SETUP_HOLD ausloesen: rc={p.returncode}\n{p.stderr[-1000:]}"
        assert "SETUP-HOLD" in p.stderr, p.stderr[-1000:]
        assert "unlesbar" in p.stderr or "falsches Schema" in p.stderr, p.stderr[-1000:]

        after_registry_files = sorted(p.name for p in registry_dir.glob("participant__*.json"))
        assert after_registry_files == before_registry_files, (
            "kein automatischer Ersatz-/Neu-Leader bei unlesbarem Marker"
        )
        assert _snapshot(data_dir) == before, "unlesbarer Marker darf keine Produktdaten veraendern"
        assert marker_path.read_text(encoding="utf-8") == "{dies ist kein gueltiges JSON", (
            "SETUP_HOLD darf den defekten Marker nicht automatisch reparieren"
        )


def test_stale_leader_marker_is_setup_hold():
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        _prepare_fresh_root_with_progressed_medic(data_dir)
        marker_path = data_dir / "harness_participant.json"
        registry_dir = data_dir / "registry"
        before_registry_files = sorted(p.name for p in registry_dir.glob("participant__*.json"))

        bogus_leader_id = "pBOGUS000000DOES0NOT0EXIST"
        marker_path.write_text(json.dumps({"leader_id": bogus_leader_id}), encoding="utf-8")
        before = _snapshot(data_dir)

        p = _run_harness(data_dir, "")
        assert p.returncode == 3, f"staler Leader muss SETUP_HOLD ausloesen: rc={p.returncode}\n{p.stderr[-1000:]}"
        assert "SETUP-HOLD" in p.stderr, p.stderr[-1000:]
        assert bogus_leader_id in p.stderr, p.stderr[-1000:]
        assert "staler Leader" in p.stderr, p.stderr[-1000:]

        after_registry_files = sorted(p.name for p in registry_dir.glob("participant__*.json"))
        assert after_registry_files == before_registry_files, (
            "kein automatisches Neuanlegen der nicht aufloesbaren leader_id"
        )
        assert not any(bogus_leader_id in name for name in after_registry_files)
        assert _snapshot(data_dir) == before, "staler Leader darf keine Produktdaten veraendern"


def test_mixed_ai_bestand_holds_before_any_partial_write():
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        run_dir = data_dir / "run"
        registry_dir = data_dir / "registry"
        marker_path = data_dir / "harness_participant.json"

        # Direkter Bestandsaufbau ueber dieselben echten Produktwege wie der
        # Harness selbst (kein Fake an dieser Grenze) -- gezielt EIN Root
        # mit drei unterschiedlichen Personas-Zustaenden gleichzeitig:
        # sniper bleibt KOMPLETT unberuehrt ("absent"), tech wird
        # vollstaendig tischbereit gemacht ("complete"), medic wird
        # bewusst widerspruechlich gemacht ("inconsistent"). `sniper` wird
        # bewusst NICHT an `bootstrap_six_persona_community` uebergeben --
        # schon die reine Rosteranlage (`bootstrap_community`) schreibt fuer
        # JEDE uebergebene Persona sofort einen States-Stub (Roster-Eintrag,
        # noch keine Figur), VOR jedem `make_ready`-Aufruf. Nur wer hier gar
        # nicht erst im Roster auftaucht, bleibt wirklich "absent" (keine
        # einzige Datei) statt eines rosterbedingten Zwischenzustands.
        leader = sup.register_human(registry_dir, "Testspieler A")
        leader_id = leader.participant_id
        marker_path.write_text(json.dumps({"leader_id": leader_id}), encoding="utf-8")

        ai_boot = sup.bootstrap_six_persona_community(data_dir, f"community-{leader_id}", persona_keys=("tech", "medic"))
        sup.make_ready(ai_boot["onboarding_dir"], ai_boot["states_dir"], ai_boot["run_dir"], "tech")
        sup.make_ready(ai_boot["onboarding_dir"], ai_boot["states_dir"], ai_boot["run_dir"], "medic")
        medic_state_path = ai_boot["states_dir"] / "medic.json"
        assert medic_state_path.is_file()
        medic_state_path.unlink()  # macht medic widerspruechlich (Current+Onboarding vorhanden, State fehlt)

        sniper_onboarding = ai_boot["onboarding_dir"] / "onboarding__sniper.json"
        sniper_state = ai_boot["states_dir"] / "sniper.json"
        sniper_current = run_dir / "current_saves" / "sniper.json"
        sniper_versions = run_dir / "current_saves" / "sniper__versions"
        assert not sniper_onboarding.exists()
        assert not sniper_state.exists()
        assert not sniper_current.exists()
        assert not sniper_versions.exists()

        tech_state_before = (ai_boot["states_dir"] / "tech.json").read_bytes()
        before = _snapshot(data_dir)

        p = _run_harness(data_dir, "")
        assert p.returncode == 3, (
            f"widerspruechlicher medic-Bestand muss SETUP_HOLD ausloesen: rc={p.returncode}\n"
            f"stdout={p.stdout[-1000:]}\nstderr={p.stderr[-1000:]}"
        )
        assert "SETUP-HOLD" in p.stderr, p.stderr[-1000:]
        assert "medic" in p.stderr, p.stderr[-1000:]

        # Kernbeleg Regel 3: sniper (in Aufzaehlungsreihenfolge VOR medic)
        # darf NICHT bereits per `make_ready` beschrieben worden sein, bevor
        # der Abbruch bei medic ausgeloest wurde -- kein Teilwrite.
        assert not sniper_onboarding.exists(), "Teilwrite-Regression: sniper wurde trotz HOLD beschrieben"
        assert not sniper_state.exists(), "Teilwrite-Regression: sniper wurde trotz HOLD beschrieben"
        assert not sniper_current.exists(), "Teilwrite-Regression: sniper wurde trotz HOLD beschrieben"
        assert not sniper_versions.exists(), "Teilwrite-Regression: sniper wurde trotz HOLD beschrieben"

        # tech (bereits "complete") bleibt ebenfalls unberuehrt.
        assert (ai_boot["states_dir"] / "tech.json").read_bytes() == tech_state_before

        assert _snapshot(data_dir) == before, (
            "SETUP_HOLD darf bei einem gemischten KI-Bestand ueberhaupt keine Produktdaten veraendern"
        )
        assert not medic_state_path.is_file(), "kein automatisches Auffuellen des fehlenden medic-States"


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
