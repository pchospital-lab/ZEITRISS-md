#!/usr/bin/env python3
"""
tests/mmo_sim/test_i4_current_readpaths.py — I4-Nachzug: durchgaengige
Current-Lesewege bis zum tatsaechlichen Verbraucher (Vertrag §3 A/B, R1/R2;
externe Abnahme 02_ABNAHME_I4-CURRENTLESEWEGE Faelle 1-7).

Ergaenzt `test_i4_figure_continuity.py` und
`test_i4_active_authority_subprocess.py` (beide unveraendert -- decken vor
allem die Aktivautoritaets-/Bindungsseite an `_switch_active_figure`/
`_cmd_new_or_switch_character`/`_resolve_real_active_chrononaut_id` ab, mit
Fehlerinjektionen ueberwiegend an der referenzierten Versionsdatei) um eine
Matrix der tatsaechlich maßgeblichen LESESTELLEN/VERBRAUCHER, die zuvor den
fehlertoleranten `store.load_current_save` verwendeten:

  - `TuiSession._resolve_active_save` -> `_cmd_import`s Konfliktbasis
    (VOR jeder a/k-Wahl und jedem Zielsave-Write).
  - `TuiSession._resolve_active_save` -> `_cmd_local_round._resolve_member`,
    fuer LEADER UND GAST (dieselbe Autoritaet, geteilter Code).
  - `TuiSession._cmd_export` (`store.load_current_save_or_raise` direkt).
  - `store._current_save_version_path_or_raise`s GANZE Referenzkette
    (Persona-State + run_id + Ref-Abgleich, nicht nur die zuletzt
    referenzierte Versionsdatei) -- zusaetzlich zum bereits bestehenden
    `test_i4aa_weg4_current_read_error_blocks_instead_of_silent_reset`
    (Versions-Lesefehler) hier: gewoehnlicher run_id.json-Lesefehler UND
    transienter Persona-State-Absenzfehler an `_switch_active_figure`.

Fuer jede Stelle: gesunder Pfad (keine Fehlerinjektion) UND ein einmaliger
gewoehnlicher Lese-/Absenzfehler an einer TATSAECHLICH vorhandenen Datei
(Original bleibt intakt, nur der EINE Zugriff schlaegt fehl) -- sowie der
echte Erstzustand (kein run_id-Init-Write, `load_current_save_or_raise`
selbst initialisiert nichts). Kein Test schwaecht eine Assertion ab; jede
Injektion wird ueber einen Trefferzaehler tatsaechlich verifiziert.

Pure Python, nur `assert`, echter Exitcode. Providerfrei (synthetisches
GM-/Treiber-Double, kein externer Modellaufruf, kein HTTP)."""
from __future__ import annotations

import builtins
import contextlib
import json
import sys
import tempfile
import traceback
from pathlib import Path
from unittest.mock import patch

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import test_i4_figure_continuity as t4  # noqa: E402
from mmo_sim.core import store  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, saves  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


def _ps() -> PersonaStateStore:
    return PersonaStateStore(_SCHEMA)


def _cur(base: Path, pk: str = "sniper") -> dict | None:
    return store.load_current_save(base / "run", pk, _ps(), states_dir=base / "states")


def _version_path(base: Path, pk: str = "sniper") -> Path:
    state = _ps().load_state(pk, states_dir=base / "states")
    ref = state["current_save_version"]
    return base / "run" / "current_saves" / f"{pk}__versions" / f"{int(ref['seq']):04d}.json"


def _setup(base: Path):
    """Rig mit 'sniper' als einzigem Rig-Mitglied, ein echter Abschnitts-
    abschluss etabliert A_neu als veroeffentlichten Current (identisches
    Muster zu `test_i4_figure_continuity._progressed`)."""
    r = t4.Rig(base, ("sniper",))
    anew = t4._progressed(r)
    return r, anew


@contextlib.contextmanager
def _inject_version_read_error(version_path: Path):
    """Genau EIN gewoehnlicher `OSError` beim Lesen der referenzierten,
    TATSAECHLICH vorhandenen Versionsdatei -- die Datei selbst bleibt
    unveraendert auf der Platte."""
    original = Path.read_text
    hit = [0]

    def _fail(path, *a, **kw):
        if path == version_path and hit[0] == 0:
            hit[0] += 1
            raise OSError("INJECT ordinary one-shot version read failure")
        return original(path, *a, **kw)

    with patch.object(Path, "read_text", _fail):
        yield hit


@contextlib.contextmanager
def _inject_run_id_read_error(run_id_path: Path):
    """Genau EIN gewoehnlicher `OSError` beim Lesen einer TATSAECHLICH
    vorhandenen `run_id.json` -- unterscheidet sich von echter Absenz
    (Datei existiert, nur der eine Lesezugriff schlaegt fehl)."""
    original = Path.read_text
    hit = [0]

    def _fail(path, *a, **kw):
        if path == run_id_path and hit[0] == 0:
            hit[0] += 1
            raise OSError("INJECT ordinary one-shot run_id read failure")
        return original(path, *a, **kw)

    with patch.object(Path, "read_text", _fail):
        yield hit


