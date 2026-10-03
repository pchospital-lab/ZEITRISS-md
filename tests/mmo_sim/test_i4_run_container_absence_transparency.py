#!/usr/bin/env python3
"""
tests/mmo_sim/test_i4_run_container_absence_transparency.py — I4-Laufkontext-
abschluss (2026-09-25, Vertrag §3 A/B, MAIN-QUELLENENTSCHEIDUNG.md §3, externe
Abnahme tests-review/review_i4_run_context.py).

`store._has_publication_trail` behandelte bislang jedes `FileNotFoundError` an
`os.scandir(run_dir)` -- ob beim OEFFNEN oder waehrend einer bereits begonnenen
ITERATION, auch nach real gelesenen Eintraegen wie `run_id.json` -- pauschal als
`False` (Erstzustand, Alt-Export). Eine fruehere Docstring-Passage erklaerte das
zu einem "bewusst akzeptierten Restzustand" -- das war NIE Flos Freigabe
(MAIN-QUELLENENTSCHEIDUNG.md §0).

Der Fix ersetzt diesen Zweig durch eine EINMALIGE Disambiguierung gegen den
bereits bekannten, festen Datencontainer `run_dir.parent` (dieselbe Basis wie
`states_dir = run_dir.parent / "states"`; KEINE FS-Rekursion, Vertrag §3 B):
nur eine ERFOLGREICH ABGESCHLOSSENE Auflistung dieses Containers kann die
Abwesenheit von `run_dir` positiv belegen (`False`); listet der Container den
`run_dir`-Eintrag, oder schlaegt seine EIGENE Auflistung selbst fehl (Oeffnen
ODER Iteration, jeder `OSError`), ist das eine ungeklaerte bekannte Autoritaet
-- `raise CurrentSaveUnavailableError`, KEINE neue ENOENT-Ausnahme, KEIN
weiteres Hoehersteigen (02_ABNAHME).

Deckt (MAIN-QUELLENENTSCHEIDUNG.md §4, Testliste, dauerhaft in-repo statt nur
in der ephemeren Paketlieferung `tests-review/review_i4_run_context.py`):
  - open-ENOENT bei vorhandenem run -> Sperre statt Alt-Export;
  - partial-ENOENT NACH real gelesenem `run_id.json` -> Sperre statt Alt-Export;
  - vorhandener nicht aufloesbarer run-Symlink (kein Mock) -> Sperre;
  - NEUER Seam `os.scandir(run_dir.parent)`: Fehler am OEFFNEN UND an der
    ITERATION -> Sperre (terminale Grenze, keine neue ENOENT-Ausnahme);
  - echter Erstzustand (Datencontainer leer ODER mit realen Geschwister-
    eintraegen, `run_dir` fehlt wirklich) -> `False`/Erstimport bleibt moeglich;
  - exakte Wiederherstellung nach einem geblockten Versuch liefert wieder den
    unveraenderten aktuellen Stand, keine Nebenwrites.

Pure Python, nur `assert`, echte neue Interpreterprozesse fuer die
Fehlerinjektion (reale Verzeichniszustaende, kein Mock am Produkt), direkte
Aufrufe der oeffentlichen strengen Lesehilfe fuer die reinen Absenzfaelle."""
from __future__ import annotations

import errno
import hashlib
import json
import os
import subprocess
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
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"

import argparse  # noqa: E402

_pa = argparse.ArgumentParser(add_help=False)
_pa.add_argument("--child", choices=["store-call", "export"])
_pa.add_argument("--base", type=Path)
_pa.add_argument("--pk", default="sniper")
_pa.add_argument("--fault", choices=[
    "none", "run-dir-open-enoent", "run-dir-partial-enoent",
    "data-dir-open-eacces", "data-dir-open-eio", "data-dir-iter-enoent",
])
_ARGS, _REMAINING = _pa.parse_known_args()


def _ps() -> PersonaStateStore:
    return PersonaStateStore(_SCHEMA)


def _ui(base: Path, inputs=(), shown=None, pk: str = "sniper") -> TuiSession:
    return TuiSession(
        base / "onboarding", base / "catalog", pk, input_fn=t4._script(inputs),
        print_fn=(shown.append if shown is not None else (lambda _x: None)),
        run_dir=base / "run", states_dir=base / "states", schema_path=_SCHEMA,
    )


