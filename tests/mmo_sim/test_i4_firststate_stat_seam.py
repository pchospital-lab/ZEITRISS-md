#!/usr/bin/env python3
"""
tests/mmo_sim/test_i4_firststate_stat_seam.py — I4-Erstzustandsnachweis-
Nachzug (2026-09-25, Vertrag §3 A/B Rest, Main-Quellenentscheidung
tmp/i4fs-2026-09-25/main/MAIN-QUELLENENTSCHEIDUNG.md §3, externe Abnahme
tests-review/review_i4_firststate_evidence.py).

`store._has_publication_trail` bewertete den ERSTEN Existenzbefund bislang
allein ueber `os.stat(current_saves_dir)`: ein `FileNotFoundError` an diesem
EINEN Probezugriff wurde pauschal zu `return False` ("Ordner nachweislich nie
angelegt"). Zwei reale Faelle widerlegten das:

  - ein einmaliger, isolierter `FileNotFoundError` an genau diesem stat,
    OBWOHL `current_saves/<persona_key>__versions/` tatsaechlich existiert
    (transienter/eingespielter Fehler an einem bekannten Pfad ist kein
    Abwesenheitsbeleg, nur ein gerade nicht aufgeloester Zugriff);
  - ein vorhandener DANGLING Symlink an `current_saves`: der Eintrag ist in
    der Elternauflistung sichtbar (`os.lexists`), `os.stat` folgt ihm aber
    und scheitert an dessen nicht existierendem Ziel mit demselben ENOENT.

Der Fix ersetzt das direkte `os.stat(current_saves_dir)` als Existenzbeleg
durch eine vorgelagerte, unabhaengige `os.scandir(run_dir)`-Auflistung (liest
nur Eintragsnamen, kein `entry.is_dir()` -- das waere ein zweiter, redundanter
`os.stat` auf denselben Pfad und wuerde die Fehlerinjektion der externen Probe
doppelt treffen). Nur wenn diese Auflistung `current_saves` NICHT als Eintrag
liefert (oder `run_dir` selbst nachweislich fehlt), bleibt `False` erlaubt.
Ist der Eintrag laut Elternauflistung vorhanden, bleibt `os.stat(current_saves_
dir)` UNVERAENDERT die Nahtstelle fuer die Typaufloesung (Verzeichnis vs.
Datei vs. nicht aufloesbarer Symlink) -- jeder Fehler dort fuehrt jetzt zu
`raise CurrentSaveUnavailableError` statt zu `False`.

Seam-Hinweis (Main-Quellenentscheidung §3, Seam-Pflicht): die externe Probe
`tests-review/review_i4_firststate_evidence.py` injiziert ihre Faelle
('stat-enoent'/'stat-eacces'/'stat-eio'/'stat-enotdir') an `os.stat`, gefiltert
auf den `current_saves`-Pfad -- exakt der hier weiterhin benutzte Seam. Diese
Datei liefert die geforderte gleichwertige DAUERHAFTE In-Repo-Deckung an
diesem Seam (Original der externen Probe bleibt unveraendert).

Deckt (additiv zu `test_i4_publication_trail_error_transparency.py`, die den
NACHGELAGERTEN `os.scandir`-Kindscan-Seam abdeckt, nicht diesen vorgelagerten
`os.stat`-Seam):
  - ein einmaliger `FileNotFoundError` an `os.stat(current_saves_dir)` bei
    TATSAECHLICH vorhandener eigener Publikationsspur -> kontrollierte Sperre,
    KEIN Alt-Export (Faelle: fehlender State, fehlende Ref);
  - EACCES/EIO/ENOTDIR an derselben Nahtstelle -> ebenfalls kontrollierte
    Sperre, keine Aenderung an Originaldaten;
  - ein ECHTER dangling Symlink an `current_saves` (kein Mock -- `os.stat`
    folgt ihm real und scheitert an dessen fehlendem Ziel) -> dieselbe
    kontrollierte Sperre, kein automatischer Symlink-Reparaturversuch;
  - nach exakter Wiederherstellung der Originaldaten liefert ein frischer
    Prozess wieder A_neu -- keine Versionswahl/Heuristik, keine Restwirkung;
  - positive Erstzustandsevidenz bleibt moeglich: `run_dir` existiert noch
    nicht einmal (voellig leerer Speicherbereich) UND `run_dir` existiert
    bereits, aber `current_saves` selbst noch nicht (z.B. vor der ersten
    Veroeffentlichung ueberhaupt) -> `False` aus einer POSITIVEN Feststellung,
    nie aus einem gefangenen Fehler am Zielzugriff selbst.

Direkte Aufrufe der oeffentlichen strengen Lesehilfe
(`store.load_current_save_or_raise`) fuer die reinen Absenzfaelle (keine
Mocks, echte Verzeichniszustaende). ECHTE neue Interpreterprozesse
(`subprocess.run([sys.executable, __file__, '--child', ...])`, analog zu
`test_i4_publication_trail_error_transparency.py`) fuer die I/O-Fehler-
injektion bis zum realen Verbraucher `TuiSession._cmd_export`. Rein
synthetische Fixtures, providerfrei.

Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import argparse
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

_pa = argparse.ArgumentParser(add_help=False)
_pa.add_argument("--child", choices=["export"])
_pa.add_argument("--base", type=Path)
_pa.add_argument(
    "--fault",
    choices=["none", "stat-enoent", "stat-eacces", "stat-eio", "stat-enotdir"],
)
_pa.add_argument("--park", choices=["missing-state", "missing-ref"])
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
    A_neu als veroeffentlichten Current mit eigener Publikationsspur --
    identisches Muster zu `test_i4_figure_continuity._progressed`."""
    r = t4.Rig(base, ("sniper",))
    anew = t4._progressed(r)
    return r, anew


