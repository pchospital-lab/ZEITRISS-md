#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_r10_passive_teststart_grenze.py — R10/W36 (ZEITRISS
Terminal UX-1, Reparatur R10, BRIEF-W36.md): belegt die geschlossene
passive TESTSTART-Grenze (R9-F01) am ECHTEN `manual_offline_harness.py`-
Subprozess (nicht an einer Testdoppel-Nachbildung).

Befund R9-F01 (REVIEW-DECISION.json, `evidence/probes/probe_profile_
restart`, `evidence/probes/probe_absent_member`): R9 klassifiziert den
GESAMTBESTAND vollstaendig lesend VOR jedem Write (`_classify_harness_
root()`), ABER `write_test_profile()`/`bootstrap_six_persona_community()`/
die `make_ready`-Schleife liefen bisher UNBEDINGT fuer FRESH_EMPTY UND
EXISTING_CONSISTENT -- ein passiver EXISTING-Neustart reautorisierte dadurch
eine zuvor bewusst GESCHLOSSENE Testfreigabe (`provider_free: False` ->
`True`, `probe_profile_restart`) UND fuellte jede noch "absent" KI-Persona
nachtraeglich ueber `make_ready` auf (`probe_absent_member`:
`sniper_current_created=True`, OBWOHL `_classify_harness_root()` das bereits
als `EXISTING_CONSISTENT` einstufte).

Fix (`manual_offline_harness.py`, s. dortige R10/W36-Docstring-Notizen):
`write_test_profile`/`register_human`+Marker/`bootstrap_six_persona_
community`/`make_ready` laufen jetzt AUSSCHLIESSLICH im `FRESH_EMPTY`-Zweig.
`_classify_harness_root()` liefert `EXISTING_CONSISTENT` nur noch, wenn
ZUSAETZLICH (a) ALLE DREI KI-Personas bereits "complete" sind (keine einzige
mehr "absent") UND (b) die bestehende Testfreigabe ueber die unveraenderte,
rein lesende Produktfunktion `admission.read_admission_block(run_dir)` als
NICHT blockiert gilt -- sonst `SETUP_HOLD` (`return 3`), ohne jede
Neu-Autorisierung/Teilwrite.

## Zustandsmatrix (R10/W36, s. REPORT-W36.md fuer die volle Herleitung)

  FRESH   -- Marker absent UND kein begonnener Produktbestand (Registry/
             Onboarding/States/Current/Community). Erstvorbereitung
             (write_test_profile + register_human+Marker +
             bootstrap_six_persona_community + make_ready fuer alle drei)
             bleibt ERLAUBT, ausschliesslich hier. -> rc 0.

  EXISTING -- gueltiger Marker + aufloesbarer Leader + ALLE DREI Personas
             "complete" + offene Testfreigabe (`read_admission_block`
             liefert `blocked=False`). KEIN Write -- nur der echte Client
             startet passiv, Fortschritt (Save/Profil/Marker) bleibt
             bytegleich. -> rc 0 (client rc), kein Harness-Write.

  HOLD    -- jede andere Kombination bei bereits begonnenem Bestand:
             Marker fehlt/unlesbar/staler Leader (R9-erhalten), irgendeine
             KI-Persona "inconsistent" (R9-erhalten), IRGENDEINE KI-Persona
             noch "absent" bei gueltigem Marker (einzeln ODER alle drei,
             R10/W36 NEU), Testfreigabe geschlossen/fehlend/beschaedigt/
             gesperrt bei sonst vollstaendigem Bestand (R10/W36 NEU),
             Produktreste ohne Marker (R9-erhalten, s. dortiger Test). ->
             rc 3, `SETUP-HOLD` in stderr, KEIN Write, KEIN Teilwrite.

