#!/usr/bin/env python3
"""
tests/mmo_sim/test_h02_h09_headless_lab_journey.py — neue dauerhafte
Regressionen fuer den Headless-/Lab-Lobbydurchstich (Bau-GO 2026-09-27,
02_ABNAHME.md H02/H07/H08/H09).

H02/H07 vollstaendige positive Reise NUR ueber `scripts/mmo_sim.py lab
    start`/`lab resume` (ECHTE, geschlossene-stdin-Subprozesse, ECHTE
    Factories, Loopback-HTTP fuer Persona UND GM) -- kein Testhelper baut
    Angebot/Tisch/Abschnitt ausserhalb des Produktwegs. `lab start` mit
    `MMO_SIM_LOBBY_INITIATIVE_LIMIT=1` stellt genau das eigene Angebot;
    `lab resume` (NEUER Prozess) nimmt es auf, spielt den Abschnitt zu einem
    gueltigen Abschluss und kehrt in die Lobby zurueck.
H08 beide Providerprofile ueber tatsaechliche Adaptergrenzen: `--profile
    hybrid` mit einer ECHTEN, aber ersetzten ausfuehrbaren Fake-CLI (kein
    echtes `claude`, kein Login) UND ein Fehlerfall (Fake-CLI liefert rc!=0)
    ohne API-Fallback.
H09 Menschen und Beobachtung bleiben getrennt: `lobby_flow.play_bound_table`
    haelt an (WAITING_HUMAN), sobald ein Tischmitglied ausserhalb der
    ausdruecklich gewaehlten KI-Personamenge liegt -- OHNE fuer irgendein
    Mitglied dieses Tisches einen KI-Treiber zu konstruieren (kein
    automatischer Adapterwechsel)."""
from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from mmo_sim.core import lobby_flow  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core import lobby_service  # noqa: E402
from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER, ZeitrissTableSizePolicy  # noqa: E402
from mmo_sim.lab import runner as lab_runner  # noqa: E402

from test_l01_l10_lobby_initiative import (  # noqa: E402
    _FIX, _bootstrap_community, _make_ready, _persona_http_server, _session,
)

_MMO_SIM = _REPO_ROOT / "scripts" / "mmo_sim.py"


def _run_lab(args: list[str], env_extra: dict | None = None, timeout: int = 30) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.update(env_extra or {})
    return subprocess.run(
        [sys.executable, str(_MMO_SIM), "lab", *args],
        stdin=subprocess.DEVNULL, capture_output=True, text=True, env=env, timeout=timeout,
    )