def _current_saves_dir(base: Path) -> Path:
    return base / "run" / "current_saves"


def _fingerprints(base: Path) -> dict:
    run = base / "run"
    if not run.exists():
        return {}
    out = {}
    for f in run.rglob("*"):
        if f.is_symlink():
            out[str(f.relative_to(run))] = {"symlink": os.readlink(f)}
        elif f.is_file():
            out[str(f.relative_to(run))] = hashlib.sha256(f.read_bytes()).hexdigest()
    return out


def _ui(base: Path, inputs=(), shown=None, pk: str = "sniper") -> TuiSession:
    return TuiSession(
        base / "onboarding", base / "catalog", pk, input_fn=t4._script(inputs),
        print_fn=(shown.append if shown is not None else (lambda _x: None)),
        run_dir=base / "run", states_dir=base / "states", schema_path=_SCHEMA,
    )


def _park(base: Path, kind: str) -> bytes:
    """Entfernt genau EIN Metadatum am bestehenden Persona-State, ohne den
    Publikationsordner selbst anzufassen -- identisch zu Review-Fall 02.
    Sichert die Originalbytes zusaetzlich unter `state-original-evidence.json`
    fuer die spaetere exakte Wiederherstellung."""
    sp = base / "states" / "sniper.json"
    saved = sp.read_bytes()
    (base / "state-original-evidence.json").write_bytes(saved)
    if kind == "missing-state":
        sp.unlink()
    else:
        data = json.loads(saved)
        data.pop("current_save_version", None)
        sp.write_text(json.dumps(data))
    return saved


# ── Positive Erstzustandsevidenz: os.stat(current_saves) wird gar nicht erst gebraucht ──

def test_no_trail_when_run_dir_itself_never_created():
    """Voellig leerer Speicherbereich (§E, aeusserste Grenze): `run_dir`
    existiert nicht einmal -- die vorgelagerte `os.scandir(run_dir)` wirft
    `FileNotFoundError`, `os.stat(current_saves_dir)` wird dabei NIE
    aufgerufen (positive Absenz aus dem Elterncontainer, nicht aus einem
    gefangenen Fehler am Zielzugriff)."""
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        assert not (base / "run").exists()
        save, err = _strict(base)
        assert save is None and err is None, \
            "ohne jeden run_dir-Container bleibt die Spurpruefung der legitime Erstzustand"
        assert not (base / "run" / "run_id.json").exists(), \
            "die Spurpruefung selbst darf niemals eine run_id initialisieren"