Sieben kleine, getrennte Szenarien (je eigener Tempdir), volle Vor-/
Nach-Dateimenge (Profil `run/lab.status.json`, Marker, Roster/Registry,
states, onboarding, catalog, `run/current_saves` inkl. `__versions`-
Archiv) statt nur `save_id`:

  test_fresh_setup_prepares_leader_marker_and_complete_ai_bestand:
  FRESH -> rc 0, Marker + offenes Profil + alle drei KI-Personas
  tischbereit (Fixture-Stand, R9-Parallelbeleg mit vollem Dateiset).

  test_normal_product_start_is_positive_preservation_control:
  normaler, echter Produktstart (`scripts/mmo_sim.py --participant`, KEIN
  Harness) -> VOLLER Snapshot (nicht nur ein Save) bleibt bytegleich
  (Positivkontrolle).

  test_existing_passive_restart_preserves_profile_and_inactive_archive:
  passiver, echter Harness-Neustart eines fortgeschriebenen Bestands
  (Marker + alle drei Personas complete, offenes Profil, medic mit
  fortgeschriebenem Save UND inaktivem `__versions`-Archiv) -> EXISTING,
  `lab.status.json`/Marker BYTE- UND MTIME-STABIL (kein `write_test_
  profile`-Write), kein neuer Leader, kein `make_ready`, VOLLER Snapshot
  (inkl. `__versions`-Archiv) bytegleich -- der zentrale R9-F01/R9P01-
  Regressionsbeleg.

  test_marker_missing_or_unreadable_or_stale_leader_remains_setup_hold_r9:
  kurze R9-Erhaltskontrolle (fehlender/unlesbarer Marker, staler Leader) ->
  weiterhin SETUP_HOLD, nichts veraendert (R9 bleibt unveraendert korrekt,
  keine neue Randfallrunde noetig, 01_AUFTRAG_R10.md).

  test_single_persona_absent_with_valid_marker_is_setup_hold:
  gueltiger Marker/Leader, `tech`+`medic` complete, `sniper` NIE
  bootstrapped ("absent") -- entspricht genau dem belegten
  "absent+complete+complete"-Fall (`probe_absent_member`) -> SETUP_HOLD,
  `sniper` bleibt NACHWEISLICH unberuehrt (kein `make_ready`-Teilwrite),
  `tech`/`medic` ebenfalls unberuehrt.

  test_all_personas_absent_with_valid_marker_is_setup_hold:
  gueltiger Marker/Leader, aber KEINE der drei KI-Personas je bootstrapped
  (abgebrochene/fehlende Gruppe) -> SETUP_HOLD, keine einzige
  Onboarding-/States-/Current-Datei wird angelegt.

  test_closed_test_release_on_complete_bestand_is_setup_hold_no_reauthorization:
  sonst vollstaendiger Bestand (Marker + alle drei Personas complete), aber
  die Testfreigabe wurde explizit GESCHLOSSEN (`provider_free: False`, keine
  Limitfelder -- derselbe Zustand wie `evidence/probes/probe_profile_
  restart`) -> SETUP_HOLD, `lab.status.json` bleibt BYTEGLEICH geschlossen
  (KEINE automatische Neu-Autorisierung auf `provider_free=True`),
  `read_admission_block` bleibt nach dem Harness-Lauf weiterhin blockiert.

  test_locked_or_damaged_test_release_profile_is_setup_hold:
  zwei getrennte Unterfaelle auf je eigenem vollstaendigen Bestand: (a)
  explizit gesperrt ueber `run/lab.stop` (derselbe Mechanismus wie ein
  echter Lab-Stop) UND (b) beschaedigtes `lab.status.json` (kein
  parsebares JSON) -> je SETUP_HOLD, die jeweilige Sperr-/Schadensdatei
  bleibt UNVERAENDERT (keine automatische Reparatur/Entsperrung).