@contextlib.contextmanager
def _inject_state_open_error(state_path: Path):
    """Genau EIN transienter `FileNotFoundError` beim OEFFNEN einer
    TATSAECHLICH vorhandenen Persona-State-Datei (die Datei bleibt auf der
    Platte, nur dieser eine `open()`-Aufruf schlaegt fehl) -- unterscheidet
    sich von echter Absenz (Datei existiert wirklich nicht)."""
    open_orig = builtins.open
    hit = [0]

    def _opened(path, *a, **kw):
        if not isinstance(path, int) and Path(path) == state_path and hit[0] == 0:
            hit[0] += 1
            raise FileNotFoundError("INJECT transient absent state authority")
        return open_orig(path, *a, **kw)

    with patch("builtins.open", _opened):
        yield hit


# ── gesunder Referenzpfad (keine Fehlerinjektion) ───────────────────────────

def test_healthy_resolve_active_save_and_export_use_real_published_current():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r, anew = _setup(base)
        ui = r.ui()
        resolved, unresolved = ui._resolve_active_save("sniper", None)
        assert not unresolved and resolved == anew, \
            "ohne Fehler muss _resolve_active_save den real veroeffentlichten Current liefern"
        shown: list = []
        r.ui(shown=shown)._cmd_export()
        export_path = base / "exports" / "sniper.json"
        assert export_path.exists() and json.loads(export_path.read_text(encoding="utf-8")) == anew, \
            "gesunder Export muss den real veroeffentlichten Current schreiben"


# ── Konfliktbasis (`_cmd_import`, 02_ABNAHME Fall 2/R1a) ────────────────────

def test_import_conflict_basis_blocks_on_known_current_version_read_error():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r, anew = _setup(base)
        version_path = _version_path(base)
        incoming = json.loads(json.dumps(anew))
        incoming["save_id"] = "synthetic-external-proposal-readpaths"
        shown: list = []
        with _inject_version_read_error(version_path) as hit:
            r.ui(inputs=[json.dumps(incoming), "ENDE", "k"], shown=shown)._cmd_import()
        assert hit[0] == 1, "Injektion muss tatsaechlich feuern"
        assert any("Import abgebrochen" in s for s in shown), f"kontrollierter Abbruch erwartet, shown={shown}"
        assert _cur(base) == anew, \
            "ein bekannter, gerade nicht lesbarer Current darf durch 'k' NICHT durch die alte " \
            "Onboarding-Fassung ersetzt werden (kein Fortschritts-Rollback)"


def test_import_conflict_basis_blocks_on_known_current_persona_state_transient_error():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r, anew = _setup(base)
        state_path = base / "states" / "sniper.json"
        incoming = json.loads(json.dumps(anew))
        incoming["save_id"] = "synthetic-external-proposal-readpaths-2"
        shown: list = []
        with _inject_state_open_error(state_path) as hit:
            r.ui(inputs=[json.dumps(incoming), "ENDE", "k"], shown=shown)._cmd_import()
        assert hit[0] == 1, "Injektion muss tatsaechlich feuern"
        assert any("Import abgebrochen" in s for s in shown), f"kontrollierter Abbruch erwartet, shown={shown}"
        assert _cur(base) == anew, \
            "ein transienter Persona-State-Fehler an einer bekannten Autoritaet darf nicht als " \
            "Erstzustand missgedeutet werden"


# ── lokale Runde, Leader UND Gast (02_ABNAHME Fall 3/R1b) ───────────────────

def test_local_round_leader_blocks_on_known_current_version_read_error():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r, anew = _setup(base)
        version_path = _version_path(base)
        gm = t4._GM(["Die synthetische Szene bleibt offen."])
        shown: list = []
        with _inject_version_read_error(version_path) as hit:
            r.ui(inputs=["Ich beginne meinen Abschnitt."], shown=shown, gm=gm)._cmd_local_round()
        assert hit[0] == 1, "Injektion muss tatsaechlich feuern"
        assert not gm.calls, "kein GM-Aufruf, solange der Leader-Current ungeklaert ist"
        assert any("nicht moeglich" in s or "nicht lesbar" in s for s in shown), f"shown={shown}"
        assert _cur(base) == anew


