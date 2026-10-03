#!/usr/bin/env python3
"""
tests/mmo_sim/test_i4_active_authority_subprocess.py — I4-Nachzug: aktive
Figurenautoritaet nach unterbrochenem Wechsel, mit ECHTEN neuen
Interpreterprozessen (02_ABNAHME_I4-Nachzug Wege 1-5, Vertrag §3 A/B).

Ergaenzt `test_i4_figure_continuity.py` (bleibt unveraendert -- deckt
denselben Grund-Vertrag ueberwiegend INNERHALB eines Prozesses/derselben
`Rig` ab; sein Test `test_weg1_same_process_second_tuisession_retains_a_
neu_after_a_b_a` nutzt zwar eine ZWEITE `TuiSession`-Instanz, aber KEINEN
eigenen Interpreterprozess). DIESE Datei startet fuer jeden
Uebergangsschritt, der als "frischer Prozess" gepruef wird, einen ECHTEN,
EIGENSTAENDIGEN Python-Subprozess (`subprocess.run([sys.executable,
__file__, '--child', ...])`), analog zum bereits im Repo etablierten Muster
in `e2e_real_subprocess_dialog.py`.

Deckt (02_ABNAHME_I4-Nachzug, Wege 1-5):
  - Weg 1: durchgehende Positivkontrolle ueber mehrere echte Prozesse
    (Auswahl -> echter Spielfortschritt -> Ruecktausch -> erneute Auswahl).
  - Weg 2 (T1a): nach Abbruch zwischen `core_store.publish_current_save`
    und `catalog.bind_for_section` (Current bereits B, Katalog noch A)
    darf ein spaeterer ECHTER Spielfortschritt von B plus erneute Auswahl
    von B nicht auf den alten Katalog-Importstand zurueckfallen.
  - Weg 3 (T1b): dieselbe Unterbrechung darf eine per TUI real
    tischgebundene Figur B nicht durch Auswahl/Import/Erschaffung von C/D
    ersetzen -- alle drei Uebergangswege, je eigener frischer Prozess.
  - Weg 4 (T2): ein transienter Lesefehler an der referenzierten Current-
    Versionsdatei muss den Wechsel kontrolliert blockieren statt die
    bekannte Fassung still als 'nicht vorhanden' zu behandeln und spaeter
    (in einem frischen Prozess) den alten Katalogstand zu republizieren.
  - Weg 5: kleine Interruptions-Matrix an der KORRIGIERTEN Uebergangsfolge
    -- zusaetzlich zur bereits bestehenden Naht in
    `test_i4_figure_continuity.py::test_weg4_stale_catalog_active_id_does_
    not_corrupt_outgoing_figure` (Absturz am ABSCHLIESSENDEN `bind_for_
    section`) hier zwei WEITERE Absturzpunkte: die NEUE Selbstheilungs-
    Bindung in `_resolve_real_active_chrononaut_id` und die Ausgangs-
    sicherung (`catalog.store_figure_save` in `_sync_outgoing_active_
    figure`). An keiner der drei Naehte darf eine Figurenvertauschung oder
    ein falsch gespeicherter Fortschritt entstehen.

Weg 6 (inaktive Zielkonflikte/Teilnehmertrennung) wird durch die bereits
bestehenden, von diesem Nachzug unveraendert erhaltenen Tests
`test_weg3_inactive_figure_*`/`test_weg5_two_participants_keep_independent_
bindings` in `test_i4_figure_continuity.py` abgedeckt (reine
Importkonflikt-/Registry-Logik, keine Prozessgrenze betroffen) -- keine
redundante Zweitausfuehrung hier.

Pure Python, nur `assert`, echter Exitcode. Providerfrei (synthetisches
GM-/Treiber-Double, kein externer Modellaufruf, kein HTTP)."""
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
from mmo_sim.ui.tui import EndOfInput, TuiSession  # noqa: E402

_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"

_pa = argparse.ArgumentParser(add_help=False)
_pa.add_argument("--child", choices=["select", "play_then_select", "bound_attempt"])
_pa.add_argument("--base", type=Path)
_pa.add_argument("--target")
_pa.add_argument("--method", default="select")
_pa.add_argument("--allow-safe-block", action="store_true")
_ARGS, _REMAINING = _pa.parse_known_args()