def _fingerprints(base: Path) -> dict:
    if not base.exists():
        return {}
    out = {}
    for f in base.rglob("*"):
        rel = f.relative_to(base)
        if "exports" in rel.parts:
            continue
        if f.is_symlink():
            out[str(rel)] = {"symlink": os.readlink(f)}
        elif f.is_file():
            out[str(rel)] = hashlib.sha256(f.read_bytes()).hexdigest()
    return out


def _norm(path) -> str:
    try:
        return os.path.normpath(os.fsdecode(os.fspath(path)))
    except TypeError:
        return ""


# ── direkte Aufrufe (kein Subprocess noetig, keine Fehlerinjektion): echter Erstzustand ──

def test_genuinely_missing_run_dir_in_empty_data_dir_is_initial_state():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        assert not (base / "run").exists() and list(base.iterdir()) == []
        save = store.load_current_save_or_raise(base / "run", "fresh", _ps(), states_dir=base / "states")
        assert save is None, "ein voellig leerer Datencontainer mit wirklich fehlendem run_dir bleibt Erstzustand"
        assert list(base.iterdir()) == [], "die reine Lesepruefung darf keinerlei Verzeichnis anlegen"


def test_genuinely_missing_run_dir_alongside_real_sibling_entries_is_still_initial_state():
    """Der Datencontainer ist NICHT leer (`states/sniper.json` existiert real
    durch den Rig-Konstruktor), `run_dir` selbst wurde aber noch NIE angelegt
    (der Rig-Konstruktor allein legt noch keinen `run/`-Ordner an -- das
    geschieht erst durch `write_test_profile`/`_progressed`). Ein anderer,
    wirklich unbekannter Teilnehmer ('newguy') muss trotz der realen
    Geschwistereintraege weiterhin einen echten Erstzustand sehen -- keine
    pauschale 'Container nicht leer -> Sperre'-Fehldeutung."""
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        t4.Rig(base, ("sniper",))
        assert (base / "states" / "sniper.json").is_file(), "Testaufbau: realer Geschwistereintrag muss existieren"
        assert not (base / "run").exists(), "Testaufbau: run_dir darf durch den reinen Konstruktor noch nicht angelegt sein"
        save = store.load_current_save_or_raise(base / "run", "newguy", _ps(), states_dir=base / "states")
        assert save is None, \
            "reale Geschwistereintraege im Datencontainer duerfen einen wirklich fehlenden run_dir nicht zur Sperre machen"


# ── echte neue Interpreterprozesse: Fehlerinjektion an beiden Ebenen ───────

def _run_child_store_call(base: Path, pk: str, fault: str) -> dict:
    cmd = [
        sys.executable, str(Path(__file__).resolve()), "--child", "store-call",
        "--base", str(base), "--pk", pk, "--fault", fault,
    ]
    env = {k: v for k, v in os.environ.items() if not any(t in k.upper() for t in ("TOKEN", "SECRET", "API_KEY", "PASSWORD"))}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    res = subprocess.run(cmd, cwd=base, env=env, text=True, capture_output=True, timeout=45)
    if res.returncode not in (0, 1):
        raise RuntimeError(f"child crashed rc={res.returncode}\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}")
    return json.loads(res.stdout)