def test_h02_h07_full_journey_start_then_resume_real_subprocess_loopback():
    """H02/H07: 'lab start' (1 echter Request: sniper stellt sein eigenes
    Angebot, Fenster endet danach kontrolliert wegen --max-idle-windows 1,
    KEIN zweiter Request in diesem Prozess) -> 'lab resume' (NEUER Prozess,
    NEUE `LabRunner`-Instanz) nimmt das noch offene eigene Angebot auf (kein
    doppeltes Angebot), tech stimmt zu, der Tisch wird real bis zum
    gueltigen Abschluss gespielt (Saves/Reflexion), und kehrt in die Lobby
    zurueck."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = ["sniper", "tech"]
        _schema, _states, run_dir, onboarding_dir, _catalog = _bootstrap_community(root, "community-h02", keys)
        for pk in keys:
            _make_ready(onboarding_dir, _states, run_dir, pk)

        with _persona_http_server([
            (200, {"choices": [{"message": {"content": json.dumps({"action": "propose", "wants": ["tech"]})}}]}),
        ]) as persona_srv_1:
            env1 = {
                "MMO_SIM_PERSONA_API_BASE_URL": persona_srv_1.base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTH", "MMO_SIM_PERSONA_API_MODEL": "synthetic-h02",
                "MMO_SIM_LOBBY_INITIATIVE_LIMIT": "1",
            }
            p1 = _run_lab([
                "start", "--data-dir", str(root), "--community", "h02", "--profile", "api",
                "--max-requests", "20", "--max-seconds", "120", "--max-usd", "5.0", "--max-idle-windows", "1",
            ], env_extra=env1)
            assert p1.returncode == 0, p1.stdout + p1.stderr
            assert "schlaegt eine Runde vor" in p1.stdout, p1.stdout
            assert len(persona_srv_1.calls) == 1

        offers_after_p1 = [r for r in lobby_service.read_offer_log(run_dir) if r.get("type") == "offer"]
        assert len(offers_after_p1) == 1, "genau EIN Angebot nach 'lab start' erwartet"
        offer_id = offers_after_p1[0]["offer_id"]
        table_id, section_id = "lobby-sniper-tech", "lobby-sniper-tech-section"
        final_saves = {pk: json.loads((_FIX / f"{pk}.json").read_text(encoding="utf-8")) for pk in keys}
        debrief_blocks = "\n".join(
            f"```json\n{json.dumps(b, ensure_ascii=False)}\n```" for b in final_saves.values()
        )

        with _persona_http_server([
            (200, {"choices": [{"message": {
                "content": f"ENTSCHEIDUNG offer_id={offer_id} participant_id=tech decision=accept explanation=Ja.",
            }}]}),
            (200, {"choices": [{"message": {"content": "Wir sichern das Gebiet."}}]}),  # sniper Leader-Anker
            (200, {"choices": [{"message": {"content": "Ich bin bereit."}}]}),  # tech Gast-Import
            (200, {"choices": [{"message": {"content": "Ich nehme mit, dass wir gut zusammengespielt haben."}}]}),
            (200, {"choices": [{"message": {"content": "Ich nehme mit, dass ich gut gedeckt war."}}]}),
        ]) as persona_srv_2, _persona_http_server([
            (200, {"choices": [{"message": {"content": "Ihr steht bereit. Was tut ihr?"}}]}),
            (200, {"choices": [{"message": {
                "content": f"{debrief_blocks}\n{COMPLETION_MARKER} table_id={table_id} section_id={section_id}",
            }}]}),
        ]) as gm_srv_2:
            env2 = {
                "MMO_SIM_PERSONA_API_BASE_URL": persona_srv_2.base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTH", "MMO_SIM_PERSONA_API_MODEL": "synthetic-h02b",
                "OPENWEBUI_URL": gm_srv_2.base_url, "OPENWEBUI_API_KEY": "SYNTH",
                # H-E/Q07: unter einem harten `--max-usd` braucht die GM-Rolle
                # eine bekannte Ausgabegrenze, sonst blockiert `read_admission_
                # block` jede weitere Anfrage NACH dem Tischstart (Kein
                # durchsetzbares Ausgabe-/Gesamtlimit UND hartes max_usd
                # konfiguriert) -- realer Betreiber-Konfigpunkt, kein Testbug.
                "MMO_SIM_GM_OUTPUT_LIMIT_TOKENS": "2000",
            }
            p2 = _run_lab([
                "resume", "--data-dir", str(root), "--community", "h02", "--profile", "api",
                "--max-requests", "20", "--max-seconds", "120", "--max-usd", "5.0", "--max-idle-windows", "1",
            ], env_extra=env2)
            assert p2.returncode == 0, p2.stdout + p2.stderr
            assert "schlaegt eine Runde vor" not in p2.stdout, (
                f"sniper haette sein bereits offenes Angebot NICHT erneut stellen duerfen: {p2.stdout}"
            )
            assert "antwortet auf Angebot" in p2.stdout and "accept" in p2.stdout, p2.stdout
            assert "Lobby-Tisch abgeschlossen" in p2.stdout, p2.stdout

        offers_after_p2 = [r for r in lobby_service.read_offer_log(run_dir) if r.get("type") == "offer"]
        assert len(offers_after_p2) == 1, "kein zweites/doppeltes Angebot durch 'lab resume' entstanden"
        table = core_store.Table.load(run_dir, table_id)
        assert table.status == "closed" and set(table.members) == {"sniper", "tech"}
        assert core_store._read_locks(run_dir) == {}, "Locks nach Abschluss geloest -- Rueckkehr in die Lobby"

        status = lab_runner.read_status(run_dir)
        # turns_used zaehlt JEDEN admission-gepflichtigen Request (Persona
        # UND GM, s. `core.request_ledger.begin` -> `admission.
        # record_turn_usage`) -- der exakte Wert haengt von der Turnanzahl
        # innerhalb `run_full_section` ab; die H07-Kerneigenschaft ist, dass
        # 'lab resume' den bereits verbrauchten Turn aus 'lab start' (1)
        # FORTSETZT statt zurueckzusetzen.
        real_requests_in_resume = len(persona_srv_2.calls) + len(gm_srv_2.calls)
        assert status.turns_used >= 1 + real_requests_in_resume, (
            f"Resume-Verbrauch ({status.turns_used}) haette den Start-Verbrauch (1) UND alle "
            f"real erfolgten Resume-Requests ({real_requests_in_resume}) umfassen sollen"
        )
        assert status.turns_used > 1, "Resume darf den Verbrauch aus 'lab start' nicht verwerfen/zuruecksetzen"


_FAKE_CLI_TEMPLATE = '''#!/usr/bin/env python3
import json
import sys

MARKER_PATH = {marker_path!r}
FAIL_MARKER_PATH = {fail_marker_path!r}
RESULT_TEXT = {result_text!r}

with open(MARKER_PATH, "a", encoding="utf-8") as fh:
    fh.write(json.dumps({{"argv": sys.argv[1:]}}) + "\\n")

if "--help" in sys.argv:
    print("Usage: fake-claude [options]\\n  --permission-mode <mode>  restrict tool execution\\n  --safe-mode  skip hooks, MCP servers, settings, plugins")
    sys.exit(0)
if "--version" in sys.argv:
    print("fake-claude 0.0.0-test")
    sys.exit(0)

import os
if FAIL_MARKER_PATH and os.path.exists(FAIL_MARKER_PATH):
    print("simulated CLI failure", file=sys.stderr)
    sys.exit(1)

sys.stdin.read()
print(json.dumps({{"type": "result", "subtype": "success", "is_error": False, "result": RESULT_TEXT, "usage": {{}}}}))
'''


def _write_fake_cli(
    root: Path, marker_path: Path, *, fail_marker_path: Path | None = None, result_text: str = '{"action": "pause"}',
) -> Path:
    """`_CHILD_ENV_ALLOWLIST` (`adapters/persona_claude_code.py`) reicht dem
    tatsaechlichen `decide()`-Subprozessaufruf NUR PATH/HOME/LANG/LC_ALL/
    TMPDIR/TERM/SHELL durch -- eigene Testsignal-Env-Vars (Marker/Fail/
    Ergebnistext) waeren dort unsichtbar (nur die separaten `--version`/
    `--help`-Isolationschecks in `check_isolation()` erben die volle
    Umgebung). Die Marker-/Fail-/Ergebnispfade werden deshalb HIER, beim
    Erzeugen des Skripts, als Literale eingebettet -- kein Env-Zustand noetig."""
    path = root / "fake_claude.py"
    path.write_text(
        _FAKE_CLI_TEMPLATE.format(
            marker_path=str(marker_path),
            fail_marker_path=str(fail_marker_path) if fail_marker_path else "",
            result_text=result_text,
        ),
        encoding="utf-8",
    )
    path.chmod(path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return path


def test_h08_hybrid_profile_real_fake_cli_subprocess_positive_and_failure():
    """H08: Hybrid-Profil (`--profile hybrid`, `--max-usd` fuer API-Anteile)
    treibt die ECHTE `PersonaClaudeCodeDriver`-Adapterklasse gegen eine
    ersetzte, ausfuehrbare Fake-CLI (kein echtes `claude`, kein Login) --
    positiver Durchstich (ein echter Subprozessaufruf, Marker-Datei beweist
    die tatsaechliche Ausfuehrung) UND ein Fehlerfall (Fake-CLI rc=1) OHNE
    API-Fallback (keine `MMO_SIM_PERSONA_API_*`-Variable gesetzt).

    F3-Fix (Critic-Nacharbeit, Bau-GO 2026-09-27, REVIEW-TEILSTAND.md §5):
    die alte Assertion `status.max_usd is None` widersprach bereits dem
    G2b-Auftrag (endliches API-Budget auch im Hybrid, CLI-Quota getrennt).
    Semantische Testkorrektur (kein Produkt-/API-SL-Rueckbau): beide
    Lab-Aufrufe erhalten jetzt ein explizites `--max-usd 5`, die Assertion
    prueft `status.max_usd == 5`."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = ["sniper"]
        _schema, _states, run_dir, onboarding_dir, _catalog = _bootstrap_community(root, "community-h08", keys)
        _make_ready(onboarding_dir, _states, run_dir, "sniper")
        marker = root / "fake_cli_calls.jsonl"
        fake_cli = _write_fake_cli(root, marker, result_text='{"action": "pause"}')

        env = {
            "MMO_SIM_PERSONA_CLI": str(fake_cli),
            "MMO_SIM_PERSONA_ISOLATION_FLAGS": "--permission-mode=plan,--safe-mode",
        }
        p_ok = _run_lab([
            "start", "--data-dir", str(root), "--community", "h08", "--profile", "hybrid",
            "--max-requests", "3", "--max-seconds", "60", "--max-idle-windows", "1", "--max-usd", "5",
        ], env_extra=env)
        assert p_ok.returncode == 0, p_ok.stdout + p_ok.stderr
        assert "'sniper' pausiert" in p_ok.stdout, p_ok.stdout
        assert marker.exists() and marker.read_text(encoding="utf-8").strip(), (
            "Fake-CLI haette real (echter Subprozess) aufgerufen werden muessen"
        )
        status = lab_runner.read_status(run_dir)
        assert status.max_usd == 5, "Hybrid muss die explizite API-Dollargrenze erhalten; CLI-Quota ist davon getrennt"

        # Fehlerfall: Fake-CLI liefert rc=1 -- kein API-Fallback (keine
        # MMO_SIM_PERSONA_API_*-Variable in `env` gesetzt, s.o.).
        fail_marker = root / "fake_cli_should_fail"
        fail_marker.write_text("1", encoding="utf-8")
        _write_fake_cli(root, marker, fail_marker_path=fail_marker, result_text='{"action": "pause"}')
        p_fail = _run_lab([
            "resume", "--data-dir", str(root), "--community", "h08", "--profile", "hybrid",
            "--max-requests", "3", "--max-seconds", "60", "--max-idle-windows", "1", "--max-usd", "5",
        ], env_extra=env)
        assert p_fail.returncode == 0, p_fail.stdout + p_fail.stderr  # geordneter Stop, kein Absturz.
        assert "fehlgeschlagen" in p_fail.stdout, p_fail.stdout
        assert "openai_compatible" not in p_fail.stdout and "PersonaApiDriver" not in p_fail.stdout