def test_no_trail_when_run_dir_exists_but_current_saves_absent():
    """`run_dir` existiert bereits (z.B. durch eine andere, current_saves-
    unabhaengige Datei), `current_saves` selbst wurde aber noch nie angelegt
    -- die Elternauflistung liefert das positiv (`current_saves` fehlt unter
    den Eintragsnamen), `os.stat(current_saves_dir)` wird nicht erreicht."""
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        run = base / "run"
        run.mkdir()
        (run / "unrelated.marker").write_text("kein current_saves hier")
        assert not _current_saves_dir(base).exists()
        save, err = _strict(base)
        assert save is None and err is None, \
            "ein vorhandener run_dir ohne current_saves-Eintrag ist weiterhin ein legitimer Erstzustand"


# ── echte neue Interpreterprozesse: os.stat(current_saves)-Injektion bei NACHWEISLICH vorhandener Spur ──

def _run_child(base: Path, fault: str, park: str | None = None) -> dict:
    cmd = [sys.executable, str(Path(__file__).resolve()), "--child", "export", "--base", str(base), "--fault", fault]
    if park:
        cmd += ["--park", park]
    env = {k: v for k, v in os.environ.items() if not any(t in k.upper() for t in ("TOKEN", "SECRET", "API_KEY", "PASSWORD"))}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    res = subprocess.run(cmd, cwd=base, env=env, text=True, capture_output=True, timeout=45)
    if res.returncode:
        raise RuntimeError(f"child failed rc={res.returncode}\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}")
    return json.loads(res.stdout)


def _child_export(base: Path, fault: str, park: str | None) -> None:
    if park:
        sp = base / "states" / "sniper.json"
        saved = sp.read_bytes()
        (base / "state-original-evidence.json").write_bytes(saved)
        if park == "missing-state":
            sp.unlink()
        else:
            data = json.loads(saved)
            data.pop("current_save_version", None)
            sp.write_text(json.dumps(data))

    target = _current_saves_dir(base)
    original_stat = os.stat
    hits: list = []

    def _norm(path) -> str:
        try:
            return os.path.normpath(os.fsdecode(os.fspath(path)))
        except TypeError:
            return ""

    def _stat(path, *args, **kwargs):
        if fault != "none" and not hits and _norm(path) == str(target):
            err = {
                "stat-enoent": errno.ENOENT, "stat-eacces": errno.EACCES,
                "stat-eio": errno.EIO, "stat-enotdir": errno.ENOTDIR,
            }[fault]
            hits.append({"seam": "os.stat", "errno": err})
            raise OSError(err, "INJECT one failed metadata lookup of existing current_saves parent", str(path))
        return original_stat(path, *args, **kwargs)

    shown: list = []
    error = None
    with patch("os.stat", _stat):
        try:
            _ui(base, shown=shown)._cmd_export()
        except Exception as e:  # noqa: BLE001 -- Identitaet/Kontrolliertheit wird geprueft.
            error = {"type": type(e).__name__, "message": str(e), "controlled": isinstance(e, store.CurrentSaveUnavailableError)}
    exp = base / "exports" / "sniper.json"
    print(json.dumps({
        "hits": hits, "error": error, "shown": shown,
        "export": json.loads(exp.read_text()) if exp.exists() else None,
    }, ensure_ascii=False))


def _blocked_stat_fault_case(fault: str, park: str) -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r, anew = _setup(base)
        before = _fingerprints(base)

        result = _run_child(base, fault, park=park)

        assert len(result["hits"]) == 1 and result["hits"][0]["seam"] == "os.stat", \
            f"[{fault}/{park}] Injektion muss den realen os.stat-Seam an current_saves genau einmal treffen: {result['hits']}"
        assert result["error"] is None, \
            f"[{fault}/{park}] kein roher Fehler darf am _cmd_export-Aufrufer entkommen: {result['error']}"
        assert result["export"] is None, \
            f"[{fault}/{park}] ein einmaliger fehlgeschlagener stat auf eine nachweislich vorhandene Spur darf NIE zum Alt-Export fuehren"
        assert any("Export abgebrochen" in s for s in result["shown"]), \
            f"[{fault}/{park}] der kontrollierte Current-Fehlerpfad muss den Export sichtbar ablehnen: {result['shown']}"

        after = _fingerprints(base)
        assert after == before, \
            f"[{fault}/{park}] ein geblockter Versuch darf keine Nebenwrites an State/Ref/run_id/Versionsdateien hinterlassen"

        # Exakte Wiederherstellung der Originaldaten (State zurueckspielen) --
        # ein frischer Prozess ohne Fehlerinjektion muss wieder A_neu liefern.
        (base / "state-original-evidence.json").replace(base / "states" / "sniper.json")
        recovered = _run_child(base, "none")
        assert recovered["hits"] == [] and recovered["error"] is None and recovered["export"] == anew, \
            f"[{fault}/{park}] nach exakter Wiederherstellung der Originaldaten muss ein frischer Prozess " \
            "wieder A_neu liefern, keine Restwirkung der vorherigen Blockade"


