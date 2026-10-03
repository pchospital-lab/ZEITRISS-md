#!/usr/bin/env python3
"""
tests/mmo_sim/test_i4_parent_scan_error_transparency.py — I4-Elternscan-
Nachzug (2026-09-25, Vertrag §3 A Rest, MAIN-QUELLENENTSCHEIDUNG §3; externe
Abnahme tests-review/review_i4_parent_scan.py).

`store._has_publication_trail` behandelte am ERSTEN Scan (`current_saves/`
selbst) `FileNotFoundError`/`NotADirectoryError` -- egal ob beim OEFFNEN von
`os.scandir` oder WAEHREND der Iteration (der `with ... as it: any(...)`
deckt beides ab) -- pauschal als `False`. Das deutete einen bestehenden,
falsch-typisierten (eine echte Datei statt eines Verzeichnisses) oder nur
teil-aufgelisteten Bereich faelschlich als Erstzustand und exportierte den
alten Onboarding-Save.

Der Fix stellt VOR den ersten `os.scandir`-Aufruf eine unabhaengige,
nicht-schluckende `os.stat(current_saves_dir)`-Existenz-/Typpruefung (kein
`is_dir()`/`os.path.isdir` -- die schlucken ENOENT/ENOTDIR ebenfalls):
  - `os.stat` wirft `FileNotFoundError` -> `False` (echter Erstzustand).
  - `os.stat` wirft einen anderen `OSError` -> `raise CurrentSaveUnavailableError`.
  - Ergebnis ist kein Verzeichnis (`not stat.S_ISDIR(...)`) -> `raise
    CurrentSaveUnavailableError` (struktureller Widerspruch, Fall 03).
Sobald die Verzeichnisexistenz damit UNABHAENGIG belegt ist, darf das
folgende `os.scandir(current_saves_dir)` keinen Fehler mehr als Abwesenheit
werten: JEDER `OSError` (inkl. erneutem ENOENT/ENOTDIR, beim Oeffnen ODER
waehrend der Iteration) -> `raise CurrentSaveUnavailableError` (Fall 02 +
Fall 04). Der unveraenderte Kindscan (`<persona_key>__versions`-Inhalt)
bleibt unberuehrt.

Seam-Hinweis (Worker-Brief §4 "Seam-Verifikation Pflicht"): die externe Probe
`tests-review/review_i4_parent_scan.py` injiziert ausschliesslich an
`os.scandir(run/current_saves)` -- fuer ihre Faelle 02/04/05 wird dieser Seam
durch den Fix weiterhin real erreicht (`hits==1`, empirisch bestaetigt gegen
den reparierten Worktree). Fall 03 (echte Datei statt Verzeichnis) wird durch
den neuen `os.stat`-Typcheck bereits VOR `os.scandir` gefangen (`hits==0`,
von der externen Probe selbst so erwartet -- sie assertet dort keine hits).
test_04 der externen Probe hat zusaetzlich eine ZWEITE, von diesem Fix
unabhaengige Fixtureigenschaft: `assert ... and out['seen']` verlangt, dass
VOR dem injizierten Fehler mindestens ein echter Verzeichniseintrag gelesen
wurde. Das Standard-Rig (`test_i4_figure_continuity.Rig`, ein Mitglied
'sniper') legt unter `current_saves/` nur zwei Eintraege an
('sniper__versions', 'sniper.json'); die Injektion der externen Probe feuert
namensbasiert auf 'sniper__versions'. Empirisch bestaetigt (2026-09-25, gegen
den UNVERAENDERTEN Start-Index-Tree, also VOR diesem Fix): `os.scandir`
liefert 'sniper__versions' auf diesem Dateisystem bereits als ERSTEN Eintrag
-> `seen` bleibt in JEDEM Fall leer, unabhaengig vom Fix (identische
Fehlermeldung "Injected iterator error must occur after actual parent
entries have been read" bereits an der unveraenderten Baseline reproduziert).
Das ist eine Eigenschaft der Fixture-/Dateisystem-Eintragsreihenfolge, keine
Regression dieses Fixes (Fall 02/04 selbst -- `hits==1`, `error is None`,
`export is None`, `originals_unchanged` -- ist nach dem Fix erfuellt).
`test_scandir_mid_iteration_error_after_confirmed_existence_blocks_with_
preceding_entry_preserved` unten liefert dafuer die geforderte gleichwertige
DAUERHAFTE In-Repo-Deckung mit einer indexbasierten (statt namensbasierten)
Injektion, die UNABHAENGIG von der Dateisystem-Eintragsreihenfolge belegt,
dass ein echter, vor dem Fehler gelesener Eintrag erhalten bleibt und der
Fehler trotzdem korrekt sperrt.

Direkte In-Prozess-Aufrufe von `store._has_publication_trail` fuer die reinen
Zustandsfaelle (kein Mock noetig -- echte Verzeichniszustaende); gemockte
`os.scandir`-Fehlerinjektion NUR fuer die TOCTOU-/Mid-Iteration-Faelle, die
ohne Mock nicht reproduzierbar sind. Rein synthetische Fixtures, kein
Netz-/Modellzugriff.

Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import errno
import os
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


def _current_saves_dir(base: Path) -> Path:
    return base / "run" / "current_saves"


def _setup(base: Path):
    """Ein Rig mit 'sniper' UND ein echter Abschnittsabschluss -- identisches
    Muster zu `test_i4_figure_continuity._progressed` -- etabliert eine
    echte, nicht leere Publikationsspur unter `current_saves/sniper__
    versions/`."""
    r = t4.Rig(base, ("sniper",))
    anew = t4._progressed(r)
    return r, anew


# ── (i) nachweislich nie angelegt -- stat-ENOENT ist der echte Erstzustand ──

def test_stat_enoent_on_current_saves_is_genuine_first_state():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        assert not _current_saves_dir(base).exists()
        result = store._has_publication_trail(base / "run", "brandnew")
        assert result is False, \
            "ein komplett fehlender current_saves-Elternordner (stat-ENOENT) bleibt der echte Erstzustand"


# ── (iii) struktureller Widerspruch -- current_saves existiert, ist aber KEIN Verzeichnis ──

def test_non_directory_at_current_saves_path_raises_instead_of_false():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        run_dir = base / "run"
        run_dir.mkdir(parents=True)
        (run_dir / "current_saves").write_text("SYNTHETIC_NON_DIRECTORY_AT_REQUIRED_PATH")
        try:
            store._has_publication_trail(run_dir, "sniper")
            raised = False
        except store.CurrentSaveUnavailableError:
            raised = True
        assert raised, \
            "eine echte Datei statt eines Verzeichnisses an current_saves/ ist kein leerer/neuer " \
            "Teilnehmer (Fall 03) -- Regression gegen das alte pauschale `return False`"


# ── Positivfall: unveraenderter Kindscan bleibt ueber den neuen Elternblock erreichbar ──

def test_existing_own_trail_is_still_detected_true_through_new_parent_block():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r, anew = _setup(base)
        result = store._has_publication_trail(r.run, "sniper")
        assert result is True, \
            "eine echte, nicht leere eigene Spur muss ueber den neuen stat-Elternblock hinweg " \
            "weiterhin `True` liefern (Kindscan-Fix bleibt unveraendert)"


# ── (i) neuer Teilnehmer bleibt trotz bestehender fremder Community-Struktur erlaubt ──

def test_new_participant_not_blocked_by_existing_foreign_parent_structure():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r, anew = _setup(base)
        assert _current_saves_dir(base).is_dir(), "Testaufbau: Elternordner existiert bereits durch 'sniper'"
        result = store._has_publication_trail(r.run, "firstuser")
        assert result is False, \
            "ein wirklich neuer Teilnehmer darf durch eine FREMDE, bereits bestehende Elternstruktur " \
            "nicht gesperrt werden (Fall e / test_01)"
        assert store._has_publication_trail(r.run, "sniper") is True, \
            "der bestehende Teilnehmer 'sniper' bleibt von dieser Pruefung unberuehrt"


# ── (iv) TOCTOU nach unabhaengig bestaetigter Existenz -- Fall 02 ──

def _toctou_case(exc_type: type[OSError], errno_value: int) -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r, anew = _setup(base)
        target = str(_current_saves_dir(base))
        orig_scandir = os.scandir
        hits: list = []

        def _scan(path):
            p = os.path.normpath(os.fsdecode(os.fspath(path)))
            if p == target and not hits:
                hits.append(p)
                raise exc_type(errno_value, "INJECT TOCTOU disappearance/retype after confirmed stat existence", p)
            return orig_scandir(path)

        with patch("os.scandir", _scan):
            try:
                store._has_publication_trail(r.run, "sniper")
                raised = False
            except store.CurrentSaveUnavailableError:
                raised = True
        assert len(hits) == 1, f"die Injektion muss den realen Elternscan genau einmal treffen: {hits}"
        assert raised, \
            f"{exc_type.__name__} am os.scandir-Aufruf NACH unabhaengig bestaetigter Verzeichnis-" \
            "existenz ist keine Abwesenheit mehr (Fall 02) -- Regression gegen das alte pauschale " \
            "`except (FileNotFoundError, NotADirectoryError): return False`"


def test_scandir_call_enoent_after_confirmed_existence_raises():
    _toctou_case(FileNotFoundError, errno.ENOENT)


def test_scandir_call_enotdir_after_confirmed_existence_raises():
    _toctou_case(NotADirectoryError, errno.ENOTDIR)


# ── (iv) Mid-Iteration-Fehler nach unabhaengig bestaetigter Existenz -- Fall 04 ──
# Der Produktcode prueft `any(entry.name == versions_name for entry in it)`:
# `any()` bricht die Iteration SOFORT ab, sobald der gesuchte Name gefunden
# ist. Auf diesem Dateisystem liefert das Rig 'sniper__versions' bereits als
# ERSTEN echten Eintrag (empirisch bestaetigt) -- ein an die REALEN Eintraege
# gekoppelter Mid-Iteration-Test haette daher NIE einen echten, VOR dem
# Fehler gelesenen (und verworfenen) Eintrag, unabhaengig vom Fix (siehe
# Moduldocstring). Diese Injektion liefert deshalb einen vollstaendig
# SYNTHETISCHEN, garantiert NICHT-passenden ersten Eintrag (eine andere
# Persona), erst danach den injizierten Fehler -- deterministisch unabhaengig
# von der Dateisystem-Reihenfolge, und funktional aequivalent zu Fall 04
# (Auflistung hat bereits Fortschritt gemacht, BEVOR sie fehlschlaegt).

def test_scandir_mid_iteration_error_after_confirmed_existence_blocks_with_preceding_entry_preserved():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r, anew = _setup(base)
        target = str(_current_saves_dir(base))
        hits: list = []
        seen: list = []

        class _FakeEntry:
            def __init__(self, name: str) -> None:
                self.name = name

        class _SyntheticMidIterator:
            """Liefert genau einen echten (nicht passenden) Eintrag, dann
            einen ENOENT -- unabhaengig von der realen Verzeichnisreihenfolge."""

            def __init__(self) -> None:
                self._items = [_FakeEntry("otherparticipant__versions")]
                self._idx = 0

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def __iter__(self):
                return self

            def __next__(self):
                if self._idx < len(self._items):
                    entry = self._items[self._idx]
                    self._idx += 1
                    seen.append(entry.name)
                    return entry
                hits.append({"preceding_entries": list(seen), "errno": errno.ENOENT})
                raise FileNotFoundError(errno.ENOENT, "INJECT error while enumerating existing parent", target)

        orig_scandir = os.scandir

        def _scan(path):
            p = os.path.normpath(os.fsdecode(os.fspath(path)))
            if p == target and not hits:
                return _SyntheticMidIterator()
            return orig_scandir(path)

        with patch("os.scandir", _scan):
            try:
                store._has_publication_trail(r.run, "sniper")
                raised = False
            except store.CurrentSaveUnavailableError:
                raised = True
        assert len(hits) == 1, f"die Injektion muss die reale Elternauflistung genau einmal treffen: {hits}"
        assert seen == ["otherparticipant__versions"], \
            "der injizierte Fehler muss NACH mindestens einem gelesenen Elterneintrag auftreten -- " \
            f"sonst pruefte dieser Test keine 'mid-iteration', beobachtet: {seen}"
        assert raised, \
            "eine unvollstaendige Elternauflistung (Fehler nach bereits gelesenen Eintraegen) ist keine " \
            "erfolgreich-leere Liste (Fall 04) -- Regression gegen das alte pauschale `return False`"


# ── keine Nebenwrites bei einem geblockten Versuch, exakte Wiederherstellung danach ──

def test_blocked_attempt_has_no_side_writes_and_recovers_exactly_afterwards():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r, anew = _setup(base)
        target = str(_current_saves_dir(base))
        orig_scandir = os.scandir
        hits: list = []

        def _scan(path):
            p = os.path.normpath(os.fsdecode(os.fspath(path)))
            if p == target and not hits:
                hits.append(p)
                raise FileNotFoundError(errno.ENOENT, "INJECT TOCTOU disappearance", p)
            return orig_scandir(path)

        run_files_before = sorted(str(f) for f in r.run.rglob("*"))
        with patch("os.scandir", _scan):
            try:
                store._has_publication_trail(r.run, "sniper")
            except store.CurrentSaveUnavailableError:
                pass
        run_files_after = sorted(str(f) for f in r.run.rglob("*"))
        assert run_files_before == run_files_after, \
            "die Spurpruefung selbst darf bei einem geblockten Versuch keine Datei anlegen/aendern/loeschen"

        # Ein zweiter, unbeeinflusster Aufruf danach liefert exakt dieselbe Spur.
        assert store._has_publication_trail(r.run, "sniper") is True, \
            "nach einem geblockten Versuch (ohne fortbestehende Injektion) muss die Spur unveraendert " \
            "wieder korrekt gelesen werden -- kein Restzustand aus dem geblockten Versuch"


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