def _ui(base: Path, inputs=(), shown=None, gm=None) -> TuiSession:
    return TuiSession(
        base / "onboarding", base / "catalog", "sniper", input_fn=t4._script(inputs),
        print_fn=(shown.append if shown is not None else (lambda _x: None)),
        run_dir=base / "run", states_dir=base / "states", schema_path=_SCHEMA,
        gm_transport_factory=(lambda: gm) if gm is not None else None,
    )


def _cur(base: Path) -> dict | None:
    return store.load_current_save(base / "run", "sniper", PersonaStateStore(_SCHEMA), states_dir=base / "states")


def _summary(base: Path) -> dict:
    blk = _cur(base)
    st = PersonaStateStore(_SCHEMA).load_state("sniper", states_dir=base / "states")
    return {
        "current": blk,
        "current_char": saves.block_char_id(blk) if blk else None,
        "catalog_active": catalog.active_chrononaut_id(base / "catalog", "sniper"),
        "plays_char": st.get("plays_char"),
        "rounds": st.get("rounds_played"),
    }


def _child_run(mode: str, base: Path, target=None, method=None, allow_safe_block=False) -> dict:
    cmd = [sys.executable, str(Path(__file__).resolve()), "--child", mode, "--base", str(base)]
    if target:
        cmd += ["--target", target]
    if method:
        cmd += ["--method", method]
    if allow_safe_block:
        cmd += ["--allow-safe-block"]
    env = {k: v for k, v in os.environ.items() if not any(x in k.upper() for x in ("TOKEN", "SECRET", "API_KEY"))}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    p = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=base, timeout=40)
    if p.returncode:
        raise RuntimeError(f"Child-Subprozess fehlgeschlagen (exit={p.returncode}): {p.stdout}\n{p.stderr}")
    return json.loads(p.stdout)


def _play_b(base: Path, shown: list) -> tuple[dict, list]:
    bnew = copy.deepcopy(_cur(base))
    bnew["save_id"] = "synthetic-B-after-accepted-section-002"
    tid = "local-sniper"
    gm = t4._GM(["Die Szene laeuft.", t4._final_text({"sniper": bnew}, tid, tid + "-section")])
    _ui(base, ["Beginnen", "Fortfahren", ""], shown, gm)._cmd_local_round()
    assert _cur(base) == bnew, "Positive Spielvorbereitung muss B_neu wirklich vor dem Retry publizieren"
    assert store.Table.load(base / "run", tid).status == "closed"
    return bnew, gm.calls