def _child_store_call(base: Path, pk: str, fault: str) -> None:
    run_dir = base / "run"
    data_dir = base
    orig_scandir = os.scandir
    hits: list = []

    class _PartialDataDir:
        """Listet die REALEN Eintraege von `data_dir`, injiziert dann genau
        einmal einen Fehler NACH mindestens einem real gelesenen Eintrag --
        ein begonnener Scan darf auch am NEUEN Container-Seam keine Absenz
        beweisen (symmetrisch zur run_dir-Iterationsluecke, s. unten)."""

        def __init__(self, path):
            with orig_scandir(path) as it:
                self._entries = list(it)
            self._idx = 0

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def __iter__(self):
            return self

        def __next__(self):
            if self._idx >= 1 and not hits:
                hits.append({
                    "seam": "data-dir-scandir-iterator", "errno": errno.ENOENT,
                    "already_seen": [e.name for e in self._entries[: self._idx]],
                })
                raise FileNotFoundError(errno.ENOENT, "INJECT after a real data_dir entry", str(data_dir))
            if self._idx >= len(self._entries):
                raise StopIteration
            e = self._entries[self._idx]
            self._idx += 1
            return e

    class _PartialRunDir:
        """Analoge Iterationsluecke direkt am `run_dir`-Seam: real vorhandene
        Eintraege (u.a. `run_id.json`) werden zuerst geliefert, danach
        schlaegt die Iteration EINMALIG fehl -- ein bereits begonnener,
        nichtleerer Scan ist kein Beleg fuer 'nie angelegt' (Vertrag §3 A)."""

        def __init__(self, path):
            with orig_scandir(path) as it:
                entries = list(it)
            entries.sort(key=lambda e: (0 if e.name == "run_id.json" else 2 if e.name == "current_saves" else 1, e.name))
            self._entries = entries
            self._idx = 0

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def __iter__(self):
            return self

        def __next__(self):
            if self._idx < len(self._entries) and self._entries[self._idx].name == "current_saves" and not hits:
                hits.append({
                    "seam": "run-dir-scandir-iterator", "errno": errno.ENOENT,
                    "already_seen": [e.name for e in self._entries[: self._idx]],
                })
                raise FileNotFoundError(errno.ENOENT, "INJECT after a real run_id.json entry, before current_saves", str(run_dir))
            if self._idx >= len(self._entries):
                raise StopIteration
            e = self._entries[self._idx]
            self._idx += 1
            return e

    def _scan(path):
        p = _norm(path)
        if fault == "run-dir-open-enoent" and p == _norm(run_dir) and not hits:
            hits.append({"seam": "run-dir-scandir-open", "errno": errno.ENOENT})
            raise FileNotFoundError(errno.ENOENT, "INJECT one failed listing of an existing run container", str(run_dir))
        if fault == "run-dir-partial-enoent" and p == _norm(run_dir) and not hits:
            return _PartialRunDir(path)
        if fault == "data-dir-open-eacces" and p == _norm(data_dir) and not hits:
            hits.append({"seam": "data-dir-scandir-open", "errno": errno.EACCES})
            raise PermissionError(errno.EACCES, "INJECT data_dir listing denied", str(data_dir))
        if fault == "data-dir-open-eio" and p == _norm(data_dir) and not hits:
            hits.append({"seam": "data-dir-scandir-open", "errno": errno.EIO})
            raise OSError(errno.EIO, "INJECT data_dir listing I/O failure", str(data_dir))
        if fault == "data-dir-iter-enoent" and p == _norm(data_dir) and not hits:
            return _PartialDataDir(path)
        return orig_scandir(path)

    error = None
    save = None
    with patch("os.scandir", _scan):
        try:
            save = store.load_current_save_or_raise(run_dir, pk, _ps(), states_dir=base / "states")
        except Exception as e:  # noqa: BLE001 -- Kontrolliertheit selbst wird geprueft.
            error = {"type": type(e).__name__, "message": str(e), "controlled": isinstance(e, store.CurrentSaveUnavailableError)}
    print(json.dumps({"pid": os.getpid(), "hits": hits, "error": error, "save": save}, ensure_ascii=False))


def _park_state(base: Path, pk: str = "sniper") -> bytes:
    """Entfernt die Persona-State-Datei, damit die strenge Lesekette
    (`_persona_state_or_raise`) auf die Publikationsspur
    (`_has_publication_trail`) angewiesen ist, statt den gueltigen Ref direkt
    zu lesen -- identisches Muster zu
    `tests-review/review_i4_run_context.py:park`. Ohne diesen Schritt wird
    `_has_publication_trail` fuer einen bereits real publizierenden
    Teilnehmer NIE aufgerufen (der Ref-Lesepfad braucht gar keinen
    `os.scandir(run_dir)`-Zugriff). Liefert die Originalbytes fuer die
    exakte Wiederherstellung."""
    sp = base / "states" / f"{pk}.json"
    saved = sp.read_bytes()
    sp.unlink()
    return saved


def _unpark_state(base: Path, saved: bytes, pk: str = "sniper") -> None:
    (base / "states" / f"{pk}.json").write_bytes(saved)