def test_subprocess_stat_enoent_on_existing_parent_with_missing_state_blocks_export():
    """Kernregression (Review-Fall 02, Unterfall 1): ein einmaliger
    `FileNotFoundError` an `os.stat(current_saves_dir)` beweist bei
    tatsaechlich vorhandener eigener Spur KEINEN Erstzustand mehr."""
    _blocked_stat_fault_case("stat-enoent", "missing-state")


def test_subprocess_stat_enoent_on_existing_parent_with_missing_ref_blocks_export():
    """Kernregression (Review-Fall 02, Unterfall 2): dieselbe Injektion bei
    fehlender/unvollstaendiger Ref statt fehlendem State."""
    _blocked_stat_fault_case("stat-enoent", "missing-ref")


def test_subprocess_stat_eacces_on_existing_parent_blocks_export():
    """Bereits vor diesem Nachzug kontrolliert -- bleibt gruen (Review-Fall
    03), jetzt am unveraenderten os.stat-Seam nach der Elternauflistung."""
    _blocked_stat_fault_case("stat-eacces", "missing-state")


def test_subprocess_stat_eio_on_existing_parent_blocks_export():
    _blocked_stat_fault_case("stat-eio", "missing-state")


def test_subprocess_stat_enotdir_on_existing_parent_blocks_export():
    _blocked_stat_fault_case("stat-enotdir", "missing-state")


# ── echter dangling Symlink: KEIN Mock, os.stat scheitert real an dessen fehlendem Ziel ──

def test_real_dangling_symlink_at_current_saves_blocks_without_mock():
    """Review-Fall 04: `current_saves` selbst ist ein Symlink auf ein nicht
    existierendes Ziel. Der Eintrag ist in der Elternauflistung SICHTBAR
    (`os.lexists`/als Name in `os.scandir(run_dir)`), `os.stat` folgt ihm
    aber real und scheitert an dessen Ziel -- keine Fehlerinjektion noetig.
    Die Originaldaten bleiben in einem geparkten Verzeichnis erhalten, damit
    die Wiederherstellung ohne Raten moeglich ist."""
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r, anew = _setup(base)
        _park(base, "missing-state")
        parent = _current_saves_dir(base)
        parked = base / "current-saves-original-evidence"
        parent.rename(parked)
        parent.symlink_to(base / "absent-target", target_is_directory=True)

        before = _fingerprints(base)
        result = _run_child(base, "none")
        after = _fingerprints(base)

        assert os.path.lexists(parent) and parent.is_symlink(), \
            "Testaufbau: der dangling Symlink muss am current_saves-Pfad sichtbar bleiben"
        assert after == before, "ein geblockter Versuch darf die dangling-Struktur nicht veraendern"
        assert result["error"] is None and result["export"] is None, \
            "ein vorhandener, aber nicht aufloesbarer Pfadeintrag darf NIE einen alten Export freigeben " \
            "(keine automatische Symlink-Reparatur gefordert)"
        assert any("Export abgebrochen" in s for s in result["shown"])

        # Wiederherstellung: Symlink entfernen, Original zurueckstellen, State
        # zurueckspielen -- derselbe Speicherbereich muss wieder A_neu liefern.
        parent.unlink()
        parked.rename(parent)
        (base / "state-original-evidence.json").replace(base / "states" / "sniper.json")
        recovered = _run_child(base, "none")
        assert recovered["error"] is None and recovered["export"] == anew, \
            "nach exaktem Rueckstellen von Symlink-Ziel und State muss ein frischer Prozess wieder A_neu liefern"


if _ARGS.child == "export":
    _child_export(_ARGS.base, _ARGS.fault or "none", _ARGS.park)
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
