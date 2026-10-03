#!/usr/bin/env python3
"""
tests/mmo_sim/test_i4_reference_contract.py — I4-Referenzvertrag (2026-09-25,
Vertrag §3 A/B Rest A/B; externe Abnahme review_i4_reference_contract.py,
02_ABNAHME Faelle 1-7).

Ergaenzt `test_i4_current_readpaths.py` (deckt die Verbraucher-Anschluesse ab,
UNVERAENDERT) und `test_i4_figure_continuity.py`/`test_i4_active_authority_
subprocess.py` (Aktivautoritaets-/Bindungsseite) um die Feld-/Absenzmatrix der
strengen Referenzkette selbst (`store._current_save_version_path_or_raise`
ueber `store._persona_state_or_raise`/`store._has_publication_trail`):

  - Stateobjekt: echte Absenz OHNE eigene Publikationsspur bleibt `None`
    (Erstzustand); echte Absenz MIT vorhandener Spur sperrt (Fall 02).
  - Ref: fehlender Schluessel/`null`/leeres Objekt/fehlende/`null`-Sequenz
    sperren bei vorhandener Spur (Fall 03), bleiben ohne Spur `None`.
  - Bereich: eine formal gueltige Ref auf einen ANDEREN tatsaechlich
    angelegten `run_id`-Bereich sperrt, statt den lokalen Bereich zu erben
    oder den alten Onboardingstand freizugeben (Fall 04).
  - Sequenz: nur ein echter `int` (kein `bool`, keine Bruchzahl) ist eine
    gueltige Producerform; ungueltige Werte sperren ohne `int()`-Coerce auf
    eine bestehende aeltere Version (Fall 05) -- ein gueltiger `int` bleibt
    unveraendert lesbar (Regressionsschutz gegen Ueberkorrektur).
  - referenzierte Version: eine gueltige Ref, deren Versionsdatei fehlt,
    sperrt (ergänzt die bereits bestehende Kontrolle 06 in
    `test_i4_current_readpaths.py`/`test_i4_active_authority_subprocess.py`).
  - Positivfall: ein wirklich neuer Teilnehmer ohne eigene Publikationsspur
    darf in einer bereits bestehenden Community weiterhin starten (Fall 07).

Direkte Aufrufe der strengen Lesehilfe UND reale I4-Verbraucher
(`TuiSession._cmd_export`/`_cmd_import`) -- teils im selben Prozess, teils
ueber ECHTE neue Interpreterprozesse (`subprocess.run([sys.executable,
__file__, '--child', ...])`, analog zum bereits etablierten Muster in
`test_i4_active_authority_subprocess.py`). Rein synthetische Fixtures, kein
Netz-/Modellzugriff.

Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import argparse
import copy
import json
import os
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

import test_i4_figure_continuity as t4  # noqa: E402
from mmo_sim.core import store  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"

_pa = argparse.ArgumentParser(add_help=False)
_pa.add_argument("--child", choices=["export", "keep_import", "select_back"])
_pa.add_argument("--base", type=Path)
_pa.add_argument("--target")
_ARGS, _REMAINING = _pa.parse_known_args()


def _ps() -> PersonaStateStore:
    return PersonaStateStore(_SCHEMA)


def _strict(base: Path, pk: str = "sniper") -> tuple[dict | None, Exception | None]:
    try:
        return store.load_current_save_or_raise(base / "run", pk, _ps(), states_dir=base / "states"), None
    except Exception as e:  # noqa: BLE001 -- die Exception-Identitaet selbst wird geprueft.
        return None, e


def _setup(base: Path):
    """Ein Rig mit 'sniper' UND ein echter Abschnittsabschluss etablieren
    A_neu (seq=2) als veroeffentlichten Current mit eigener Publikationsspur
    -- identisches Muster zu `test_i4_figure_continuity._progressed`."""
    r = t4.Rig(base, ("sniper",))
    anew = t4._progressed(r)
    return r, anew


def _versions_dir(base: Path, pk: str = "sniper") -> Path:
    return base / "run" / "current_saves" / f"{pk}__versions"


def _ui(base: Path, inputs=(), shown=None) -> TuiSession:
    return TuiSession(
        base / "onboarding", base / "catalog", "sniper", input_fn=t4._script(inputs),
        print_fn=(shown.append if shown is not None else (lambda _x: None)),
        run_dir=base / "run", states_dir=base / "states", schema_path=_SCHEMA,
    )


# ── Stateobjekt ──────────────────────────────────────────────────────────────

def test_state_absent_with_trail_blocks_instead_of_first_setup():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r, anew = _setup(base)
        state_path = base / "states" / "sniper.json"
        original = state_path.read_bytes()
        archive = base / "parked-state.json"
        state_path.replace(archive)
        versions_before = sorted(p.name for p in _versions_dir(base).glob("*.json"))

        save, err = _strict(base)
        assert save is None and isinstance(err, store.CurrentSaveUnavailableError), \
            "fehlender State bei vorhandener Publikationsspur muss sperren, nicht Erstzustand liefern"
        assert archive.read_bytes() == original, "das geparkte Original bleibt unveraendert (kein Test-Fix am Produkt)"
        assert sorted(p.name for p in _versions_dir(base).glob("*.json")) == versions_before, \
            "die vorhandene Publikationsspur selbst darf durch das strenge Lesen nicht veraendert werden"


def test_state_absent_without_trail_is_genuine_first_setup():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        # Kein Rig/_progressed -- 'sniper' hat hier NIE publiziert, run_dir
        # existiert noch nicht einmal.
        save, err = _strict(base)
        assert save is None and err is None, \
            "ohne jede eigene Publikationsspur bleibt fehlender State der legitime Erstzustand"
        assert not (base / "run" / "run_id.json").exists(), \
            "das strenge Lesen selbst darf niemals eine run_id initialisieren"


# ── Ref ──────────────────────────────────────────────────────────────────────

def test_ref_missing_variants_block_when_trail_present():
    for variant in ("missing-key", "null-ref", "empty-ref", "missing-seq", "null-seq"):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            r, anew = _setup(base)
            state_path = base / "states" / "sniper.json"
            st = json.loads(state_path.read_text(encoding="utf-8"))
            if variant == "missing-key":
                st.pop("current_save_version")
            elif variant == "null-ref":
                st["current_save_version"] = None
            elif variant == "empty-ref":
                st["current_save_version"] = {}
            elif variant == "missing-seq":
                st["current_save_version"].pop("seq")
            elif variant == "null-seq":
                st["current_save_version"]["seq"] = None
            state_path.write_text(json.dumps(st), encoding="utf-8")

            save, err = _strict(base)
            assert save is None and isinstance(err, store.CurrentSaveUnavailableError), \
                f"Variante {variant!r}: fehlende/mangelhafte Ref bei vorhandener Spur muss sperren"


def test_ref_absent_without_trail_is_none():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        # Rig legt den Persona-State an (Fixture-Onboardingstand), OHNE
        # jemals zu publizieren -- current_save_version wurde bereits in
        # Rig.__init__ entfernt, keine eigene Versionsspur existiert.
        t4.Rig(base, ("sniper",))
        save, err = _strict(base)
        assert save is None and err is None, \
            "ein Persona-State ohne jede eigene Ref UND ohne Publikationsspur bleibt Erstzustand"


# ── Bereich ──────────────────────────────────────────────────────────────────

def test_ref_to_foreign_run_blocks_instead_of_old_export():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r, anew = _setup(base)
        other = base / "other-run"
        other.mkdir()
        foreign = copy.deepcopy(anew)
        foreign["save_id"] = "synthetic-current-in-other-run"
        store.publish_current_save(other, "sniper", foreign, _ps(), base / "states")

        save, err = _strict(base)
        assert save is None and isinstance(err, store.CurrentSaveUnavailableError), \
            "eine Ref auf einen anderen tatsaechlich angelegten run_id-Bereich muss sperren"
        # Der lokale Bereich bleibt unveraendert -- kein Erben/Umschreiben.
        local_run_id = json.loads((base / "run" / "run_id.json").read_text())["run_id"]
        other_run_id = json.loads((other / "run_id.json").read_text())["run_id"]
        assert local_run_id != other_run_id


# ── Sequenz ──────────────────────────────────────────────────────────────────

def test_sequence_bool_and_float_block_no_coerce():
    for value in (True, 1.75):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            r, anew = _setup(base)
            state_path = base / "states" / "sniper.json"
            st = json.loads(state_path.read_text(encoding="utf-8"))
            assert st["current_save_version"]["seq"] > 1
            st["current_save_version"]["seq"] = value
            state_path.write_text(json.dumps(st), encoding="utf-8")

            save, err = _strict(base)
            assert save is None and isinstance(err, store.CurrentSaveUnavailableError), \
                f"seq={value!r} ({type(value).__name__}) darf nicht auf eine aeltere Version gekuerzt werden"
            # 0001.json (die urspruengliche Importfassung) bleibt unberuehrt/ungewaehlt.
            assert (_versions_dir(base) / "0001.json").exists()


def test_sequence_valid_int_reads_normally():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r, anew = _setup(base)
        save, err = _strict(base)
        assert err is None and save == anew, \
            "eine gueltige int-Sequenz ist weiterhin eine unterstuetzte Producerform (kein Ueberkorrigieren)"


# ── referenzierte Version ────────────────────────────────────────────────────

def test_referenced_version_file_missing_blocks():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r, anew = _setup(base)
        state = _ps().load_state("sniper", states_dir=base / "states")
        seq = state["current_save_version"]["seq"]
        version_path = _versions_dir(base) / f"{seq:04d}.json"
        original = version_path.read_bytes()
        version_path.unlink()

        save, err = _strict(base)
        assert save is None and isinstance(err, store.CurrentSaveUnavailableError), \
            "eine gueltige, aber fehlende referenzierte Versionsdatei muss sperren, kein stiller Rueckfall"
        # Kein Ersatzwrite entstanden.
        assert not version_path.exists()
        assert len(original) > 0


# ── Positivfall (Fall 07) ────────────────────────────────────────────────────

def test_genuine_first_participant_in_existing_community_allowed():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r, anew = _setup(base)
        before_existing = _strict(base)[0]
        pk = "newhuman"
        empty_save, empty_err = _strict(base, pk)
        assert empty_save is None and empty_err is None

        initial = t4._sv("tech")
        shown: list = []
        # `_ui` baut die Session fuer 'sniper' -- ein zweiter Teilnehmer
        # braucht eine eigene Session-Instanz mit passender participant_id.
        TuiSession(
            base / "onboarding", base / "catalog", pk, input_fn=t4._script([json.dumps(initial), "ENDE"]),
            print_fn=shown.append, run_dir=base / "run", states_dir=base / "states", schema_path=_SCHEMA,
        )._cmd_import()

        after_save, after_err = _strict(base, pk)
        assert after_err is None and after_save == initial, \
            "ein wirklich neuer Teilnehmer ohne eigene Publikationsspur darf in bestehender Community starten"
        assert _strict(base)[0] == before_existing, \
            "der bereits bestehende Teilnehmer bleibt durch den neuen Import unveraendert"


# ── echte neue Interpreterprozesse ───────────────────────────────────────────

def _run_child(base: Path, mode: str, extra: list[str] | None = None) -> dict:
    cmd = [sys.executable, str(Path(__file__).resolve()), "--child", mode, "--base", str(base)]
    if extra:
        cmd += extra
    env = {k: v for k, v in os.environ.items() if not any(t in k.upper() for t in ("TOKEN", "SECRET", "API_KEY"))}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    res = subprocess.run(cmd, cwd=base, env=env, text=True, capture_output=True, timeout=45)
    if res.returncode:
        raise RuntimeError(f"child failed rc={res.returncode}\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}")
    return json.loads(res.stdout)


def _child_export(base: Path) -> None:
    shown: list = []
    _ui(base, shown=shown)._cmd_export()
    exp = base / "exports" / "sniper.json"
    print(json.dumps({
        "shown": shown,
        "export": json.loads(exp.read_text()) if exp.exists() else None,
    }, ensure_ascii=False))


def _child_keep_import(base: Path) -> None:
    proposal = copy.deepcopy(t4._sv("sniper"))
    proposal["save_id"] = "synthetic-external-proposal"
    shown: list = []
    _ui(base, [json.dumps(proposal), "ENDE", "k"], shown)._cmd_import()
    print(json.dumps({"shown": shown}, ensure_ascii=False))


def test_subprocess_export_blocks_after_state_removed_with_trail():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r, anew = _setup(base)
        state_path = base / "states" / "sniper.json"
        state_path.replace(base / "parked-state.json")
        before_exports = list((base / "exports").glob("*.json")) if (base / "exports").exists() else []

        result = _run_child(base, "export")
        assert any("Export abgebrochen" in s for s in result["shown"]), \
            f"echter neuer Prozess muss den Export kontrolliert ablehnen: {result['shown']}"
        assert result["export"] is None
        after_exports = list((base / "exports").glob("*.json")) if (base / "exports").exists() else []
        assert after_exports == before_exports, "kein Exportfile darf durch den geblockten Versuch entstehen"


def test_subprocess_keep_import_does_not_republish_after_broken_ref():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r, anew = _setup(base)
        state_path = base / "states" / "sniper.json"
        st = json.loads(state_path.read_text(encoding="utf-8"))
        st["current_save_version"] = None
        broken_bytes = json.dumps(st).encode("utf-8")
        state_path.write_bytes(broken_bytes)

        result = _run_child(base, "keep_import")
        assert any("Import abgebrochen" in s for s in result["shown"]), \
            f"echter neuer Prozess darf 'k' nicht als Republish des Onboardingstands durchlaufen: {result['shown']}"
        assert state_path.read_bytes() == broken_bytes, "kein stiller Reparatur-/Ersatzwrite am State"


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
    if _ARGS.child == "export":
        _child_export(_ARGS.base)
        raise SystemExit(0)
    if _ARGS.child == "keep_import":
        _child_keep_import(_ARGS.base)
        raise SystemExit(0)
    raise SystemExit(main())