def _child() -> None:
    base = _ARGS.base
    shown: list = []
    rec: dict = {"pid": os.getpid()}
    if _ARGS.child == "select":
        try:
            _ui(base, [_ARGS.target], shown)._cmd_new_or_switch_character()
        except Exception as exc:
            rec["controlled_exception"] = f"{type(exc).__name__}: {exc}"
    elif _ARGS.child == "play_then_select":
        before_play = _summary(base)
        try:
            bnew, calls = _play_b(base, shown)
        except Exception as exc:
            if not _ARGS.allow_safe_block:
                raise
            rec.update(
                blocked_before_progress=True, controlled_exception=f"{type(exc).__name__}: {exc}",
                before=before_play, after=_summary(base), shown=shown,
            )
            print(json.dumps(rec, ensure_ascii=False))
            return
        rec["expected_bnew"] = bnew
        rec["gm_calls"] = calls
        try:
            _ui(base, [_ARGS.target], shown)._cmd_new_or_switch_character()
        except Exception as exc:
            rec["controlled_exception"] = f"{type(exc).__name__}: {exc}"
    elif _ARGS.child == "bound_attempt":
        before = _cur(base)
        tid = "local-sniper"
        gm = t4._GM(["Der Abschnitt bleibt offen."])
        start_error = None
        try:
            _ui(base, ["Beginnen"], shown, gm)._cmd_local_round()
        except EndOfInput:
            pass
        except Exception as exc:
            start_error = f"{type(exc).__name__}: {exc}"
        try:
            table = store.Table.load(base / "run", tid)
        except FileNotFoundError:
            table = None
        if start_error or table is None:
            if not _ARGS.allow_safe_block:
                raise RuntimeError(f"Unerwarteter Tischstart-Fehlschlag: {start_error}")
            rec.update(
                blocked_before_play=True, controlled_exception=start_error, before=before,
                gm_calls=gm.calls, after=_summary(base), shown=shown,
            )
            print(json.dumps(rec, ensure_ascii=False))
            return
        assert table.status == "active" and table.chrononaut_ids["sniper"] == saves.block_char_id(before), \
            "Setup muss die ECHTE aktuelle Figur B ueber die UI binden"
        assert store.chrononaut_active_binding(base / "run", saves.block_char_id(before))
        rec.update(before=before, table_before=dict(table.chrononaut_ids), gm_calls=gm.calls)
        try:
            if _ARGS.method == "select":
                _ui(base, [_ARGS.target], shown)._cmd_new_or_switch_character()
            elif _ARGS.method == "import":
                incoming = copy.deepcopy(catalog.load_figure_save(base / "catalog", "sniper", _ARGS.target))
                incoming["save_id"] = "synthetic-C-external-update"
                _ui(base, [json.dumps(incoming), "ENDE", "a", "w"], shown)._cmd_import()
            elif _ARGS.method == "create":
                cb = copy.deepcopy(t4._sv("face"))
                cb["characters"][0]["id"] = "CHR-I4AA-NEW-D"
                cb["characters"][0]["char_id"] = "CHR-I4AA-NEW-D"
                cb["char_id"] = "CHR-I4AA-NEW-D"
                cb["save_id"] = "synthetic-D-created"
                cg = t4._GM(["```json\n" + json.dumps(cb) + "\n```"])
                _ui(base, ["neu"], shown, cg)._cmd_new_or_switch_character()
                rec["creation_gm_calls"] = cg.calls
        except Exception as exc:
            rec["controlled_exception"] = f"{type(exc).__name__}: {exc}"
        rec["table_after"] = store.Table.load(base / "run", tid).chrononaut_ids
    rec["after"] = _summary(base)
    rec["shown"] = shown
    print(json.dumps(rec, ensure_ascii=False))


def _setup(base: Path, include_c: bool = False):
    r = t4.Rig(base, ("sniper",))
    anew = t4._progressed(r)
    b = t4._sv("tech")
    bid = saves.block_char_id(b)
    r.ui(inputs=[json.dumps(b), "ENDE", "b"])._cmd_import()
    cid = None
    if include_c:
        c = t4._sv("face")
        cid = saves.block_char_id(c)
        r.ui(inputs=[json.dumps(c), "ENDE", "b"])._cmd_import()
    return r, anew, b, bid, cid


def _interrupted_switch(r, bid: str) -> dict:
    """Reproduziert die reale I4-Unterbrechung: `catalog.bind_for_section`
    schlaegt GENAU EINMAL fehl, NACHDEM `core_store.publish_current_save`
    (im Produktcode unveraendert) bereits gelaufen ist -- derselbe Zeitpunkt
    wie im End-Critic-Befund/02_ABNAHME_I4-Nachzug."""
    hit = 0

    def _fail(*_a, **_kw):
        nonlocal hit
        hit += 1
        raise OSError("INJECT nach Current-Publikation, vor Katalog-Aktivierung")

    err = None
    with patch.object(catalog, "bind_for_section", side_effect=_fail):
        try:
            r.ui(inputs=[bid])._cmd_new_or_switch_character()
        except OSError as exc:
            err = str(exc)
    assert hit == 1 and err, "Injektion muss die reale Katalog-Bindungsnaht treffen"
    assert saves.block_char_id(_cur(r.base)) == bid, "Current B muss vor dem injizierten Fehler publiziert sein"
    assert catalog.active_chrononaut_id(r.cat, "sniper") == r.ids["sniper"], \
        "Katalog muss an dieser Naht noch A zeigen"
    return {"hits": hit, "error": err, "after_failure": _summary(r.base)}


