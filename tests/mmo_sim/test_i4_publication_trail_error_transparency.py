#!/usr/bin/env python3
"""
tests/mmo_sim/test_i4_publication_trail_error_transparency.py — I4-Nachzug
Fehlertransparenz-Fix (2026-09-25, Vertrag §3 A Rest, externe Abnahme
tests-review/review_i4_publication_trail.py + ADAPTED-Kopie fuer den
gewechselten Seam).

`store._has_publication_trail` unterschied bisher NICHT zwischen "zuverlaessig
leer" und "gerade nicht pruefbar": `Path.is_dir()` verschluckte ENOENT/
ENOTDIR/EBADF/ELOOP (-> `False`) und liess z.B. EIO roh durch; `Path.glob()`
verschluckte PermissionError/OSError beim darunterliegenden `os.scandir`-Scan
(-> leerer Iterator, `any(...)`=`False`). Ein blosser I/O-Fehler an der
Spurpruefung konnte dadurch wie ein sicherer Erstzustand aussehen (alter
Onboarding-Save wurde exportiert) ODER als roher `OSError` am vorgesehenen
`CurrentSaveUnavailableError`-Handler vorbeigehen (Vertrag §3 A, MAIN-
Quellenentscheidung 2026-09-25 §2c).

Der Fix ersetzt `is_dir()+glob()` durch zwei UNABHAENGIGE, fehlerbehandelte
`os.scandir()`-Aufrufe: zuerst der Elternordner `current_saves/` (listet
NUR den Eintragsnamen `<persona_key>__versions`, keine eigene teure Typ-
pruefung), danach -- NUR wenn der Eintrag dort nachweislich existiert -- die
eigentliche Inhaltsauflistung dieses Verzeichnisses. Nur an der
Elternauflistung gilt `FileNotFoundError`/`NotADirectoryError` als echte
Abwesenheit (kein Teilnehmer hat je etwas dort abgelegt bzw. DIESER
Teilnehmer hat dort keinen Eintrag -- Erstzustand bleibt moeglich, auch fuer
neue Teilnehmer in einer bereits bestehenden Community). Sobald der Eintrag
laut dieser unabhaengigen Quelle existiert, macht JEDER Fehler beim Lesen
seines Inhalts (EACCES, EIO, oder sogar ein erneutes ENOENT als TOCTOU-
Widerspruch) die Spur NICHT wieder zu einer leeren Menge -- `raise
CurrentSaveUnavailableError` statt `False`/rohem `OSError` (Vertrag §3 A:
"Fehler der Spurpruefung nicht wiederum als leere Menge behandeln").

Seam-Hinweis (Review §6 / Worker-Brief §4 "Seam-Verifikation Pflicht"): die
externe Probe `tests-review/review_i4_publication_trail.py` injiziert ihre
Faelle 'stat-missing'/'stat-io' an `Path.stat` -- diesen Seam ruft der
Fixcode nicht mehr auf (nur noch `os.scandir`, siehe oben), daher trifft die
UNVERAENDERTE externe Probe diesen Seam nicht mehr (`hits=0`, empirisch
bestaetigt gegen den reparierten Worktree, 2026-09-25). Diese Datei liefert
dafuer die geforderte gleichwertige DAUERHAFTE In-Repo-Deckung am tatsaechlich
benutzten Seam (Original bleibt unveraendert; eine reine Kopie mit
angepasstem Seam liegt zusaetzlich als
`adapted-tests/review_i4_publication_trail.ADAPTED.py` im Workerbereich).

Deckt (Worker-Brief §4, Mindestanforderung):
  - echter Scanfehler (EACCES/EIO, Kind- UND Elternebene) -> kontrollierte
    Sperre statt Alt-Export, KEIN roher OSError am Aufrufer;
  - ein erneutes ENOENT NACH unabhaengig bestaetigter Elternexistenz
    (TOCTOU) ist KEIN sicherer Erstzustand -> ebenfalls kontrollierte Sperre;
  - eigene Spur bei fehlendem State fuehrt nie zu Alt-Save-Export;
  - ein wirklich neuer Teilnehmer wird durch eine FREMDE Spur (Elternordner
    existiert bereits durch einen ANDEREN Teilnehmer) nicht gesperrt;
  - eine nachweislich leere/nur-fremdartige Versionsablage bleibt Erstzustand
    (kein falsches Sperren);
  - nach einem geblockten Versuch entstehen keine Nebenwrites, ein spaeterer
    fehlerfreier Versuch liefert exakt die unveraenderte aktuelle Fassung.

Direkte Aufrufe der bereits oeffentlichen strengen Lesehilfe
(`store.load_current_save_or_raise`) fuer die reinen Absenz-/Leerfaelle
(kein Netz-/Modellzugriff, keine Mocks noetig -- echte Verzeichniszustaende),
ECHTE neue Interpreterprozesse (`subprocess.run([sys.executable, __file__,
'--child', ...])`, analog zu `test_i4_reference_contract.py`/
`test_i4_active_authority_subprocess.py`) fuer die I/O-Fehlerinjektion bis
zum realen Verbraucher `TuiSession._cmd_export`. Rein synthetische Fixtures.

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
_pa.add_argument("--fault", choices=["child-permission", "child-toctou-enoent", "child-io", "parent-permission"])
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


def _versions_dir(base: Path, pk: str = "sniper") -> Path:
    return base / "run" / "current_saves" / f"{pk}__versions"


def _current_saves_dir(base: Path) -> Path:
    return base / "run" / "current_saves"


def _fingerprints(base: Path) -> dict:
    run = base / "run"
    if not run.exists():
        return {}
    return {
        str(f.relative_to(run)): hashlib.sha256(f.read_bytes()).hexdigest()
        for f in run.rglob("*") if f.is_file()
    }


def _ui(base: Path, inputs=(), shown=None, pk: str = "sniper") -> TuiSession:
    return TuiSession(
        base / "onboarding", base / "catalog", pk, input_fn=t4._script(inputs),
        print_fn=(shown.append if shown is not None else (lambda _x: None)),
        run_dir=base / "run", states_dir=base / "states", schema_path=_SCHEMA,
    )


# ── (i) nachweislich nie angelegt -- Elternordner fehlt komplett ───────────

def test_no_trail_when_current_saves_parent_never_created():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        # Kein Rig -- 'sniper' hat hier NIE publiziert, `current_saves/`
        # existiert noch nicht einmal.
        assert not _current_saves_dir(base).exists()
        save, err = _strict(base)
        assert save is None and err is None, \
            "ohne jeden current_saves-Elternordner bleibt die Spurpruefung der legitime Erstzustand"
        assert not (base / "run" / "run_id.json").exists(), \
            "die Spurpruefung selbst darf niemals eine run_id initialisieren"


# ── (i) nachweislich nie angelegt -- Eintrag fehlt trotz bestehendem Elternordner ──

def test_no_trail_for_new_participant_when_parent_exists_from_other_persona():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r, anew = _setup(base)
        assert _current_saves_dir(base).is_dir(), "Testaufbau: Elternordner muss durch 'sniper' bereits existieren"
        pk = "firstuser"
        assert not (_current_saves_dir(base) / f"{pk}__versions").exists(), \
            "Testaufbau: der neue Teilnehmer darf noch keinen eigenen Eintrag haben"

        save, err = _strict(base, pk)
        assert save is None and err is None, \
            "ein wirklich neuer Teilnehmer darf durch eine FREMDE, bereits bestehende Spur nicht gesperrt werden"
        assert _strict(base)[0] == anew, "der bestehende Teilnehmer 'sniper' bleibt von dieser Pruefung unberuehrt"


# ── (i) nachweislich leer/fremdartig -- Verzeichnis existiert, enthaelt aber keine gueltige Spur ──

def test_versions_dir_exists_but_empty_is_no_trail():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r, anew = _setup(base)
        pk = "secondhuman"
        empty_versions = _current_saves_dir(base) / f"{pk}__versions"
        empty_versions.mkdir(parents=True)
        save, err = _strict(base, pk)
        assert save is None and err is None, \
            "ein tatsaechlich existierendes, aber leeres Versionsverzeichnis ist weiterhin ein legitimer Erstzustand"


def test_versions_dir_with_only_non_digit_or_hidden_entries_is_no_trail():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r, anew = _setup(base)
        pk = "thirdhuman"
        versions = _current_saves_dir(base) / f"{pk}__versions"
        versions.mkdir(parents=True)
        (versions / "notes.txt").write_text("kein Save")
        (versions / ".0001.json").write_text("{}")  # versteckte Datei, Stem ".0001" ist KEINE Ziffernfolge
        save, err = _strict(base, pk)
        assert save is None and err is None, \
            "nur nicht-ziffern-stemmige/versteckte Eintraege duerfen weiterhin keine Spur belegen " \
            "(Paritaet zum bisherigen `stem.isdigit()`-Verhalten)"


# ── echte neue Interpreterprozesse: I/O-Fehler an einer NACHWEISLICH VORHANDENEN Spur ──

def _run_child(base: Path, fault: str) -> dict:
    cmd = [sys.executable, str(Path(__file__).resolve()), "--child", "export", "--base", str(base), "--fault", fault]
    env = {k: v for k, v in os.environ.items() if not any(t in k.upper() for t in ("TOKEN", "SECRET", "API_KEY", "PASSWORD"))}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    res = subprocess.run(cmd, cwd=base, env=env, text=True, capture_output=True, timeout=45)
    if res.returncode:
        raise RuntimeError(f"child failed rc={res.returncode}\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}")
    return json.loads(res.stdout)


def _child_export(base: Path, fault: str) -> None:
    target = _versions_dir(base)
    parent = _current_saves_dir(base)
    orig_scandir = os.scandir
    hits: list = []

    def _norm(path) -> str:
        try:
            return os.path.normpath(os.fsdecode(os.fspath(path)))
        except TypeError:
            return ""

    def _scan(path):
        p = _norm(path)
        if not hits:
            if fault == "child-permission" and p == str(target):
                hits.append({"seam": "child-scandir", "errno": errno.EACCES})
                raise PermissionError(errno.EACCES, "INJECT existing own trail scan denied", str(path))
            if fault == "child-toctou-enoent" and p == str(target):
                hits.append({"seam": "child-scandir", "errno": errno.ENOENT})
                raise FileNotFoundError(errno.ENOENT, "INJECT TOCTOU disappearance of existing own trail", str(path))
            if fault == "child-io" and p == str(target):
                hits.append({"seam": "child-scandir", "errno": errno.EIO})
                raise OSError(errno.EIO, "INJECT transient scan failure for existing own trail", str(path))
            if fault == "parent-permission" and p == str(parent):
                hits.append({"seam": "parent-scandir", "errno": errno.EACCES})
                raise PermissionError(errno.EACCES, "INJECT parent directory listing denied", str(path))
        return orig_scandir(path)

    shown: list = []
    error = None
    with patch("os.scandir", _scan):
        try:
            _ui(base, shown=shown)._cmd_export()
        except Exception as e:  # noqa: BLE001 -- Identitaet/Kontrolliertheit wird geprueft.
            error = {"type": type(e).__name__, "message": str(e), "controlled": isinstance(e, store.CurrentSaveUnavailableError)}
    exp = base / "exports" / "sniper.json"
    print(json.dumps({
        "hits": hits, "error": error, "shown": shown,
        "export": json.loads(exp.read_text()) if exp.exists() else None,
    }, ensure_ascii=False))


def _blocked_fault_case(fault: str, expect_seam: str) -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r, anew = _setup(base)
        state_path = base / "states" / "sniper.json"
        state_path.replace(base / "parked-state.json")  # State fehlt -- Spur ist der einzige verbleibende Beleg.
        before = _fingerprints(base)

        result = _run_child(base, fault)

        assert len(result["hits"]) == 1 and result["hits"][0]["seam"] == expect_seam, \
            f"[{fault}] Injektion muss den realen {expect_seam}-Seam genau einmal treffen: {result['hits']}"
        assert result["error"] is None, \
            f"[{fault}] kein roher Fehler darf am _cmd_export-Aufrufer entkommen: {result['error']}"
        assert result["export"] is None, \
            f"[{fault}] eine nicht pruefbare, aber nachweislich vorhandene Spur darf NIE zum Alt-Export fuehren"
        assert any("Export abgebrochen" in s for s in result["shown"]), \
            f"[{fault}] der kontrollierte Current-Fehlerpfad muss den Export sichtbar ablehnen: {result['shown']}"
        after = _fingerprints(base)
        assert after == before, \
            f"[{fault}] ein geblockter Versuch darf keine Nebenwrites an State/Ref/run_id/Versionsdateien hinterlassen"

        # Nach dem geblockten Versuch (ohne Fehlerinjektion) muss ein frischer
        # Prozess exakt die unveraenderte aktuelle Fassung wiederfinden --
        # keine Reparatur, kein Rueckfall auf eine andere Version.
        (base / "parked-state.json").replace(state_path)
        recovered = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--child", "export", "--base", str(base), "--fault", "child-permission"],
            cwd=base, timeout=45, capture_output=True, text=True,
        )
        # Zweiter echter Prozess: der State ist wieder vorhanden, die Ref
        # bleibt gueltig -- `_has_publication_trail` wird auf diesem
        # gesunden Weg gar nicht erst aufgerufen, die (beliebig gewaehlte)
        # Fault-Auswahl 'child-permission' bleibt daher wirkungslos (hits=[]).
        assert recovered.returncode == 0, recovered.stdout + recovered.stderr
        recovered_out = json.loads(recovered.stdout)
        assert recovered_out["hits"] == [] and recovered_out["error"] is None and recovered_out["export"] == anew, \
            "nach Wiederherstellung des Persona-States muss ein frischer Prozess exakt A_neu liefern, " \
            "die vorherige Blockade darf keine Restwirkung hinterlassen"


def test_subprocess_child_scandir_permission_error_on_existing_trail_blocks_export():
    _blocked_fault_case("child-permission", "child-scandir")


def test_subprocess_child_scandir_toctou_enoent_on_existing_trail_blocks_export():
    """Kernregression: ein ENOENT NACH unabhaengig durch die Elternauflistung
    bestaetigter Existenz ist KEIN sicherer Erstzustand -- anders als ein
    ENOENT AN der Elternauflistung selbst (dort bleibt es `False`, s.
    `test_no_trail_when_current_saves_parent_never_created`)."""
    _blocked_fault_case("child-toctou-enoent", "child-scandir")


def test_subprocess_child_scandir_io_error_on_existing_trail_blocks_export():
    """Regression gegen den alten Bug: `is_dir()` liess EIO roh durch (kein
    kontrollierter `CurrentSaveUnavailableError`, roher `OSError` entkam bis
    zum Aufrufer)."""
    _blocked_fault_case("child-io", "child-scandir")


def test_subprocess_parent_scandir_permission_error_blocks_export():
    """Neue, durch den Zwei-Ebenen-Fix hinzugekommene Schutzflaeche: auch ein
    Fehler an der ELTERNauflistung selbst (bevor ueberhaupt feststeht, ob der
    Eintrag existiert) darf trotz einer TATSAECHLICH vorhandenen eigenen Spur
    nicht als 'keine Spur' erscheinen."""
    _blocked_fault_case("parent-permission", "parent-scandir")


if _ARGS.child == "export":
    _child_export(_ARGS.base, _ARGS.fault)
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