def test_h09_waiting_human_no_driver_constructed_for_any_member():
    """H09: ein Tisch mit einem Mitglied ausserhalb der ausdruecklich
    gewaehlten KI-Personamenge (hier: ein zweiter, NICHT ausgewaehlter
    Community-Persona-Key -- Stellvertreter fuer 'nicht von diesem Lab
    gespielt', z.B. weil er tatsaechlich ein menschlicher Teilnehmer waere)
    haelt mit WAITING_HUMAN an, OHNE fuer IRGENDEIN Mitglied dieses Tisches
    einen KI-Treiber zu konstruieren (kein Teil-Adapterwechsel)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = ["sniper", "tech"]
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = _bootstrap_community(
            root, "community-h09", keys,
        )
        for pk in keys:
            _make_ready(onboarding_dir, states_dir, run_dir, pk)

        lobby = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        for pk in keys:
            lobby.join(pk)
        from mmo_sim.core.store import load_current_save_or_raise
        from mmo_sim.core.persona_state import PersonaStateStore
        ps_store = PersonaStateStore(schema_path=schema_path)
        chrono_ids = {}
        active_saves = {}
        for pk in keys:
            save = load_current_save_or_raise(run_dir, pk, ps_store, states_dir=states_dir)
            from mmo_sim.domain.zeitriss import saves as zeitriss_saves
            chrono_ids[pk] = zeitriss_saves.block_char_id(save)
            active_saves[pk] = save
        offer_events = [
            {"type": "offer", "id": "offer-h09", "from": "sniper", "wants": ["tech"], "window_id": "w0"},
            {"type": "consent", "offer_id": "offer-h09", "from": "tech", "accept": True},
        ]
        table, derivation = core_store.create_table_from_offer_log(
            lobby, "lobby-sniper-tech-h09", offer_events, chrono_ids,
        )
        assert table is not None, derivation.reason

        def _raising_driver_factory(pk):
            raise AssertionError(f"kein KI-Treiber fuer '{pk}' erwartet -- Tisch enthaelt Nicht-KI-Mitglied (H09)")

        printed: list[str] = []
        session = _session(
            "op", onboarding_dir, catalog_dir, run_dir, states_dir, schema_path,
            gm_transport_factory=lambda *_a, **_kw: (_ for _ in ()).throw(AssertionError("kein GM-Call erwartet")),
            persona_driver_factory=_raising_driver_factory,
            printed=printed,
        )
        outcome = lobby_flow.play_bound_table(
            session, lobby, table, offer_events, "offer-h09", active_saves,
            ai_personas=frozenset({"sniper"}),  # 'tech' ist NICHT ausgewaehlt -> Stellvertreter fuer Mensch.
        )
        assert outcome.kind == lobby_flow.LobbyOutcomeKind.WAITING_HUMAN, outcome
        assert "tech" in outcome.reason, outcome.reason
        assert table.status != "closed", "kein Spielstart erwartet"


if __name__ == "__main__":
    import traceback

    tests = [
        test_h02_h07_full_journey_start_then_resume_real_subprocess_loopback,
        test_h08_hybrid_profile_real_fake_cli_subprocess_positive_and_failure,
        test_h09_waiting_human_no_driver_constructed_for_any_member,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print(f"OK   {t.__name__}")
            passed += 1
        except Exception:
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
            failed += 1
    print(f"\n{passed}/{len(tests)} Tests bestanden.")
    sys.exit(0 if failed == 0 else 1)