# ── Weg 1: durchgehende Positivkontrolle ueber echte neue Prozesse ─────────

def test_i4aa_weg1_real_subprocess_roundtrip():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r, anew, b, bid, _cid = _setup(base)
        p1 = _child_run("select", base, bid)
        assert p1["after"]["current"] == b, "frischer Prozess: Auswahl von B muss B's eigene Bytes publizieren"
        p2 = _child_run("play_then_select", base, r.ids["sniper"])
        assert p2["after"]["current"] == anew, "frischer Prozess: Rueckwechsel zu A muss A_neu liefern"
        p3 = _child_run("select", base, bid)
        assert p3["after"]["current"] == p2["expected_bnew"], \
            "frischer Prozess: erneute Auswahl von B muss den zwischenzeitlich erspielten B-Fortschritt liefern"


# ── Weg 2 (T1a): unterbrochener Wechsel darf echten B-Fortschritt nicht zuruecksetzen ──

def test_i4aa_weg2_interrupted_switch_must_not_roll_back_real_b_progress():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r, anew, b, bid, _cid = _setup(base)
        _interrupted_switch(r, bid)
        c = _child_run("play_then_select", base, bid, allow_safe_block=True)
        expected = c["before"]["current"] if c.get("blocked_before_progress") else c["expected_bnew"]
        assert c["after"]["current"] == expected, \
            "Auswahl der real aktuellen Figur B (frischer Prozess) nach unterbrochener Bindung muss B_neu erhalten"


# ── Weg 3 (T1b): unterbrochener Wechsel darf reale Tischbindung nicht umgehen ──

def test_i4aa_weg3_interrupted_switch_binding_survives_select_import_create():
    for method in ("select", "import", "create"):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            r, anew, b, bid, cid = _setup(base, include_c=True)
            _interrupted_switch(r, bid)
            c = _child_run("bound_attempt", base, cid, method, allow_safe_block=True)
            assert c["after"]["current"] == c["before"], \
                f"[{method}] tischgebundene Current-Figur B darf nicht ersetzt werden (frischer Prozess)"
            assert c["after"]["plays_char"].get("character_id") == bid, \
                f"[{method}] plays_char muss an B gebunden bleiben (frischer Prozess)"


# ── Weg 4 (T2): Lesefehler an der bekannten Current-Version muss blockieren ──

def test_i4aa_weg4_current_read_error_blocks_instead_of_silent_reset():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r, anew, b, bid, _cid = _setup(base)
        state = r.ps.load_state("sniper", states_dir=r.states)
        ref = state["current_save_version"]
        seq = ref["seq"]
        vp = r.run / "current_saves" / "sniper__versions" / f"{int(seq):04d}.json"
        assert vp.is_file()
        original = Path.read_text
        hit = 0

        def _fail(path, *args, **kwargs):
            nonlocal hit
            if path == vp and hit == 0:
                hit += 1
                raise OSError("INJECT transienter Current-Versions-Lesefehler waehrend Ausgangssync")
            return original(path, *args, **kwargs)

        with patch.object(Path, "read_text", _fail):
            r.ui(inputs=[bid])._cmd_new_or_switch_character()
        assert hit == 1, "Leseinjektion muss tatsaechlich feuern"
        c = _child_run("select", base, r.ids["sniper"])
        assert c["after"]["current"] == anew, \
            "ein bekannter, gerade nicht lesbarer Current-Save darf nicht durch den alten Katalogstand " \
            "ersetzt werden (frischer Prozess bestaetigt A_neu bleibt massgeblich)"


# ── Weg 5: kleine Interruptions-Matrix an zusaetzlichen Absturzpunkten ─────
# (Punkt 1 -- Absturz am ABSCHLIESSENDEN `bind_for_section` -- ist bereits
# `test_i4_figure_continuity.py::test_weg4_stale_catalog_active_id_does_not_
# corrupt_outgoing_figure`. Hier zwei WEITERE Naehte derselben korrigierten
# Uebergangsfolge.)