def _blocked_case(setup_run: bool, fault: str, expect_seam: str, pk: str = "sniper") -> tuple[Path, dict, dict, dict, bytes | None]:
    """Gemeinsamer Ablauf: Rig aufbauen (ggf. bis `_progressed`, also mit
    real vorhandenem `run_dir` UND geparktem State, damit die Pruefung
    tatsaechlich `_has_publication_trail` erreicht), Fingerprint VOR dem
    geblockten Versuch nehmen, Kindprozess mit Injektion ausfuehren, harte
    Kernassertions pruefen, Fingerprint NACH dem Versuch vergleichen. Liefert
    `(base, expected_a_neu, result, tempdir, saved_state_bytes)` fuer
    optionale Wiederherstellung im Aufrufer."""
    td = tempfile.TemporaryDirectory()
    base = Path(td.name)
    r = t4.Rig(base, ("sniper",))
    anew = t4._progressed(r) if setup_run else None
    saved_state = _park_state(base, pk) if setup_run else None
    if not setup_run:
        assert not (base / "run").exists(), "Testaufbau: run_dir darf fuer diesen Fall nicht angelegt sein"
    before = _fingerprints(base)
    result = _run_child_store_call(base, pk, fault)

    assert len(result["hits"]) == 1 and result["hits"][0]["seam"] == expect_seam, \
        f"[{fault}] Injektion muss den realen {expect_seam}-Seam genau einmal treffen: {result['hits']}"
    assert result["error"] is not None and result["error"]["controlled"], \
        f"[{fault}] eine ungeklaerte Laufkontextfrage muss kontrolliert als CurrentSaveUnavailableError gemeldet werden: {result['error']}"
    assert result["error"]["type"] == "CurrentSaveUnavailableError", result["error"]
    assert result["save"] is None, f"[{fault}] bei einer ungeklaerten Frage darf keine (moeglicherweise veraltete) Fassung geliefert werden"

    after = _fingerprints(base)
    assert after == before, f"[{fault}] ein geblockter Versuch darf keine Nebenwrites an State/Ref/run_id/Versionsdateien hinterlassen"
    return base, anew, result, td, saved_state


# ── (a) open-ENOENT bei vorhandenem run -> Sperre statt Alt-Export ─────────

def test_run_dir_open_enoent_with_run_present_blocks_not_false():
    """Kernregression des Fixes (MAIN-QUELLENENTSCHEIDUNG.md §1): vorher
    wurde dieser Fall pauschal `False` (Alt-Export moeglich); jetzt sperrt
    die Disambiguierung gegen `run_dir.parent`, weil `run_dir` dort
    nachweislich vorhanden ist."""
    base, anew, result, td, saved_state = _blocked_case(setup_run=True, fault="run-dir-open-enoent", expect_seam="run-dir-scandir-open")
    try:
        _unpark_state(base, saved_state, "sniper")
        recovered = _run_child_store_call(base, "sniper", "none")
        assert recovered["hits"] == [] and recovered["error"] is None and recovered["save"] == anew, \
            "nach dem geblockten Versuch liefert ein frischer, fehlerfreier Prozess exakt die unveraenderte aktuelle Fassung (A_neu)"
    finally:
        td.cleanup()


# ── (b) partial-ENOENT NACH real gelesenem run_id.json -> Sperre statt Alt-Export ──

def test_run_dir_partial_enoent_after_real_run_id_entry_blocks_not_false():
    """Ein bereits begonnener, nichtleerer Scan (der u.a. das real
    existierende `run_id.json` schon gesehen hat) ist logisch kein Beleg,
    dass `run_dir` nie existiert habe -- auch dieser Fall darf nicht mehr
    `False` werden."""
    base, anew, result, td, saved_state = _blocked_case(setup_run=True, fault="run-dir-partial-enoent", expect_seam="run-dir-scandir-iterator")
    try:
        assert "run_id.json" in result["hits"][0]["already_seen"], \
            "die Injektion muss NACH einem real gelesenen run_id.json-Eintrag greifen, nicht davor"
        _unpark_state(base, saved_state, "sniper")
        recovered = _run_child_store_call(base, "sniper", "none")
        assert recovered["hits"] == [] and recovered["error"] is None and recovered["save"] == anew
    finally:
        td.cleanup()


# ── (c) vorhandener nicht aufloesbarer run-Symlink (kein Mock) -> Sperre ───

def test_dangling_run_symlink_blocks_without_mock():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r = t4.Rig(base, ("sniper",))
        anew = t4._progressed(r)
        saved_state = _park_state(base, "sniper")
        parked = base / "run-original-evidence"
        r.run.rename(parked)
        r.run.symlink_to(base / "never-created-target", target_is_directory=True)
        assert os.path.lexists(r.run) and r.run.is_symlink()
        before = _fingerprints(base)

        save, err = None, None
        try:
            save = store.load_current_save_or_raise(r.run, "sniper", _ps(), states_dir=r.states)
        except Exception as e:  # noqa: BLE001
            err = e
        assert save is None, "ein vorhandener, aber nicht aufloesbarer run-Link ist kein sicherer Erstzustand"
        assert isinstance(err, store.CurrentSaveUnavailableError), \
            f"ein dangling run-Symlink muss kontrolliert sperren, nicht still False werden: {err!r}"
        after = _fingerprints(base)
        assert after == before, "die reine Lesepruefung darf am dangling Link nichts veraendern"

        r.run.unlink()
        parked.rename(r.run)
        _unpark_state(base, saved_state, "sniper")
        assert store.load_current_save_or_raise(r.run, "sniper", _ps(), states_dir=r.states) == anew, \
            "nach exaktem Zuruecklegen des Originals liefert ein frischer Aufruf wieder A_neu"


