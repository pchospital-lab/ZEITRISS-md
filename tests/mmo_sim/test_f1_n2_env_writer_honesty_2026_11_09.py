#!/usr/bin/env python3
"""tests/mmo_sim/test_f1_n2_env_writer_honesty_2026_11_09.py — Delta-Test
für ZR-MINT-SPIELSTART-FEINSCHLIFF F1-N2 WP-N2-1e (P1d).

Vorher behandelte `scripts/setup.py:_update_env_file_preserving` einen
Lesefehler einer EXISTIERENDEN Datei wie eine leere Datei ("baue neu") --
fremde Felder/Kommentare gingen dabei unwiderruflich verloren. Ein
chmod(0o600)-Fehlschlag wurde stumm als Erfolg (`return True`) behandelt,
obwohl die Datei dann NICHT mit den erwarteten Rechten geschützt ist.

Deckt:
  (A) Existierende, aber nicht lesbare Datei -> Funktion gibt `False`
      zurück UND lässt die Datei bytegleich unangetastet (kein "baue
      neu"-Überschreiben).
  (B) chmod(0o600) wirft `OSError` auf der (noch nicht veroeffentlichten)
      Temp-Datei -> Funktion gibt `False` zurück UND veroeffentlicht den
      neuen Wert NICHT (atomare Transaktion vor dem Rename abgebrochen --
      N2-Fix, ersetzt die fruehere schwaechere "Inhalt steht trotzdem schon
      da"-Erwartung).
  (C) Gegenprobe: normaler Erfolgsfall (lesbar, Schreiben+chmod klappen)
      bleibt `True`, unbekannte Felder/Kommentare bleiben erhalten.

Double-Grenze (A4, offen gelegt): `Path.read_text`/`Path.chmod` werden
gezielt mit `unittest.mock.patch.object` auf echten temporären Dateien
gedoubelt, um die Fehlerpfade ohne Dateisystem-Berechtigungstricks
(portabel, auch als root) zu erzwingen. Keine Netzwerk-/Docker-Calls."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import traceback
import unittest.mock as mock
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_SETUP_PY = _REPO_ROOT / "scripts" / "setup.py"
_SUPPORT_SCRIPT = _HERE / "_local_tokenhost_support_2026_11_14.py"

# G3 (O6-C.C1): Diese Datei gehoerte zu den 8 ohne eigenen Fruehschutz und
# scheiterte unter der G3-Starter-Huelle, weil ihre G1-Leserkinder (unten,
# `_fresh_process_provider`) einen unregistrierten `subprocess.run` starteten
# -- den der Primaerguard korrekt als nicht autorisiert ablehnt. Fix: den
# bestehenden Support importieren (im geteilten unittest-Elternprozess
# seiteneffektfrei -- KEIN Guard, KEIN Produktimport) und nur im REALEN
# Koerper (`__main__`/run_all/G3-Starter/Bundle) den Guard VOR dem
# Produktimport uebernehmen/installieren. Keine Abschwaechung bestehender
# Assertions, kein neuer Guardbau -- der vorhandene Guard wird unveraendert
# wiederverwendet.
_support_spec = importlib.util.spec_from_file_location(
    "f1n2honesty_local_tokenhost_support", _SUPPORT_SCRIPT,
)
_support_mod = importlib.util.module_from_spec(_support_spec)
sys.modules["f1n2honesty_local_tokenhost_support"] = _support_mod
_support_spec.loader.exec_module(_support_mod)

_REAL_BODY = (__name__ == "__main__") or _support_mod.is_real_body_env()

if _REAL_BODY:
    # Fall 1: uebernimmt einen bereits vom G3-Starter via `bootstrap_isolation
    # (context=...)` installierten Primaerguard UNVERAENDERT; Fall 3:
    # installiert standalone (run_all/direkt) einen vollstaendigen privaten
    # Guard. In beiden Faellen VOR dem folgenden setup.py-Produktimport.
    _GUARD = _support_mod.self_bootstrap_isolation()

    # R2 (01_GENERALREVIEW.md §3 "fuer den G1-Familienlauf fehlen die
    # vollstaendigen eigenen Kontexte/einzelnen Reader-Rohkanaele/gebundenen
    # Parentlaufdaten"): EIN bleibendes Evidenzziel innerhalb des bereits
    # vom Guard erlaubten privaten Schreibbereichs DIESES Prozesses
    # (`_GUARD.private_write_roots[0]`) -- identisches Muster zu
    # `_G2_EVIDENCE_DIR` im Profiltest. Unter dem G3-Starter ist dieser
    # Bereich bereits `fresh_tmp` (vom Starter nach dem Lauf vollstaendig
    # nach `private_root_copy` kopiert); im Solo-/run_all-Lauf kopieren
    # Main/Integrator ihn NACH dem Lauf an `.../run/evidence/g1/`. Kein
    # neues Repo-File, keine neue Guard-Architektur -- reine Pfadwahl
    # innerhalb der bestehenden Wurzel.
    _G1_EVIDENCE_DIR = Path(_GUARD.private_write_roots[0]) / "g1-raw-evidence"
    _G1_EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    _spec = importlib.util.spec_from_file_location(
        "f1_n2_env_writer_honesty_setup_under_test", _SETUP_PY,
    )
    setup_mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(setup_mod)
else:
    _G1_EVIDENCE_DIR = None


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def test_unreadable_existing_file_is_not_rebuilt_returns_false():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / ".env"
        original = "# Kommentar\nFOO=bar\nOPENWEBUI_API_KEY=old-value\n"
        path.write_text(original, encoding="utf-8")

        with mock.patch.object(Path, "read_text", side_effect=OSError("Permission denied")):
            ok = setup_mod._update_env_file_preserving(path, {"OPENWEBUI_API_KEY": "new-value"})

        assert ok is False, "Lesefehler einer existierenden Datei darf NICHT als Erfolg gelten"
        # bytegleich erhalten -- kein "baue neu"-Überschreiben.
        assert path.read_text(encoding="utf-8") == original, (
            "Datei wurde trotz Lesefehler veraendert -- fremde Felder waeren verloren gegangen"
        )


def test_chmod_failure_returns_false_even_though_write_succeeded():
    """ZR-LOCAL-TOKENHOST-N2-UEBERARBEITET (02_NACHARBEIT.md Gruppe A.2,
    03_SCOPE_ROLLEN_BUDGET.md §Bewahrte Dateien): die fruehere Assertion
    "bei chmod-Fehler liegt das neue Secret trotzdem schon in der Datei"
    ist durch die STAERKERE atomare Forderung ersetzt -- `_update_env_file_
    preserving` schreibt jetzt zuerst in eine Temp-Datei, setzt chmod DORT
    und veroeffentlicht erst per atomarem Rename; ein chmod-Fehlschlag auf
    der noch nicht veroeffentlichten Temp-Datei darf den neuen
    (ungeschuetzten) Wert NICHT mehr live auf Platte hinterlassen."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / ".env"

        with mock.patch.object(setup_mod.os, "open", side_effect=OSError("chmod not permitted")):
            ok = setup_mod._update_env_file_preserving(path, {"OPENWEBUI_API_KEY": "new-value"})

        assert ok is False, "chmod-Fehlschlag darf NICHT stumm als Erfolg (True) gelten"
        # Staerkere Forderung: alte Datei unveraendert ODER neues Profil
        # bleibt auch frisch inaktiv (hier: Zieldatei existierte vorher
        # nicht -- sie darf durch den gescheiterten Versuch nicht neu mit
        # dem ungeschuetzten Wert entstehen).
        assert not path.exists() or "OPENWEBUI_API_KEY=new-value" not in path.read_text(encoding="utf-8"), (
            "chmod-Fehlschlag darf den neuen Secretwert NICHT bereits live/aktiv auf Platte "
            "hinterlassen -- alte Datei muss unveraendert bleiben oder das neue Profil muss "
            "frisch inaktiv bleiben (staerkere atomare Forderung, ersetzt die fruehere Assertion)."
        )
        leftover = list(Path(tmp).glob(".env.tmp-*"))
        assert not leftover, f"verwaiste Temp-Datei nach chmod-Fehlschlag nicht aufgeraeumt: {leftover}"