Bestandsaufbau/-korruption nutzt ausschliesslich die bestehenden
`_a24_local_support`-Helfer (`register_human`, `bootstrap_six_persona_
community`, `make_ready`, `core_store.publish_current_save`, `hash_tree`,
`sha256_of`) UND die bestehende, rein lesende `mmo_sim.core.admission.
read_admission_block` -- dieselben echten Produktwege wie der Harness
selbst, keine Fakes an dieser Grenze. Pure Python, nur `assert`, echter
Exitcode, synthetische Temp-Dirs, Testspieler A/Testspieler B- Namensraum."""
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

from mmo_sim.core import admission  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402

import _a24_local_support as sup  # noqa: E402

HARNESS = _HERE / "manual_offline_harness.py"
AI_PERSONAS = ("sniper", "tech", "medic")
_LEADER_ID_RE = re.compile(r"Deine Teilnehmer-ID: (p[0-9a-f]+)")


def _run_harness(data_dir: Path, stdin_text: str, *, extra_args=(), timeout: int = 60) -> subprocess.CompletedProcess:
    cmd = [sys.executable, "-B", str(HARNESS), "--data-dir", str(data_dir), *extra_args]
    return subprocess.run(cmd, input=stdin_text, cwd=str(_REPO_ROOT), capture_output=True, text=True, timeout=timeout)


def _full_snapshot(data_dir: Path) -> dict:
    """Volle relevante Produktdateimenge -- Profil (`run/lab.status.json`),
    Marker, Roster/Registry, states, onboarding, catalog, `run/
    current_saves` INKLUSIVE `__versions`-Archiv -- NICHT nur ein `save_id`-
    String. `logs/` bewusst ausgeschlossen (reine Harness-Bookkeeping-
    Ablage, keine Spielberechtigung, s. R9-Testdatei). Der Marker liegt
    direkt unter `data_dir` (kein Unterordner der fuenf gehashten Baeume),
    wird deshalb separat mit aufgenommen."""
    merged: dict[str, "str | None"] = {}
    for name in ("states", "onboarding", "catalog", "registry", "run"):
        for relpath, digest in sup.hash_tree(data_dir / name).items():
            merged[f"{name}/{relpath}"] = digest
    merged["harness_participant.json"] = sup.sha256_of(data_dir / "harness_participant.json")
    return merged


def _prepare_complete_root(data_dir: Path) -> str:
    """Baut einen vollstaendig tischbereiten Root (Marker + Leader + alle
    drei KI-Personas "complete" + offenes Profil) ueber den ECHTEN
    Harness-Prozess (FRESH_EMPTY). Liefert `leader_id`."""
    p = _run_harness(data_dir, "")
    assert p.returncode == 0, f"frische Erstvorbereitung fehlgeschlagen: rc={p.returncode}\n{p.stderr[-2000:]}"
    leader_match = _LEADER_ID_RE.search(p.stdout)
    assert leader_match, p.stdout[:500]
    return leader_match.group(1)


def _prepare_complete_root_with_progressed_medic(data_dir: Path) -> tuple[str, dict]:
    """Wie `_prepare_complete_root`, zusaetzlich ein ECHT ueber `core.store.
    publish_current_save` fortgeschriebener `medic`-Save (zweite Version im
    `__versions`-Archiv, die erste bleibt die urspruengliche Fixture --
    "inaktives Archiv": beide Versionsdateien bleiben nach einem passiven
    Neustart unberuehrt liegen, nur `current_saves/medic.json` zeigt den
    aktuellen Stand)."""
    leader_id = _prepare_complete_root(data_dir)
    run_dir = data_dir / "run"
    states_dir = data_dir / "states"
    ps_store = PersonaStateStore(schema_path=sup.SCHEMA)
    old = core_store.load_current_save_or_raise(run_dir, "medic", ps_store, states_dir=states_dir)
    progressed = copy.deepcopy(old)
    progressed["save_id"] = "TEST-UX1-R10-PROGRESSED-MEDIC-SAVE-ONLY"
    progressed["characters"][0]["level"] = 11
    progressed["_r10_progress_marker"] = "PROGRESS_MUST_SURVIVE_EXISTING_PASSIVE_RESTART"
    core_store.publish_current_save(run_dir, "medic", progressed, ps_store, states_dir)
    bound = core_store.load_current_save_or_raise(run_dir, "medic", ps_store, states_dir=states_dir)
    assert bound == progressed, "echte Publikation des fortgeschrittenen Saves fehlgeschlagen"
    versions_dir = run_dir / "current_saves" / "medic__versions"
    version_files = sorted(p.name for p in versions_dir.glob("*.json"))
    assert len(version_files) == 2, f"erwartet genau 2 Archivversionen (Fixture + Fortschritt): {version_files}"
    return leader_id, progressed


def test_fresh_setup_prepares_leader_marker_and_complete_ai_bestand():
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        p = _run_harness(data_dir, "")
        assert p.returncode == 0, f"FRESH-Lauf fehlgeschlagen: rc={p.returncode}\n{p.stderr[-2000:]}"

        marker_path = data_dir / "harness_participant.json"
        assert marker_path.is_file(), "FRESH muss den Marker neu anlegen"
        marker_leader_id = json.loads(marker_path.read_text(encoding="utf-8"))["leader_id"]
        leader_match = _LEADER_ID_RE.search(p.stdout)
        assert leader_match, p.stdout[:500]
        assert marker_leader_id == leader_match.group(1)

        status_path = data_dir / "run" / "lab.status.json"
        assert status_path.is_file(), "write_test_profile() muss nach FRESH gelaufen sein"
        status = json.loads(status_path.read_text(encoding="utf-8"))
        assert status.get("provider_free") is True, status
        assert admission.read_admission_block(data_dir / "run")[0] is False, "FRESH muss eine offene Freigabe liefern"

        run_dir = data_dir / "run"
        states_dir = data_dir / "states"
        ps_store = PersonaStateStore(schema_path=sup.SCHEMA)
        for pk in AI_PERSONAS:
            save = core_store.load_current_save_or_raise(run_dir, pk, ps_store, states_dir=states_dir)
            assert save is not None, f"FRESH muss {pk!r} tischbereit machen"
            assert save["save_id"] == f"fixture-{pk}-initial-001", save
            versions_dir = run_dir / "current_saves" / f"{pk}__versions"
            assert sorted(v.name for v in versions_dir.glob("*.json")) == ["0001.json"], (
                f"FRESH darf je Persona genau eine Archivversion anlegen: {pk}"
            )


def test_normal_product_start_is_positive_preservation_control():
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        leader_id, _progressed = _prepare_complete_root_with_progressed_medic(data_dir)
        before = _full_snapshot(data_dir)

        normal = subprocess.run(
            [sys.executable, "-B", str(sup.MMO_SIM), "--data-dir", str(data_dir), "--participant", leader_id],
            input="", text=True, capture_output=True, timeout=30, cwd=str(_REPO_ROOT),
        )
        assert normal.returncode == 0, (
            f"normaler Produktstart fehlgeschlagen: rc={normal.returncode}\n{normal.stderr[-2000:]}"
        )

        after = _full_snapshot(data_dir)
        assert after == before, (
            "normaler Produktstart (kein Harness, Positivkontrolle) hat die volle Produktdateimenge "
            f"veraendert. Nur in 'after': {set(after) - set(before)}, nur in 'before': "
            f"{set(before) - set(after)}, geaenderte Hashes: "
            f"{[k for k in before if k in after and before[k] != after[k]]}"
        )


def test_existing_passive_restart_preserves_profile_and_inactive_archive():
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        leader_id, progressed = _prepare_complete_root_with_progressed_medic(data_dir)
        marker_path = data_dir / "harness_participant.json"
        status_path = data_dir / "run" / "lab.status.json"
        marker_before = marker_path.read_bytes()
        status_before = status_path.read_bytes()
        marker_mtime_before = marker_path.stat().st_mtime_ns
        status_mtime_before = status_path.stat().st_mtime_ns
        before = _full_snapshot(data_dir)

        p = _run_harness(data_dir, "")
        assert p.returncode == 0, f"passiver EXISTING-Neustart fehlgeschlagen: rc={p.returncode}\n{p.stderr[-2000:]}"

        # R10/W36-Kernbeleg (R9-F01/R9P01): kein `write_test_profile`-Write
        # mehr im EXISTING-Zweig -- weder Inhalt NOCH mtime der Freigabe-
        # Datei duerfen sich veraendert haben (ein erneutes Schreiben
        # DESSELBEN Inhalts waere ueber `os.replace` trotzdem eine neue
        # mtime, s. `admission._atomic_write_json`).
        assert status_path.read_bytes() == status_before, "EXISTING darf lab.status.json NICHT neu schreiben"
        assert status_path.stat().st_mtime_ns == status_mtime_before, (
            "EXISTING darf lab.status.json NICHT neu schreiben (mtime-Beleg)"
        )
        assert marker_path.read_bytes() == marker_before, "EXISTING darf keinen neuen Marker/Leader anlegen"
        assert marker_path.stat().st_mtime_ns == marker_mtime_before, (
            "EXISTING darf den Marker NICHT neu schreiben (mtime-Beleg)"
        )

        leader_match = _LEADER_ID_RE.search(p.stdout)
        assert leader_match, p.stdout[:500]
        assert leader_match.group(1) == leader_id, "EXISTING darf keinen neuen Leader registrieren"

        states_dir = data_dir / "states"
        ps_store = PersonaStateStore(schema_path=sup.SCHEMA)
        after_medic = core_store.load_current_save_or_raise(data_dir / "run", "medic", ps_store, states_dir=states_dir)
        assert after_medic == progressed, (
            f"F01-Regression: passiver EXISTING-Neustart hat den Save zurueckgesetzt: {after_medic}"
        )

        after = _full_snapshot(data_dir)
        assert after == before, (
            "R9-F01-Regression: ein passiver EXISTING-Neustart (alle Personas bereits complete, offene "
            "Freigabe) hat die volle Produktdateimenge (inkl. inaktivem __versions-Archiv) veraendert. "
            f"Nur in 'after': {set(after) - set(before)}, nur in 'before': {set(before) - set(after)}, "
            f"geaenderte Hashes: {[k for k in before if k in after and before[k] != after[k]]}"
        )


def test_marker_missing_or_unreadable_or_stale_leader_remains_setup_hold_r9():
    # kurze R9-Erhaltskontrolle (01_AUFTRAG_R10.md: "Konkrete Regressionen
    # statt neuer Randfallrunden") -- die vollen Regressionsbelege dieser
    # drei Faelle leben bereits in
    # test_ux1_r9_setup_hold_classification_2026_10_06.py und werden dort
    # NICHT dupliziert; hier nur eine kompakte Kontrolle, dass der R10-Fix
    # (neue not_complete-/Freigabe-Pruefung) diese drei R9-Faelle nicht
    # beeinflusst hat.
    for mutate_name, mutate in (
        ("marker_missing", lambda marker_path, registry_dir: marker_path.unlink()),
        ("marker_unreadable", lambda marker_path, registry_dir: marker_path.write_text("{nicht valides json")),
        (
            "stale_leader",
            lambda marker_path, registry_dir: marker_path.write_text(
                json.dumps({"leader_id": "pBOGUS0000R10DOES0NOT0EXIST"})
            ),
        ),
    ):
        with tempfile.TemporaryDirectory() as td:
            data_dir = Path(td)
            _prepare_complete_root_with_progressed_medic(data_dir)
            marker_path = data_dir / "harness_participant.json"
            mutate(marker_path, data_dir / "registry")
            before = _full_snapshot(data_dir)

            p = _run_harness(data_dir, "")
            assert p.returncode == 3, (
                f"[{mutate_name}] muss weiterhin SETUP_HOLD ausloesen: rc={p.returncode}\n{p.stderr[-1000:]}"
            )
            assert "SETUP-HOLD" in p.stderr, f"[{mutate_name}] {p.stderr[-1000:]}"
            assert _full_snapshot(data_dir) == before, f"[{mutate_name}] darf keine Produktdaten veraendern"


def test_single_persona_absent_with_valid_marker_is_setup_hold():
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        run_dir = data_dir / "run"
        registry_dir = data_dir / "registry"
        marker_path = data_dir / "harness_participant.json"

        # Derselbe Bestandsaufbau wie `probe_absent_member`
        # (evidence/reproducer/probes_r9.py): `sniper` wird bewusst NICHT an
        # `bootstrap_six_persona_community` uebergeben -- schon die reine
        # Rosteranlage schreibt fuer JEDE uebergebene Persona sofort einen
        # States-Stub, VOR jedem `make_ready`-Aufruf. Nur wer hier gar nicht
        # erst im Roster auftaucht, bleibt wirklich "absent".
        leader = sup.register_human(registry_dir, "Testspieler A")
        leader_id = leader.participant_id
        marker_path.write_text(json.dumps({"leader_id": leader_id}), encoding="utf-8")
        ai_boot = sup.bootstrap_six_persona_community(data_dir, f"community-{leader_id}", persona_keys=("tech", "medic"))
        sup.make_ready(ai_boot["onboarding_dir"], ai_boot["states_dir"], ai_boot["run_dir"], "tech")
        sup.make_ready(ai_boot["onboarding_dir"], ai_boot["states_dir"], ai_boot["run_dir"], "medic")
        admission.write_test_profile(run_dir)

        sniper_onboarding = ai_boot["onboarding_dir"] / "onboarding__sniper.json"
        sniper_state = ai_boot["states_dir"] / "sniper.json"
        sniper_current = run_dir / "current_saves" / "sniper.json"
        assert not sniper_onboarding.exists() and not sniper_state.exists() and not sniper_current.exists()

        tech_state_before = (ai_boot["states_dir"] / "tech.json").read_bytes()
        medic_state_before = (ai_boot["states_dir"] / "medic.json").read_bytes()
        before = _full_snapshot(data_dir)

        p = _run_harness(data_dir, "")
        assert p.returncode == 3, (
            "genau EINE fehlende Persona (sniper=absent, tech/medic=complete -- der belegte "
            f"'absent+complete+complete'-Fall) muss SETUP_HOLD ausloesen: rc={p.returncode}\n"
            f"stdout={p.stdout[-1000:]}\nstderr={p.stderr[-1000:]}"
        )
        assert "SETUP-HOLD" in p.stderr, p.stderr[-1000:]
        assert "sniper" in p.stderr, p.stderr[-1000:]

        assert not sniper_onboarding.exists(), "R9-F01-Regression: sniper wurde trotz HOLD per make_ready beschrieben"
        assert not sniper_state.exists(), "R9-F01-Regression: sniper wurde trotz HOLD per make_ready beschrieben"
        assert not sniper_current.exists(), "R9-F01-Regression: sniper wurde trotz HOLD per make_ready beschrieben"
        assert (ai_boot["states_dir"] / "tech.json").read_bytes() == tech_state_before
        assert (ai_boot["states_dir"] / "medic.json").read_bytes() == medic_state_before
        assert _full_snapshot(data_dir) == before, (
            "SETUP_HOLD darf bei genau einer fehlenden Persona ueberhaupt keine Produktdaten veraendern"
        )


def test_all_personas_absent_with_valid_marker_is_setup_hold():
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        registry_dir = data_dir / "registry"
        marker_path = data_dir / "harness_participant.json"

        # Gueltiger Marker/Leader, aber abgebrochene/fehlende KI-Gruppe --
        # KEINE der drei Personas wurde je bootstrapped (kein einziger
        # Onboarding-/States-/Current-Eintrag).
        leader = sup.register_human(registry_dir, "Testspieler A")
        leader_id = leader.participant_id
        marker_path.write_text(json.dumps({"leader_id": leader_id}), encoding="utf-8")

        onboarding_dir = data_dir / "onboarding"
        states_dir = data_dir / "states"
        catalog_dir = data_dir / "catalog"
        for pk in AI_PERSONAS:
            assert not (onboarding_dir / f"onboarding__{pk}.json").exists()
            assert not (states_dir / f"{pk}.json").exists()
        before = _full_snapshot(data_dir)

        p = _run_harness(data_dir, "")
        assert p.returncode == 3, (
            f"alle drei Personas absent bei gueltigem Marker/Leader muss SETUP_HOLD ausloesen: "
            f"rc={p.returncode}\nstdout={p.stdout[-1000:]}\nstderr={p.stderr[-1000:]}"
        )
        assert "SETUP-HOLD" in p.stderr, p.stderr[-1000:]
        for pk in AI_PERSONAS:
            assert pk in p.stderr, p.stderr[-1000:]
            assert not (onboarding_dir / f"onboarding__{pk}.json").exists(), (
                f"kein automatisches Auffuellen von {pk!r} bei abgebrochener/fehlender Gruppe"
            )
            assert not (states_dir / f"{pk}.json").exists()
        assert not catalog_dir.exists() or not any(catalog_dir.rglob("*"))
        assert _full_snapshot(data_dir) == before, (
            "SETUP_HOLD darf bei einer komplett fehlenden KI-Gruppe ueberhaupt keine Produktdaten veraendern"
        )


def test_closed_test_release_on_complete_bestand_is_setup_hold_no_reauthorization():
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        _prepare_complete_root(data_dir)
        status_path = data_dir / "run" / "lab.status.json"

        # Derselbe Zustand wie `evidence/probes/probe_profile_restart`:
        # Testfreigabe explizit GESCHLOSSEN (provider_free=False, keine
        # Limitfelder) -- ein echter Client wuerde an dieser Stelle JEDEN
        # Request blockieren (admission.read_admission_block -> blocked).
        data = json.loads(status_path.read_text(encoding="utf-8"))
        data["provider_free"] = False
        for k in ("max_turns", "max_seconds", "max_usd"):
            data.pop(k, None)
        status_path.write_text(json.dumps(data, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        status_before = status_path.read_bytes()
        assert admission.read_admission_block(data_dir / "run")[0] is True, "Vorbedingung: Freigabe muss geschlossen sein"
        before = _full_snapshot(data_dir)

        p = _run_harness(data_dir, "")
        assert p.returncode == 3, (
            f"geschlossene Testfreigabe auf sonst vollstaendigem Bestand muss SETUP_HOLD ausloesen (R9-F01/"
            f"R9P01-Regression): rc={p.returncode}\nstdout={p.stdout[-1000:]}\nstderr={p.stderr[-1000:]}"
        )
        assert "SETUP-HOLD" in p.stderr, p.stderr[-1000:]

        # Kernbeleg: KEINE automatische Neu-Autorisierung -- vorher setzte
        # `write_test_profile()` hier unbedingt `provider_free=True`.
        assert status_path.read_bytes() == status_before, (
            "R9-F01-Regression: eine geschlossene Testfreigabe wurde bei einem passiven Neustart "
            "automatisch neu autorisiert"
        )
        assert json.loads(status_path.read_text(encoding="utf-8")).get("provider_free") is False
        assert admission.read_admission_block(data_dir / "run")[0] is True, (
            "die Freigabe muss nach dem Harness-Lauf weiterhin blockiert sein"
        )
        assert _full_snapshot(data_dir) == before, "SETUP_HOLD darf bei geschlossener Freigabe nichts veraendern"


def test_locked_or_damaged_test_release_profile_is_setup_hold():
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        _prepare_complete_root(data_dir)
        stop_path = data_dir / "run" / "lab.stop"
        stop_path.write_text(json.dumps({"reason": "R10-W36-Testsperre (SIMULIERT)"}), encoding="utf-8")
        stop_before = stop_path.read_bytes()
        status_path = data_dir / "run" / "lab.status.json"
        status_before = status_path.read_bytes()
        before = _full_snapshot(data_dir)

        p = _run_harness(data_dir, "")
        assert p.returncode == 3, f"explizit gesperrtes Profil (lab.stop) muss SETUP_HOLD ausloesen: rc={p.returncode}\n{p.stderr[-1000:]}"
        assert "SETUP-HOLD" in p.stderr, p.stderr[-1000:]
        assert stop_path.read_bytes() == stop_before, "eine bestehende Sperre darf nicht automatisch entfernt werden"
        assert status_path.read_bytes() == status_before, "eine gesperrte Freigabe darf nicht neu autorisiert werden"
        assert _full_snapshot(data_dir) == before, "SETUP_HOLD darf bei einer gesperrten Freigabe nichts veraendern"

    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        _prepare_complete_root(data_dir)
        status_path = data_dir / "run" / "lab.status.json"
        status_path.write_text("{dies ist kein gueltiges JSON mehr", encoding="utf-8")
        status_before = status_path.read_bytes()
        before = _full_snapshot(data_dir)

        p = _run_harness(data_dir, "")
        assert p.returncode == 3, f"beschaedigtes Profil muss SETUP_HOLD ausloesen: rc={p.returncode}\n{p.stderr[-1000:]}"
        assert "SETUP-HOLD" in p.stderr, p.stderr[-1000:]
        assert status_path.read_bytes() == status_before, (
            "ein beschaedigtes Profil darf nicht automatisch repariert/ueberschrieben werden"
        )
        assert _full_snapshot(data_dir) == before, "SETUP_HOLD darf bei einem beschaedigten Profil nichts veraendern"


def test_closed_profile_without_marker_is_setup_hold():
    """R10/W37 (C17-F01, BRIEF-W37.md, REPORT-C17.md): Root OHNE Marker,
    OHNE sonstigen Bestand (keine Registry/Onboarding/States/Catalog/
    Current/Community), aber mit einem bereits VORHANDENEN, bewusst
    GESCHLOSSENEN Testprofil (`run/lab.status.json`, `provider_free:
    False`) -- derselbe Zustand wie `material/
    c17_finding_fresh_profile_repro.py`. VOR dem C17-Fix stufte
    `_root_has_started_product_bestand()` das nicht als begonnenen
    Bestand ein, der marker-absent-Zweig lief als `FRESH_EMPTY`, und
    `write_test_profile()` setzte die Freigabe STILL wieder auf
    `provider_free=True` zurueck (stille Reautorisierung, kein Harness-
    Write war dafuer "sichtbar"). Fix: ein vorhandenes Profil (`run/
    lab.status.json` ODER `run/lab.stop`) zaehlt jetzt als begonnener
    Bestand -> SETUP_HOLD, KEIN `write_test_profile`-Aufruf mehr,
    `provider_free` bleibt bytegleich `False`."""
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        run_dir = data_dir / "run"
        marker_path = data_dir / "harness_participant.json"

        # Profil vorbereiten (offen) und dann explizit schliessen --
        # derselbe Mechanismus wie `test_closed_test_release_on_complete_
        # bestand_is_setup_hold_no_reauthorization`, aber hier OHNE Marker
        # und OHNE jeden weiteren Bestand (reine marker-absent-Grenze).
        admission.write_test_profile(run_dir)
        status_path = run_dir / "lab.status.json"
        data = json.loads(status_path.read_text(encoding="utf-8"))
        data["provider_free"] = False
        for k in ("max_turns", "max_seconds", "max_usd"):
            data.pop(k, None)
        status_path.write_text(json.dumps(data, sort_keys=True, indent=2) + "\n", encoding="utf-8")

        assert not marker_path.exists(), "Vorbedingung: kein Marker"
        assert admission.read_admission_block(run_dir)[0] is True, "Vorbedingung: Freigabe muss geschlossen sein"
        status_before = status_path.read_bytes()
        before = _full_snapshot(data_dir)

        p = _run_harness(data_dir, "")
        assert p.returncode == 3, (
            f"C17-F01: geschlossenes Profil ohne Marker, sonst leerer Root, muss SETUP_HOLD ausloesen "
            f"(nicht FRESH): rc={p.returncode}\nstdout={p.stdout[-1000:]}\nstderr={p.stderr[-1000:]}"
        )
        assert "SETUP-HOLD" in p.stderr, p.stderr[-1000:]

        # Kernbeleg C17-F01: KEINE automatische Neu-Autorisierung mehr.
        assert status_path.read_bytes() == status_before, (
            "C17-F01-Regression: ein marker-absent-Root mit bereits vorhandenem, geschlossenem Profil "
            "wurde still reautorisiert (provider_free faelschlich wieder True)"
        )
        assert json.loads(status_path.read_text(encoding="utf-8")).get("provider_free") is False
        assert admission.read_admission_block(run_dir)[0] is True, (
            "die Freigabe muss nach dem Harness-Lauf weiterhin blockiert sein"
        )
        assert not marker_path.exists(), "SETUP_HOLD darf bei fehlendem Bestand keinen neuen Marker anlegen"
        assert _full_snapshot(data_dir) == before, "SETUP_HOLD darf das vorhandene Profil nicht veraendern"


def test_open_profile_without_marker_is_setup_hold():
    """R10/W37 (C17-F01, BRIEF-W37.md): Root OHNE Marker, OHNE sonstigen
    Bestand, aber mit einem bereits VORHANDENEN, OFFENEN Testprofil
    (`provider_free: True`). Ein vorhandenes Profil zaehlt als begonnener
    Bestand UNABHAENGIG vom offen/geschlossen-Zustand -- auch hier darf
    keine stille Uebernahme/Neuanlage von Marker/Leader/Personas
    stattfinden, der Lauf muss weiterhin SETUP_HOLD liefern (kein
    impliziter FRESH-Shortcut nur weil die Freigabe zufaellig offen
    ist)."""
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        run_dir = data_dir / "run"
        marker_path = data_dir / "harness_participant.json"

        admission.write_test_profile(run_dir)
        status_path = run_dir / "lab.status.json"
        assert admission.read_admission_block(run_dir)[0] is False, "Vorbedingung: Freigabe muss offen sein"
        assert not marker_path.exists(), "Vorbedingung: kein Marker"
        status_before = status_path.read_bytes()
        before = _full_snapshot(data_dir)

        p = _run_harness(data_dir, "")
        assert p.returncode == 3, (
            f"C17-F01: offenes Profil ohne Marker, sonst leerer Root, muss SETUP_HOLD ausloesen "
            f"(vorhandenes Profil = begonnener Bestand, keine stille Uebernahme): rc={p.returncode}\n"
            f"stdout={p.stdout[-1000:]}\nstderr={p.stderr[-1000:]}"
        )
        assert "SETUP-HOLD" in p.stderr, p.stderr[-1000:]
        assert status_path.read_bytes() == status_before, (
            "SETUP_HOLD darf das vorhandene, bereits offene Profil nicht neu schreiben"
        )
        assert not marker_path.exists(), "SETUP_HOLD darf bei fehlendem Bestand keinen neuen Marker anlegen"
        assert _full_snapshot(data_dir) == before, "SETUP_HOLD darf das vorhandene Profil nicht veraendern"


def test_truly_empty_root_without_profile_remains_fresh():
    """R10/W37 (C17-F01, Regression): ein WIRKLICH leerer Root -- kein
    Marker, KEIN Profil (`run/lab.status.json`/`run/lab.stop` existieren
    noch nicht), kein sonstiger Bestand -- muss trotz des C17-Fixes
    weiterhin FRESH_EMPTY klassifiziert werden: `_classify_harness_root()`
    laeuft nachweislich VOR `write_test_profile()` (BRIEF-W37.md), zum
    Klassifikationszeitpunkt kann der neue Profil-Check in
    `_root_has_started_product_bestand()` also gar nicht auf ein bereits
    existierendes Profil treffen. rc 0, Marker+Profil+alle drei
    KI-Personas werden wie bisher korrekt tischbereit gemacht (volle
    Vor-/Nach-Dateimenge, nicht nur rc)."""
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        marker_path = data_dir / "harness_participant.json"
        status_path = data_dir / "run" / "lab.status.json"
        assert not marker_path.exists() and not status_path.exists(), "Vorbedingung: wirklich leerer Root"
        assert not (data_dir / "run").exists(), "Vorbedingung: noch kein run/-Ordner"

        p = _run_harness(data_dir, "")
        assert p.returncode == 0, (
            f"C17-F01-Regression: ein wirklich leerer Root (kein Profil) darf nicht zu SETUP_HOLD "
            f"werden: rc={p.returncode}\nstdout={p.stdout[-1000:]}\nstderr={p.stderr[-1000:]}"
        )
        assert marker_path.is_file(), "FRESH muss den Marker neu anlegen"
        assert status_path.is_file(), "FRESH muss write_test_profile() ausfuehren"
        status = json.loads(status_path.read_text(encoding="utf-8"))
        assert status.get("provider_free") is True, status
        assert admission.read_admission_block(data_dir / "run")[0] is False, "FRESH muss eine offene Freigabe liefern"

        run_dir = data_dir / "run"
        states_dir = data_dir / "states"
        ps_store = PersonaStateStore(schema_path=sup.SCHEMA)
        for pk in AI_PERSONAS:
            save = core_store.load_current_save_or_raise(run_dir, pk, ps_store, states_dir=states_dir)
            assert save is not None, f"FRESH muss {pk!r} tischbereit machen"
            assert save["save_id"] == f"fixture-{pk}-initial-001", save


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