# ── (d) NEUER Seam os.scandir(run_dir.parent): Oeffnen UND Iteration -> Sperre ──

def test_data_dir_scandir_open_permission_error_blocks():
    """NEUER Seam (Fix 2026-09-25): schlaegt schon das OEFFNEN der
    Disambiguierungs-Auflistung von `run_dir.parent` fehl, ist das die
    terminale Grenze dieser Pruefung -- kontrollierte Sperre, KEINE neue
    ENOENT-Ausnahme, kein weiteres Hoehersteigen (02_ABNAHME)."""
    base, _anew, _result, td, _saved = _blocked_case(setup_run=False, fault="data-dir-open-eacces", expect_seam="data-dir-scandir-open", pk="fresh")
    try:
        recovered = _run_child_store_call(base, "fresh", "none")
        assert recovered["hits"] == [] and recovered["error"] is None and recovered["save"] is None, \
            "nach dem geblockten Versuch bleibt der echte Erstzustand (data_dir leer, run fehlt) unveraendert erreichbar"
    finally:
        td.cleanup()


def test_data_dir_scandir_open_io_error_blocks():
    base, _anew, _result, td, _saved = _blocked_case(setup_run=False, fault="data-dir-open-eio", expect_seam="data-dir-scandir-open", pk="fresh")
    td.cleanup()


def test_data_dir_scandir_iteration_error_after_real_entry_blocks():
    """NEUER Seam, ITERATION: die Disambiguierungs-Auflistung von
    `run_dir.parent` hat bereits mindestens einen realen Geschwistereintrag
    (`states/`, durch den Rig-Konstruktor) gesehen, bevor sie scheitert --
    eine unterbrochene Auflistung ist auch am neuen Container-Seam kein
    Abwesenheitsbeleg (symmetrisch zu (b) am run_dir-Seam)."""
    base, _anew, result, td, _saved = _blocked_case(setup_run=False, fault="data-dir-iter-enoent", expect_seam="data-dir-scandir-iterator", pk="newguy")
    try:
        assert result["hits"][0]["already_seen"] == ["states"], \
            f"Testaufbau: einziger realer Geschwistereintrag muss 'states' sein, gesehen: {result['hits'][0]['already_seen']}"
        recovered = _run_child_store_call(base, "newguy", "none")
        assert recovered["hits"] == [] and recovered["error"] is None and recovered["save"] is None
    finally:
        td.cleanup()


# ── (e) Konsument: TUI _cmd_export blockiert sichtbar (kein Alt-Export) ────

def test_tui_cmd_export_shows_controlled_abort_on_run_dir_open_enoent_with_run_present():
    """Deckt den tatsaechlichen Verbraucher `TuiSession._cmd_export`
    (`mmo_sim/ui/tui.py:873`) dauerhaft in-repo ab -- derselbe Fehlerfall wie
    oben, diesmal ueber den echten Aufrufpfad statt der direkten Lesehilfe."""
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r = t4.Rig(base, ("sniper",))
        t4._progressed(r)
        _park_state(base, "sniper")
        orig_scandir = os.scandir
        hits: list = []

        def _scan(path):
            if _norm(path) == _norm(r.run) and not hits:
                hits.append(1)
                raise FileNotFoundError(errno.ENOENT, "INJECT", str(r.run))
            return orig_scandir(path)

        shown: list = []
        with patch("os.scandir", _scan):
            _ui(base, shown=shown, pk="sniper")._cmd_export()
        assert hits == [1]
        assert any("Export abgebrochen" in s for s in shown), shown
        assert not (base / "exports" / "sniper.json").exists(), \
            "ein ungeklaerter Current-Save darf niemals durch den (moeglicherweise veralteten) Onboarding-Stand ersetzt exportiert werden"


if _ARGS.child == "store-call":
    _child_store_call(_ARGS.base, _ARGS.pk, _ARGS.fault)
    raise SystemExit(0)


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