def test_chmod_failure_on_existing_file_leaves_old_bytes_unchanged():
    """Ergaenzung zur staerkeren Forderung (existierte bereits eine aktive
    Datei mit altem Inhalt): nach einem chmod-Fehlschlag muss sie BYTEGLEICH
    beim alten Stand bleiben, nicht nur 'neuer Wert fehlt'."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / ".env"
        original = "# Kommentar\nFOO=bar\nOPENWEBUI_API_KEY=old-value\n"
        path.write_text(original, encoding="utf-8")

        with mock.patch.object(setup_mod.os, "open", side_effect=OSError("chmod not permitted")):
            ok = setup_mod._update_env_file_preserving(path, {"OPENWEBUI_API_KEY": "new-value"})

        assert ok is False, "chmod-Fehlschlag darf NICHT stumm als Erfolg (True) gelten"
        assert path.read_text(encoding="utf-8") == original, (
            "alte Datei muss nach chmod-Fehlschlag bytegleich unveraendert bleiben"
        )


def test_normal_success_path_preserves_unknown_fields_and_returns_true():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / ".env"
        path.write_text("# Kommentar\nFREMDES_FELD=bleibt\nOPENWEBUI_API_KEY=old\n", encoding="utf-8")

        ok = setup_mod._update_env_file_preserving(path, {"OPENWEBUI_API_KEY": "new-value"})

        assert ok is True
        content = path.read_text(encoding="utf-8")
        assert "FREMDES_FELD=bleibt" in content, "unbekannte Felder muessen erhalten bleiben"
        assert "OPENWEBUI_API_KEY=new-value" in content
        assert "# Kommentar" in content


# ─────────────────────────────────────────────────────────────────────────
# G1 (O1-C.C2): die DREI realen IO-Seams der geschuetzten Profiltransaktion
# EINZELN treffen -- NACH erfolgreichen Vorgaengern, nicht als frueher
# Marker-/Zugriffsfehler-Ersatz.
#
# Befund (open-groups-G1-G4): die obigen Tests (und die F1-Geschwister)
# patchen `setup_mod.os.open` GLOBAL. `_update_env_file_preserving` legt aber
# ZUERST den Pending-Marker per `pending_marker.touch()` an (setup.py ~Z.1987,
# nutzt intern denselben `os.open`), sodass ein globaler Patch dort scheitert
# und den geschuetzten Tempfile-`os.open` (~Z.2009), `fh.write` (~Z.2019) und
# `os.replace` (~Z.2025) NIE erreicht. Die folgenden Tests injizieren
# pfad-/aufruf-selektiv genau an einem der drei echten Seams -- die jeweiligen
# Vorgaenger laufen tatsaechlich erfolgreich -- und belegen Rueckgabe,
# tatsaechlich erreichte Operation, Dateiendzustand, Pending-Marker UND die
# oeffentliche Lesesicht eines FRISCHEN Prozesses. Es wird kein Produktcode
# geaendert und keine kuenstliche `chmod`-Operation hinzugefuegt; die
# Rechteanforderung wird durch die `os.open(..., O_CREAT|O_EXCL, 0o600)`-
# Erzeugung selbst erfuellt (s. test_...permission_requirement...).
_PROVIDER_KEY = "ZEITRISS_MODEL_PROVIDER"


def _active_local_profile_bytes() -> str:
    """Ein vollstaendiges, GUELTIGES aktives lokales Profil (erkennbar unechte
    Werte) -- dient als 'alte aktive Bytes' fuer den Vergleich nach einem
    Fehlerpfad. G3-Generalbefund (01_GENERALREVIEW.md §2): vorher fehlten
    `ZEITRISS_LOCAL_BASE_URL`/`_MODEL`/`_API_KEY` -- `scripts/local_model_
    profile.py::resolve_local_profile` haelt schon VOR jeder Fehlerinjektion
    (fehlende Base-URL -> ProfileHold), die als 'aktiv' bezeichnete Fixture
    war also selbst nie wirklich aktiv. Jetzt alle drei von `resolve_local_
    profile` verlangten Felder ergaenzt (synthetische, erkennbar unechte
    Werte, kein echtes Secret/Host)."""
    return (
        "# aktives lokales Profil (Testfixture, keine echten Secrets)\n"
        f"{_PROVIDER_KEY}=local\n"
        "FREMDES_FELD=bleibt-erhalten\n"
        "ZEITRISS_LOCAL_BASE_URL=http://127.0.0.1:11434\n"
        "ZEITRISS_LOCAL_MODEL=local-test-model-not-secret\n"
        "ZEITRISS_LOCAL_API_KEY=local-test-key-not-secret\n"
        "OPENWEBUI_API_KEY=fake-old-token-not-secret\n"
    )


def _marker_path(path: Path) -> Path:
    return path.with_name(f"{path.name}.local-pending")


_FRESH_READER_COUNTER = {"n": 0}


def _fresh_process_provider(path: Path) -> str:
    """Startet einen EIGENEN frischen Python-Prozess (kein In-Memory-Zustand
    dieses Testprozesses), der `scripts/setup.py` neu laedt und die
    oeffentliche `resolve_model_provider(path)` auswertet; gibt den Provider
    ('hold'|'local'|'cloud'|'legacy') zurueck.

    Belegt, dass der nach einem Fehlerpfad auf der Platte verbliebene Zustand
    (Pending-Marker bzw. unveraenderte alte Bytes) von AUSSEN als HOLD/inaktiv
    gesehen wird -- ein Writer-`False` oder derselbe In-Memory-Zustand allein
    genuegt der G1-Forderung nicht.

    G3-Generalbefund (01_GENERALREVIEW.md §2/§4): das Kind importierte
    `setup.py` bisher OHNE eigenen Fruehschutz -- `register_child` autorisiert
    nur den Spawn im PARENT, patcht aber nichts im frischen Kindinterpreter.
    Jetzt installiert das Kind SELBST (vor dem `setup.py`-Import) einen
    eigenen Primaerguard via `bootstrap_isolation(context=...)` aus dem
    bestehenden Support (eigene minimale gebundene Umgebung/cwd, eigene
    before/after-Exporte), und der Parent zeichnet echte `record_child_
    start`/`record_child_end`-Ereignisse auf (nicht nur die Autorisierung).
    Jeder tatsaechliche Aufruf bekommt einen frischen privaten Exportordner
    (eigener `tempfile.mkdtemp`) -- kein gemeinsames ueberschriebenes
    Kindartefakt, auch wenn mehrere Aufrufe denselben zu lesenden `path`
    teilen (z.B. aktive Vorbedingung vs. spaeterer HOLD-Nachweis)."""
    _FRESH_READER_COUNTER["n"] += 1
    nonce = _FRESH_READER_COUNTER["n"]
    # R2 (01_GENERALREVIEW.md §3 "fuer den G1-Familienlauf fehlen die
    # vollstaendigen eigenen Kontexte/einzelnen Reader-Rohkanaele/gebundenen
    # Parentlaufdaten"): die eigene private Wurzel dieses EINEN Leserkindes
    # wird jetzt vom PARENT VORAB innerhalb des bereits bleibenden
    # `_G1_EVIDENCE_DIR` angelegt (statt eines unbenannten System-Tempdirs)
    # -- unter dem G3-Starter landet sie damit automatisch in dessen
    # ohnehin kopierter `fresh_tmp`-Wurzel; im Solo-/run_all-Lauf bleibt sie
    # unter der eigenen, von Main/Integrator NACH dem Lauf kopierten
    # Prozesswurzel. Das Kind erhaelt den Pfad als argv-Wert, statt ihn
    # selbst per `tempfile.mkdtemp()` an einem unbekannten Ort anzulegen.
    private_root = os.path.realpath(
        tempfile.mkdtemp(prefix=f"g1-reader-{nonce}-", dir=str(_G1_EVIDENCE_DIR))
    )
    exports_dir = os.path.join(private_root, "exports")
    os.makedirs(exports_dir, exist_ok=True)
    before_export_path = os.path.join(exports_dir, "before.json")
    after_export_path = os.path.join(exports_dir, "after.json")
    code = (
        "import importlib.util, sys, os\n"
        "from pathlib import Path\n"
        "real_home = str(Path.home())\n"
        "support_spec = importlib.util.spec_from_file_location(\n"
        "    'g1_fresh_reader_support_%d' % os.getpid(), sys.argv[3])\n"
        "support = importlib.util.module_from_spec(support_spec)\n"
        "support_spec.loader.exec_module(support)\n"
        "private_root = sys.argv[5]\n"
        "ctx = {\n"
        "    'bundle_id': 'g1-fresh-reader-' + os.path.basename(private_root),\n"
        "    'process_id': 'g1-reader-' + str(os.getpid()),\n"
        "    'role': 'g1-fresh-reader',\n"
        "    'real_home_class': real_home,\n"
        "    'repo_root': sys.argv[4],\n"
        "    'source_read_roots': [os.path.dirname(sys.argv[1])],\n"
        "    'dep_read_roots': [os.path.dirname(sys.argv[2])],\n"
        "    'private_write_roots': [private_root],\n"
        "    'shared_fixture_root': None,\n"
        "    'export_before_path': sys.argv[6],\n"
        "    'export_after_path': sys.argv[7],\n"
        "    'credential_block_roots': [],\n"
        "    'artifact_read_paths': [],\n"
        "}\n"
        "guard = support.bootstrap_isolation(context=ctx)\n"
        "guard.export_phase('before', ctx['export_before_path'], completion_status='running')\n"
        "spec = importlib.util.spec_from_file_location('g1_fresh_reader_setup', sys.argv[1])\n"
        "m = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(m)\n"
        "prov, _profile, _hold = m.resolve_model_provider(Path(sys.argv[2]))\n"
        "guard.export_phase('after', ctx['export_after_path'], completion_status='completed')\n"
        "print('PROVIDER:' + str(prov))\n"
    )
    minimal_env = {"PATH": os.environ.get("PATH", "")}
    cwd = str(_REPO_ROOT)
    # G3: Unter der frühen Offlinehülle faengt der Primaerguard JEDEN
    # `subprocess.Popen` process-weit ab und verlangt eine vorherige
    # argv-genaue `register_child`-Autorisierung (`authorize_and_consume`),
    # jetzt zusaetzlich mit gebundener cwd/env -- eine Abweichung davon wird
    # ebenfalls abgelehnt (01_GENERALREVIEW.md §2 "env/cwd nicht verbindlich
    # gebunden"). `nonce` macht jeden Aufruf-Code-String eindeutig (eigener
    # Modulalias je Aufruf), sodass mehrere Leseaufrufe auf denselben `path`
    # (aktive Vorbedingung + spaeterer HOLD-Nachweis) jeweils ein EIGENES
    # argv und damit einen eigenen, frisch verbrauchbaren Grant erhalten --
    # keine Wiederbelebung eines bereits verbrauchten Grants.
    code = f"# nonce={nonce}\n" + code
    argv = [
        sys.executable, "-c", code,
        str(_SETUP_PY), str(path), str(_SUPPORT_SCRIPT), str(_REPO_ROOT),
        private_root, before_export_path, after_export_path,
    ]
    _GUARD.register_child(
        role="g1-fresh-reader", argv=argv, fixture_paths=[str(path)],
        export_id=f"g1-fresh-reader-{nonce}", count=1,
        minimal_env=minimal_env, cwd=cwd,
    )
    start_utc = _utcnow_iso()
    proc = subprocess.Popen(
        argv, cwd=cwd, env=minimal_env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    _GUARD.record_child_start(
        role="g1-fresh-reader", pid=proc.pid, ppid=os.getpid(), argv=argv, utc=start_utc,
    )

    def _write_raw_channels(*, out, err) -> None:
        # r4-Nachzug (01_GENERALREVIEW.md §3 R2 / 02_NATIVER_RESTAUFTRAG.md
        # §D "G1-Rohkanaele vollstaendig sichern"): die ohnehin per
        # `communicate()` erhaltenen VOLLEN individuellen stdout/stderr
        # DIESES Readers werden HIER, noch vor jedem Assert/Cleanup,
        # dauerhaft unter der tatsaechlichen Kindidentitaet (`private_root`,
        # bereits an nonce/pid gebunden) gesichert. Ein tatsaechlich leerer
        # Kanal wird als existierendes leeres Original geschrieben (0-Byte-
        # Datei), NICHT als "fehlt" behandelt. Kein stderr-aus-rc-0-Schluss
        # und keine aus `provider_result` nachgebildete stdout-Datei -- `out`/
        # `err` sind die tatsaechlich empfangenen Bytes GENAU dieses Laufs.
        # Bewusst KEIN `except OSError: pass`: ein Schreibfehler HIER ist ein
        # Pflichtbewahrungsfehler und MUSS sichtbar bleiben (den Testabschluss
        # verhindern), nicht als ignorierbarer Zusatzbeleg weiterlaufen.
        Path(private_root, "stdout.txt").write_text(out if out is not None else "", encoding="utf-8")
        Path(private_root, "stderr.txt").write_text(err if err is not None else "", encoding="utf-8")

    def _write_manifest(*, end_utc: str, exit_code, provider_result) -> None:
        # R2-Laufmanifest: Quelle/Rolle/PID/PPID/argv/cwd/minimale Umgebung/
        # UTC-Start-Ende/Exit -- additiv zu den bereits bestehenden Guard-
        # internen `child_starts`/`child_ends`, als eigenstaendig lesbares
        # Original direkt in der dauerhaft gesicherten Kindwurzel. Die beiden
        # Pfadfelder unten sind reine BINDUNGSINFORMATION auf die bereits von
        # `_write_raw_channels` geschriebenen Originale (keine neue
        # Manifestdateibenennung, kein neues Dateiformat).
        manifest = {
            "role": "g1-fresh-reader", "nonce": nonce, "pid": proc.pid, "ppid": os.getpid(),
            "argv": list(argv), "cwd": cwd, "minimal_env": dict(minimal_env),
            "start_utc": start_utc, "end_utc": end_utc, "exit_code": exit_code,
            "target_path": str(path), "before_export_path": before_export_path,
            "after_export_path": after_export_path, "provider_result": provider_result,
            "stdout_path": str(Path(private_root, "stdout.txt")),
            "stderr_path": str(Path(private_root, "stderr.txt")),
        }
        # r4-Nachzug (01_GENERALREVIEW.md §3 R2 "ein OSError beim
        # Manifestschreiben wird ausdruecklich verschluckt"): das Manifest
        # bindet jetzt die bereits gesicherten Pflichtrohkanaele an diesen
        # Lauf -- kein ignorierbarer Zusatzbeleg mehr. Bewusst KEIN
        # `except OSError: pass`: ein Pflichtschreibfehler muss sichtbar
        # bleiben und den Abschluss verhindern.
        Path(private_root, "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True, default=str), encoding="utf-8",
        )

    try:
        out, err = proc.communicate(timeout=60)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, err = proc.communicate()
        end_utc = _utcnow_iso()
        _GUARD.record_child_end(role="g1-fresh-reader", pid=proc.pid, rc=proc.returncode or -1, utc=end_utc)
        _write_raw_channels(out=out, err=err)
        _write_manifest(end_utc=end_utc, exit_code=proc.returncode, provider_result=None)
        raise
    end_utc = _utcnow_iso()
    _GUARD.record_child_end(role="g1-fresh-reader", pid=proc.pid, rc=proc.returncode, utc=end_utc)
    # r4-Nachzug (01_GENERALREVIEW.md §3 R2): die vollen Rohkanaele werden
    # JETZT gesichert -- VOR dem folgenden rc-/Marker-Fehlerpfad -- damit ein
    # scheiternder Leser (rc!=0 oder fehlender Marker) die bereits
    # empfangenen Pflichtdaten nicht still verliert. Vorher brach ein
    # fehlgeschlagener `assert proc.returncode == 0` die Funktion OHNE JEDE
    # Bewahrung ab (Erfolgs-/Fehlerpfad waren nicht gleich behandelt).
    _write_raw_channels(out=out, err=err)
    if proc.returncode != 0:
        _write_manifest(end_utc=end_utc, exit_code=proc.returncode, provider_result=None)
        raise AssertionError(f"frischer Leserprozess scheiterte: {err}")
    lines = [ln for ln in out.splitlines() if ln.startswith("PROVIDER:")]
    if not lines:
        _write_manifest(end_utc=end_utc, exit_code=proc.returncode, provider_result=None)
        raise AssertionError(f"kein PROVIDER-Marker im frischen Leser: {out!r}")
    provider_result = lines[-1].split(":", 1)[1]
    # R2: Bewahrung MUSS hier, noch im Testkoerper vor jedem spaeteren
    # Cleanup, passieren -- kein spaeterer Copy nach `tearDown`. Es gibt
    # hier keine explizite tearDown-Loeschung dieser Wurzel, aber die
    # Bindung (Manifest + before/after bereits unter `_G1_EVIDENCE_DIR`)
    # muss trotzdem JETZT geschrieben sein, nicht erst nachtraeglich.
    self_check = [before_export_path, after_export_path]
    for p in self_check:
        if not Path(p).is_file():
            raise AssertionError(
                f"g1-fresh-reader {nonce}: Pflicht-Export fehlt nach dem Lauf: {p}"
            )
    _write_manifest(end_utc=end_utc, exit_code=proc.returncode, provider_result=provider_result)
    return provider_result


class _SelectiveOsOpen:
    """Ruft das ECHTE `os.open` fuer alle Pfade auf und zeichnet sie auf;
    scheitert NUR fuer die geschuetzte Transaktions-Tempdatei (`.tmp-` im
    Namen). So laeuft `pending_marker.touch()` real durch und erst der
    tatsaechliche geschuetzte Tempfile-`os.open` scheitert."""

    def __init__(self, *, fail_on_tmp: bool):
        self._real = os.open
        self.fail_on_tmp = fail_on_tmp
        self.calls: list[tuple[str, int, int]] = []

    def __call__(self, path, flags, mode=0o777, *args, **kwargs):
        s = str(path)
        self.calls.append((s, flags, mode))
        if self.fail_on_tmp and ".tmp-" in os.path.basename(s):
            raise PermissionError(13, "geschuetzte Tempdatei verweigert (simuliert)")
        return self._real(path, flags, mode, *args, **kwargs)

    @property
    def tmp_open_reached(self) -> bool:
        return any(".tmp-" in os.path.basename(s) for s, _f, _m in self.calls)

    @property
    def tmp_open_modes(self) -> list[int]:
        return [m for s, _f, m in self.calls if ".tmp-" in os.path.basename(s)]

    @property
    def tmp_open_flags(self) -> list[int]:
        return [f for s, f, _m in self.calls if ".tmp-" in os.path.basename(s)]


def test_g1_protected_tmp_open_failure_hits_real_seam_not_marker():
    """G1-Seam 1: NUR das echte `os.open` der Transaktions-Tempdatei
    (`O_CREAT|O_EXCL`, 0600) scheitert -- der Pending-Marker wurde vorher
    tatsaechlich erfolgreich angelegt. Aktives Profil: alte Bytes bleiben
    bytegleich, Marker bleibt stehen (HOLD), frischer Prozess sieht HOLD."""
    tmp = Path(tempfile.mkdtemp(prefix="g1-tmpopen-"))
    try:
        path = tmp / ".env"
        original = _active_local_profile_bytes()
        path.write_text(original, encoding="utf-8")
        before_sha = hashlib.sha256(path.read_bytes()).hexdigest()
        # G1 (01_GENERALREVIEW.md §2): VOR der selektiven Fehlerinjektion die
        # oeffentliche aktive Local-Auflösung belegen -- die als "aktiv"
        # bezeichnete Fixture muss tatsaechlich aktiv sein, nicht nur dem
        # Namen nach.
        assert _fresh_process_provider(path) == "local", "aktives Profil muss vor der Injektion lokal aufgeloest werden"

        spy = _SelectiveOsOpen(fail_on_tmp=True)
        with mock.patch.object(setup_mod.os, "open", spy):
            ok = setup_mod._update_env_file_preserving(path, {"OPENWEBUI_API_KEY": "new-value-not-secret"})

        assert ok is False, "gescheiterte geschuetzte Tempdatei-Erzeugung darf nicht True liefern"
        # Der geschuetzte Tempfile-Seam wurde tatsaechlich ERREICHT (nicht der
        # Marker als frueher Ersatz), und zwar mit O_EXCL + Modus 0600.
        assert spy.tmp_open_reached, "der geschuetzte Tempfile-os.open wurde nie erreicht"
        assert all(m == 0o600 for m in spy.tmp_open_modes), spy.tmp_open_modes
        assert all((f & os.O_EXCL) and (f & os.O_CREAT) for f in spy.tmp_open_flags), spy.tmp_open_flags
        # Alte aktive Bytes vollstaendig unveraendert.
        assert path.read_text(encoding="utf-8") == original
        assert hashlib.sha256(path.read_bytes()).hexdigest() == before_sha
        # Marker steht (HOLD); keine verwaiste Tempdatei.
        assert _marker_path(path).exists(), "Pending-Marker muss nach dem Seam-Fehler stehen (HOLD)"
        assert not list(tmp.glob(".env.tmp-*")), "verwaiste Tempdatei nicht aufgeraeumt"
        # Oeffentliche Lesesicht eines FRISCHEN Prozesses: HOLD.
        assert _fresh_process_provider(path) == "hold", "frischer Prozess muss HOLD sehen"
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def test_g1_write_call_failure_after_real_open_reaches_write_not_replace():
    """G1-Seam 2: das echte `os.open` gelingt, erst der tatsaechliche
    `fh.write(content)` scheitert -- nicht `fdopen` und kein frueherer
    Zugriff. `os.replace` wird NICHT mehr erreicht; Tempdatei aufgeraeumt,
    alte Bytes bytegleich, Marker HOLD, frischer Prozess HOLD."""
    tmp = Path(tempfile.mkdtemp(prefix="g1-write-"))
    try:
        path = tmp / ".env"
        original = _active_local_profile_bytes()
        path.write_text(original, encoding="utf-8")
        # G1 (01_GENERALREVIEW.md §2): oeffentliche aktive Local-Auflösung
        # VOR der Injektion belegen.
        assert _fresh_process_provider(path) == "local", "aktives Profil muss vor der Injektion lokal aufgeloest werden"

        real_fdopen = os.fdopen
        write_reached = {"n": 0}
        replace_reached = {"hit": False}

        class _WriteFailingHandle:
            def __init__(self, fd):
                self._fd = fd

            def __enter__(self):
                outer = self

                class _W:
                    def write(self, *_a, **_k):
                        write_reached["n"] += 1
                        raise OSError(28, "No space left on device (simuliert)")

                return _W()

            def __exit__(self, *_exc):
                os.close(self._fd)  # echten fd schliessen, kein Leak
                return False

        def _bad_fdopen(fd, *a, **k):
            return _WriteFailingHandle(fd)

        real_replace = os.replace

        def _spy_replace(src, dst):
            replace_reached["hit"] = True
            return real_replace(src, dst)

        with mock.patch.object(setup_mod.os, "fdopen", _bad_fdopen), \
             mock.patch.object(setup_mod.os, "replace", _spy_replace):
            ok = setup_mod._update_env_file_preserving(path, {"OPENWEBUI_API_KEY": "new-value-not-secret"})

        assert ok is False, "ein Schreibfehler am echten fh.write muss False liefern"
        assert write_reached["n"] == 1, "der tatsaechliche fh.write-Aufruf wurde nicht genau einmal erreicht"
        assert replace_reached["hit"] is False, "os.replace darf nach Schreibfehler NICHT erreicht werden"
        assert path.read_text(encoding="utf-8") == original, "alte Bytes muessen unveraendert bleiben"
        assert not list(tmp.glob(".env.tmp-*")), "Tempdatei nach Schreibfehler nicht aufgeraeumt"
        assert _marker_path(path).exists(), "Pending-Marker muss stehen (HOLD)"
        assert _fresh_process_provider(path) == "hold", "frischer Prozess muss HOLD sehen"
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def test_g1_atomic_replace_failure_maps_source_and_target():
    """G1-Seam 3: `os.open` + `fh.write` gelingen, erst der tatsaechliche
    atomare `os.replace(tmp_path, path)` scheitert -- mit zugeordnetem
    Quell-/Zielpfad. Tempdatei aufgeraeumt, alte Bytes bytegleich, Marker
    HOLD, frischer Prozess HOLD."""
    tmp = Path(tempfile.mkdtemp(prefix="g1-replace-"))
    try:
        path = tmp / ".env"
        original = _active_local_profile_bytes()
        path.write_text(original, encoding="utf-8")
        # G1 (01_GENERALREVIEW.md §2): oeffentliche aktive Local-Auflösung
        # VOR der Injektion belegen.
        assert _fresh_process_provider(path) == "local", "aktives Profil muss vor der Injektion lokal aufgeloest werden"

        seen = {}

        def _bad_replace(src, dst):
            seen["src"] = str(src)
            seen["dst"] = str(dst)
            raise OSError(18, "Invalid cross-device link (simuliert)")

        with mock.patch.object(setup_mod.os, "replace", _bad_replace):
            ok = setup_mod._update_env_file_preserving(path, {"OPENWEBUI_API_KEY": "new-value-not-secret"})

        assert ok is False, "ein Fehler am atomaren os.replace muss False liefern"
        # Quell-/Zielpfad korrekt zugeordnet: Temp -> endgueltige Datei.
        assert seen.get("dst") == str(path), seen
        assert ".tmp-" in os.path.basename(seen.get("src", "")), seen
        assert path.read_text(encoding="utf-8") == original, "alte Bytes muessen unveraendert bleiben"
        assert not list(tmp.glob(".env.tmp-*")), "Tempdatei nach Replace-Fehler nicht aufgeraeumt"
        assert _marker_path(path).exists(), "Pending-Marker muss stehen (HOLD)"
        assert _fresh_process_provider(path) == "hold", "frischer Prozess muss HOLD sehen"
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def test_g1_erstprofil_protected_open_failure_fresh_process_sees_hold():
    """G1-Erstprofil: ohne vorbestehende Datei scheitert die geschuetzte
    Tempfile-Erzeugung. Die Zieldatei darf NICHT mit dem ungeschuetzten neuen
    Wert entstehen; der Pending-Marker macht den verbliebenen Zustand fuer
    einen GEPLANTEN FRISCHEN Prozess ueber den oeffentlichen Leser inaktiv
    (HOLD). Ein Writer-False allein genuegt nicht."""
    tmp = Path(tempfile.mkdtemp(prefix="g1-erst-"))
    try:
        path = tmp / ".openwebui_env"  # existiert noch nicht (Erstprofil)
        spy = _SelectiveOsOpen(fail_on_tmp=True)
        # G1 (01_GENERALREVIEW.md §2): der Erstprofilkandidat muss selbst ein
        # VOLLSTAENDIGES gueltiges Localprofil sein (nicht nur Provider+OWUI-
        # Key) -- sonst waere er auch nach einem erfolgreichen Schreiben kein
        # vollstaendiges Profil gewesen.
        candidate = {
            _PROVIDER_KEY: "local",
            "ZEITRISS_LOCAL_BASE_URL": "http://127.0.0.1:11434",
            "ZEITRISS_LOCAL_MODEL": "local-test-model-not-secret",
            "ZEITRISS_LOCAL_API_KEY": "local-test-key-not-secret",
            "OPENWEBUI_API_KEY": "new-value-not-secret",
        }
        with mock.patch.object(setup_mod.os, "open", spy):
            ok = setup_mod._update_env_file_preserving(path, candidate)
        assert ok is False
        assert spy.tmp_open_reached, "der geschuetzte Tempfile-os.open wurde nie erreicht"
        # Kein ungeschuetztes neues Profil live auf Platte.
        assert (not path.exists()) or (
            "new-value-not-secret" not in path.read_text(encoding="utf-8")
        ), "der ungeschuetzte neue Wert darf nicht live auf Platte entstehen"
        assert not list(tmp.glob(".openwebui_env.tmp-*")), "verwaiste Tempdatei nicht aufgeraeumt"
        assert _marker_path(path).exists(), "Pending-Marker macht den Erstprofil-Zustand HOLD"
        # Entscheidend: ein FRISCHER Prozess sieht ueber die oeffentliche API HOLD.
        assert _fresh_process_provider(path) == "hold", "frischer Prozess muss Erstprofil als HOLD sehen"
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def test_g1_permission_requirement_met_by_oexcl_0600_creation_not_separate_chmod():
    """G1-Rechtezuordnung (Vertragswort 'chmod' -> heutige Umsetzung): die
    0600-Rechteanforderung wird durch die `os.open(..., O_CREAT|O_EXCL,
    0o600)`-Erzeugung SELBST erfuellt -- kein Secretbyte landet je in einem
    Deskriptor mit laxeren Rechten, es gibt keinen separaten nachgelagerten
    `os.chmod`-Produktaufruf (und es wird auch keiner kuenstlich ergaenzt).
    Gegenprobe Erfolgsfall: Datei persistiert mit exakt 0600."""
    import stat as _stat
    tmp = Path(tempfile.mkdtemp(prefix="g1-perm-"))
    try:
        path = tmp / ".env"
        spy = _SelectiveOsOpen(fail_on_tmp=False)  # Erfolgsfall: nichts scheitert
        chmod_calls = []
        real_chmod = os.chmod

        def _spy_chmod(p, mode, *a, **k):
            chmod_calls.append((str(p), mode))
            return real_chmod(p, mode, *a, **k)

        with mock.patch.object(setup_mod.os, "open", spy), \
             mock.patch.object(setup_mod.os, "chmod", _spy_chmod):
            ok = setup_mod._update_env_file_preserving(path, {"OPENWEBUI_API_KEY": "value-not-secret"})

        assert ok is True
        # Die geschuetzte Tempdatei wurde mit O_EXCL + 0600 erzeugt.
        assert spy.tmp_open_reached
        assert all(m == 0o600 for m in spy.tmp_open_modes), spy.tmp_open_modes
        assert all((f & os.O_EXCL) and (f & os.O_CREAT) for f in spy.tmp_open_flags), spy.tmp_open_flags
        # KEIN separater chmod-Produktaufruf auf der veroeffentlichten Datei.
        assert not any(c[0] == str(path) for c in chmod_calls), (
            f"unerwarteter separater chmod auf der Zieldatei: {chmod_calls}"
        )
        # Endzustand: exakt 0600.
        mode = _stat.S_IMODE(path.stat().st_mode)
        assert mode == 0o600, f"erwartet 0600, war {oct(mode)}"
        # Marker entfernt (Erfolg), frischer Prozess sieht KEIN HOLD mehr.
        assert not _marker_path(path).exists()
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


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