def test_local_round_guest_blocks_on_known_current_version_read_error():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r, anew = _setup(base)
        tech_save = t4._sv("tech")
        r.ui(p="tech", inputs=[json.dumps(tech_save), "ENDE"])._cmd_import()
        assert _cur(base, "tech") == tech_save, "Testaufbau: tech muss einen eigenen Current haben"
        guest_version_path = _version_path(base, "tech")
        gm = t4._GM(["Die synthetische Szene bleibt offen."])
        shown: list = []
        with _inject_version_read_error(guest_version_path) as hit:
            r.ui(shown=shown, gm=gm)._cmd_local_round(["tech"])
        assert hit[0] == 1, "Injektion muss tatsaechlich feuern"
        assert not gm.calls, "kein GM-Aufruf, solange der Gast-Current ungeklaert ist -- dieselbe " \
            "Regel wie fuer den Leader (A7/D1: EINE Autoritaet fuer alle Rollen)"
        assert any("nicht moeglich" in s or "nicht lesbar" in s for s in shown), f"shown={shown}"
        # Weder Leader- noch Gast-Fassung duerfen durch den geblockten Start veraendert werden.
        assert _cur(base) == anew
        assert _cur(base, "tech") == tech_save


# ── Export (02_ABNAHME Fall 4/R1c) ──────────────────────────────────────────

def test_export_blocks_on_known_current_version_read_error():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r, anew = _setup(base)
        version_path = _version_path(base)
        shown: list = []
        with _inject_version_read_error(version_path) as hit:
            r.ui(shown=shown)._cmd_export()
        assert hit[0] == 1, "Injektion muss tatsaechlich feuern"
        assert any("Export abgebrochen" in s for s in shown), f"shown={shown}"
        export_path = base / "exports" / "sniper.json"
        assert not export_path.exists(), \
            "kein Export einer moeglicherweise veralteten (alten Onboarding-)Fassung"
        assert _cur(base) == anew


# ── strenge Referenzkette am Aktivwechsel (02_ABNAHME Fall 5/R2) ────────────
# Ergaenzt test_i4aa_weg4_current_read_error_blocks_instead_of_silent_reset
# (Versions-Lesefehler) um die BEIDEN vorgelagerten Kettenglieder.

def test_switch_blocks_on_run_id_read_error_and_preserves_state():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r, anew = _setup(base)
        tech = t4._sv("tech")
        tech_id = saves.block_char_id(tech)
        r.ui(inputs=[json.dumps(tech), "ENDE", "b"])._cmd_import()  # tech inaktiv registrieren
        run_id_path = base / "run" / "run_id.json"
        before_run_id = json.loads(run_id_path.read_text(encoding="utf-8"))["run_id"]
        entries = catalog.list_for_participant(r.cat, "sniper")
        with _inject_run_id_read_error(run_id_path) as hit:
            r.ui()._switch_active_figure(tech_id, entries)
        assert hit[0] == 1, "Injektion muss tatsaechlich feuern"
        assert _cur(base) == anew, "kein Aktivwechsel ohne geklaerte run_id-Autoritaet"
        assert json.loads(run_id_path.read_text(encoding="utf-8"))["run_id"] == before_run_id, \
            "strenges Lesen darf run_id.json NIE neu initialisieren/ueberschreiben"
        assert catalog.active_chrononaut_id(r.cat, "sniper") == r.ids["sniper"]


def test_switch_blocks_on_persona_state_transient_error_and_preserves_state():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r, anew = _setup(base)
        tech = t4._sv("tech")
        tech_id = saves.block_char_id(tech)
        r.ui(inputs=[json.dumps(tech), "ENDE", "b"])._cmd_import()  # tech inaktiv registrieren
        state_path = base / "states" / "sniper.json"
        entries = catalog.list_for_participant(r.cat, "sniper")
        with _inject_state_open_error(state_path) as hit:
            r.ui()._switch_active_figure(tech_id, entries)
        assert hit[0] == 1, "Injektion muss tatsaechlich feuern"
        assert _cur(base) == anew, \
            "ein transienter Persona-State-Fehler an einer bekannten Autoritaet darf keinen " \
            "Aktivwechsel ohne Ausgangssicherung ausloesen"
        assert catalog.active_chrononaut_id(r.cat, "sniper") == r.ids["sniper"]


# ── echter Erstzustand (02_ABNAHME Fall 7) ──────────────────────────────────

def test_genuine_first_setup_stays_none_without_run_id_init_and_allows_first_import():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        run_dir = base / "run"
        states_dir = base / "states"
        result = store.load_current_save_or_raise(run_dir, "sniper", _ps(), states_dir=states_dir)
        assert result is None, "echter Erstzustand bleibt gueltig -- keine Ausnahme"
        assert not (run_dir / "run_id.json").exists(), \
            "das strenge Lesen selbst darf niemals eine run_id initialisieren"
        initial = t4._sv("sniper")
        shown: list = []
        ui = TuiSession(
            base / "onboarding", base / "catalog", "sniper",
            input_fn=t4._script([json.dumps(initial), "ENDE"]),
            print_fn=shown.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
        )
        ui._cmd_import()
        assert _cur(base) == initial, \
            "regulaerer allererster Import muss trotz der strengeren Lesekette weiterhin funktionieren"


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