def test_i4aa_weg5a_interruption_at_self_heal_bind_keeps_consistent_state():
    """Absturz an der NEUEN Selbstheilungs-Naht (`catalog.bind_for_section`
    innerhalb `_resolve_real_active_chrononaut_id`): Current traegt bereits
    B (unverspielter Import) nach einem fruehen unterbrochenen Wechsel,
    Katalog zeigt noch veraltet A. Ein weiterer Wechselversuch (zu C) muss
    beim Selbstheil-Bind kontrolliert abbrechen koennen, OHNE Current zu
    veraendern oder A's bereits gesicherte eigene Fassung zu beschaedigen."""
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r, anew, b, bid, _cid = _setup(base)
        _interrupted_switch(r, bid)
        # C wird DIREKT ueber den Katalog registriert (kein UI-Aufruf, der
        # ueber `_resolve_real_active_chrononaut_id` bereits vorher
        # selbstheilen wuerde) -- reiner Testaufbau, kein Produktpfad.
        c = t4._sv("face")
        cid = saves.block_char_id(c)
        catalog.register(r.cat, catalog.CatalogEntry(participant_id="sniper", chrononaut_id=cid, persona_key="sniper"))
        catalog.store_figure_save(r.cat, "sniper", cid, c)
        assert catalog.active_chrononaut_id(r.cat, "sniper") == r.ids["sniper"], \
            "Testaufbau: Katalog muss vor der Injektion noch A zeigen"

        hit = 0
        real_bind = catalog.bind_for_section

        def _fail(*_a, **_kw):
            nonlocal hit
            hit += 1
            raise OSError("INJECT an der Selbstheilungs-Bindungsnaht")

        catalog.bind_for_section = _fail
        entries = catalog.list_for_participant(r.cat, "sniper")
        ui = r.ui()
        try:
            try:
                ui._switch_active_figure(cid, entries)
                raise AssertionError("der injizierte Fehler haette propagieren muessen")
            except OSError:
                pass
        finally:
            catalog.bind_for_section = real_bind
        assert hit >= 1, "Injektion muss feuern"
        current_after = _cur(base)
        assert current_after is not None and saves.block_char_id(current_after) == bid, \
            "Current darf durch den Absturz an der Selbstheilungs-Naht nicht auf eine dritte, " \
            "nie publizierte Figur springen"
        assert catalog.load_figure_save(r.cat, "sniper", r.ids["sniper"]) == anew, \
            "A's eigene Katalogfassung darf durch den Absturz nicht beschaedigt werden"


def test_i4aa_weg5b_interruption_at_outgoing_store_figure_save_keeps_consistent_state():
    """Zweite zusaetzliche Naht: Absturz WAEHREND `_sync_outgoing_active_
    figure`s `catalog.store_figure_save`-Schreibung (Ausgangssicherung),
    NACH der reinen Lese-/Selbstheilungsphase, VOR dem eigentlichen
    Aktivwechsel-Publish. Weder Current noch der Katalog-Aktivzeiger duerfen
    dadurch veraendert werden -- der Fehler muss VOR jedem weiteren Write
    propagieren."""
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r, anew, b, bid, _cid = _setup(base)
        # Katalog ist hier akkurat (A aktiv, kein vorheriger Absturz) --
        # gezielter Absturz NUR an der Ausgangssicherung.
        hit = 0
        real_store = catalog.store_figure_save

        def _fail(*_a, **_kw):
            nonlocal hit
            hit += 1
            raise OSError("INJECT an der Ausgangssicherungs-Schreibung")

        catalog.store_figure_save = _fail
        entries = catalog.list_for_participant(r.cat, "sniper")
        ui = r.ui()
        try:
            try:
                ui._switch_active_figure(bid, entries)
                raise AssertionError("der injizierte Fehler haette propagieren muessen")
            except OSError:
                pass
        finally:
            catalog.store_figure_save = real_store
        assert hit == 1, "Injektion muss genau einmal feuern"
        current_after = _cur(base)
        assert current_after == anew, "Current darf vor dem eigentlichen Wechsel-Publish nicht springen"
        assert catalog.active_chrononaut_id(r.cat, "sniper") == r.ids["sniper"], \
            "Katalog muss A weiterhin als aktiv fuehren (Bind lief nie)"


if _ARGS.child:
    _child()
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
