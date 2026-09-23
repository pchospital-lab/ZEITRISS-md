#!/usr/bin/env python3
"""
tests/mmo_sim/test_m1_adapters.py — M1-Adapter offline an der echten
Prozess-/HTTP-Grenze geprueft (03/04). Kein Fixture-Runner als Liveadapter:
die tatsaechlichen Adapterklassen (`PersonaApiDriver`, `PersonaClaudeCodeDriver`)
laufen unveraendert, nur `subprocess`/HTTP-Server werden gefaked.

Pure Python, nur `assert`, echter Exitcode. Ausgehende Bytes/Flags werden
tatsaechlich inspiziert (nicht nur Rueckgabewert)."""
from __future__ import annotations

import json
import logging
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

from mmo_sim.adapters.base import ProviderAuthError, ProviderQuotaError, ProviderUnavailableError  # noqa: E402
from mmo_sim.adapters.fakes import FakeCLIProcess, FakeHTTPServer  # noqa: E402
from mmo_sim.adapters.persona_api import PersonaApiConfig, PersonaApiDriver  # noqa: E402
from mmo_sim.adapters.persona_claude_code import (  # noqa: E402
    ClaudeCodeConfig,
    PersonaClaudeCodeDriver,
    _RealProcessRunner,
)


def test_persona_api_preflight_missing_key_raises_before_request():
    """A02/A15: fehlende Anmeldung muss VOR einem Request sichtbar werden."""
    driver = PersonaApiDriver(PersonaApiConfig(base_url="http://127.0.0.1:1", api_key="", model="x"), "p1")
    try:
        driver.decide({"system": "s", "user": "u"})
        assert False, "haette ProviderAuthError werfen muessen"
    except ProviderAuthError:
        pass
    assert driver.request_count == 0, "kein Request darf ohne Key ausgehen"


def test_persona_api_real_http_boundary_sends_expected_body_and_headers():
    """Prueft die TATSAECHLICH ausgehenden Bytes/Header an einem echten
    Loopback-HTTP-Server (kein Mock der Adapterfunktion selbst)."""
    with FakeHTTPServer([(200, {"choices": [{"message": {"content": "Hallo Persona"}}], "usage": {"prompt_tokens": 5}})]) as srv:
        driver = PersonaApiDriver(
            PersonaApiConfig(base_url=srv.base_url, api_key="test-key-123", model="test-model"), "p1",
        )
        decision = driver.decide({"system": "SYS", "user": "USR"})
        assert decision.text == "Hallo Persona"
        assert driver.request_count == 1
        assert len(srv.calls) == 1
        call = srv.calls[0]
        assert call["method"] == "POST"
        assert call["path"] == "/chat/completions"
        assert call["headers"]["Authorization"] == "Bearer test-key-123"
        body = json.loads(call["body"])
        assert body["model"] == "test-model"
        assert body["messages"][0]["content"] == "SYS"
        assert body["messages"][1]["content"] == "USR"


def test_persona_api_401_maps_to_auth_error_no_fallback():
    """A02: Abo/Key-Fehler fuehrt zu Pause/Fehlerstatus, kein Fallback."""
    with FakeHTTPServer([(401, {"error": "invalid api key"})]) as srv:
        driver = PersonaApiDriver(
            PersonaApiConfig(base_url=srv.base_url, api_key="bad-key", model="test-model"), "p1",
        )
        try:
            driver.decide({"system": "s", "user": "u"})
            assert False, "haette ProviderAuthError werfen muessen"
        except ProviderAuthError:
            pass


def test_persona_api_429_maps_to_quota_error():
    with FakeHTTPServer([(429, {"error": "rate limited"})]) as srv:
        driver = PersonaApiDriver(
            PersonaApiConfig(base_url=srv.base_url, api_key="k", model="m"), "p1",
        )
        try:
            driver.decide({"system": "s", "user": "u"})
            assert False, "haette ProviderQuotaError werfen muessen"
        except ProviderQuotaError:
            pass


def test_claude_code_isolation_check_reads_version_and_help_without_inference():
    """03 §5: --version/--help der real installierten CLI lesen, KEINE
    Inferenz. Fake-CLI zeichnet exakt die argv auf, die tatsaechlich gestartet
    wurden.

    P2-Fertigstellung (I2, alt->neu dokumentiert): 'beliebige erfolgreiche
    --help-Ausgabe' allein belegt keine Isolation mehr (Review-Befund I2/Test
    04). Diese Testfixture konfiguriert jetzt ein ECHTES, in der --help-
    Ausgabe nachweisbares Isolationsflag -- die urspruengliche Fassung ohne
    `extra_isolation_flags` wuerde mit der geschaerften Pruefung bewusst
    `ProviderUnavailableError` werfen (siehe test_m1_adapters.py in
    WORKER-REPORT.md, Abschnitt I2)."""
    with tempfile.TemporaryDirectory() as workdir:
        fake = FakeCLIProcess([
            (0, "claude-code 1.2.3", ""),
            (0, "usage: claude [options] [--strict-mcp-config]", ""),
        ])
        driver = PersonaClaudeCodeDriver(
            ClaudeCodeConfig(binary="claude", isolated_workdir=workdir,
                              extra_isolation_flags=["--strict-mcp-config"]), "p1",
            process_runner=fake,
        )
        info = driver.check_isolation()
        assert "1.2.3" in info["version_output"]
        assert info["verified_isolation_flags"] == ["--strict-mcp-config"]
        assert fake.calls[0].argv == ["claude", "--version"]
        assert fake.calls[1].argv == ["claude", "--help"]


def test_claude_code_isolation_check_rejects_configured_flag_not_found_in_help():
    """I2-Ergaenzung: wird `extra_isolation_flags` konfiguriert, MUSS jedes
    Flag tatsaechlich in der --help-Ausgabe der installierten CLI auftauchen
    -- eine Fehlkonfiguration (Flag existiert nicht) darf nicht still
    ignoriert werden."""
    with tempfile.TemporaryDirectory() as workdir:
        fake = FakeCLIProcess([(0, "claude-code 1.2.3", ""), (0, "usage: claude [options]", "")])
        driver = PersonaClaudeCodeDriver(
            ClaudeCodeConfig(binary="claude", isolated_workdir=workdir,
                              extra_isolation_flags=["--this-flag-does-not-exist"]),
            "p1", process_runner=fake,
        )
        try:
            driver.check_isolation()
            assert False, "haette ProviderUnavailableError werfen muessen (Flag nicht in --help gefunden)"
        except ProviderUnavailableError:
            pass


def test_claude_code_isolation_unverified_without_flags_is_a_hard_block():
    """alt->neu (WEGKARTE §6 A2, PLAN-CRITIC-DURCHSTICH.md BLOCKER): dieser
    Test hiess vorher '..._is_not_a_hard_block' und erwartete einen
    erfolgreichen `check_isolation()` OHNE konfigurierte `extra_isolation_
    flags` (nur WARNING, kein Abbruch). Das widersprach review_p2f_paths.py
    Test 07 ('Fehlende Isolation nur Warnung; leere Billing-Umgebung ist kein
    Rechteentzug' -- MUSS ablehnen) direkt am selben Codepfad. F4 verlangt
    jetzt 'unavailable VOR Inferenz' als harten Default -- diese Fixture ist
    bewusst umgeschrieben (semantisch notwendige Testanpassung, 04 §3): OHNE
    Flags wirft `check_isolation()` `ProviderUnavailableError`, statt eine
    unbelegte Isolation als Erfolg durchzulassen."""
    with tempfile.TemporaryDirectory() as workdir:
        fake = FakeCLIProcess([(0, "claude-code 1.2.3", ""), (0, "irgendein Text ohne Flag-Hinweise", "")])
        driver = PersonaClaudeCodeDriver(
            ClaudeCodeConfig(binary="claude", isolated_workdir=workdir), "p1", process_runner=fake,
        )
        try:
            driver.check_isolation()
            assert False, "haette ProviderUnavailableError werfen muessen (keine extra_isolation_flags konfiguriert)"
        except ProviderUnavailableError:
            pass


def test_claude_code_isolation_unverified_without_flags_logs_warning_before_reject():
    """alt->neu (WEGKARTE §6 A2): der End-Critic-W1-Befund (Isolationsluecke
    darf nicht unsichtbar bleiben) bleibt gueltig, wird jetzt aber durch
    einen HARTEN Abbruch statt nur einer WARNING erfuellt. `check_isolation()`
    MUSS weiterhin eine WARNING loggen (Betriebssichtbarkeit), zusaetzlich zum
    jetzt zwingenden `ProviderUnavailableError`."""
    with tempfile.TemporaryDirectory() as workdir:
        fake = FakeCLIProcess([(0, "claude-code 1.2.3", ""), (0, "keine Flag-Hinweise", "")])
        driver = PersonaClaudeCodeDriver(
            ClaudeCodeConfig(binary="claude", isolated_workdir=workdir), "p1", process_runner=fake,
        )
        logger = logging.getLogger("mmo_sim.adapters.persona_claude_code")
        records: list[logging.LogRecord] = []
        handler = logging.Handler()
        handler.emit = records.append  # type: ignore[method-assign]
        logger.addHandler(handler)
        try:
            try:
                driver.check_isolation()
                assert False, "haette ProviderUnavailableError werfen muessen"
            except ProviderUnavailableError:
                pass
        finally:
            logger.removeHandler(handler)
        warnings = [r for r in records if r.levelno == logging.WARNING]
        assert warnings, "check_isolation() ohne extra_isolation_flags muss eine WARNING loggen (W1), auch beim Abbruch"
        assert "isolation" in warnings[0].getMessage().lower()


def test_claude_code_unavailable_when_isolated_workdir_missing():
    """B1-Nacharbeit: ein konfigurierter, aber nicht existierender
    Arbeitsbereich darf NIE zu 'irgendwo' fuehren — 'unavailable' statt
    unbestaetigter Isolation."""
    fake = FakeCLIProcess([(0, "claude-code 1.2.3", ""), (0, "usage: ...", "")])
    driver = PersonaClaudeCodeDriver(
        ClaudeCodeConfig(binary="claude", isolated_workdir="/tmp/does-not-exist-mmo-sim-test"), "p1",
        process_runner=fake,
    )
    try:
        driver.check_isolation()
        assert False, "haette ProviderUnavailableError werfen muessen (workdir existiert nicht)"
    except ProviderUnavailableError:
        pass


def test_claude_code_unavailable_without_isolated_workdir():
    """03 §5: ohne herstellbare Isolation -> `unavailable`, kein unsicherer
    Betrieb (kein Uebernehmen des Altair-Arbeitsbereichs)."""
    fake = FakeCLIProcess([(0, "claude-code 1.2.3", ""), (0, "usage: ...", "")])
    driver = PersonaClaudeCodeDriver(
        ClaudeCodeConfig(binary="claude", isolated_workdir=None), "p1", process_runner=fake,
    )
    try:
        driver.check_isolation()
        assert False, "haette ProviderUnavailableError werfen muessen (kein Arbeitsbereich)"
    except ProviderUnavailableError:
        pass


def test_claude_code_missing_binary_is_unavailable_not_crash():
    with tempfile.TemporaryDirectory() as workdir:
        fake = FakeCLIProcess([(127, "", "command not found")])
        driver = PersonaClaudeCodeDriver(
            ClaudeCodeConfig(binary="nonexistent-cli", isolated_workdir=workdir), "p1", process_runner=fake,
        )
        try:
            driver.check_isolation()
            assert False, "haette ProviderUnavailableError werfen muessen"
        except ProviderUnavailableError:
            pass


def test_claude_code_decide_sends_stdin_no_shell_injection():
    """Kein aus Spielertext gebauter Shellbefehl: argv ist eine feste Liste,
    Nutzertext geht ausschliesslich ueber stdin. B1/B2-Nacharbeit: `cwd` muss
    der isolierte Arbeitsbereich sein, `env` muss die geerbte Umgebung
    (PATH/HOME) enthalten statt sie zu ersetzen.

    P2-Fertigstellung (I2, alt->neu dokumentiert): `extra_isolation_flags`
    jetzt Pflicht fuer eine belegte Isolation (s.
    test_claude_code_isolation_check_reads_version_and_help_without_inference);
    Umgebung wird zusaetzlich um die Billing-Risk-Vars bereinigt, damit dieser
    Test unabhaengig vom Host-Environment deterministisch bleibt (A3)."""
    with tempfile.TemporaryDirectory() as workdir:
        fake = FakeCLIProcess([
            (0, "claude-code 1.2.3", ""), (0, "usage: ... [--strict-mcp-config]", ""),
            (0, json.dumps({"type": "result", "subtype": "success", "is_error": False,
                             "result": "Persona-Antwort hier", "usage": {}}), ""),
        ])
        driver = PersonaClaudeCodeDriver(
            ClaudeCodeConfig(binary="claude", isolated_workdir=workdir,
                              extra_isolation_flags=["--strict-mcp-config"]), "p1", process_runner=fake,
        )
        dangerous_text = "; rm -rf / #"
        env_clean = {k: v for k, v in os.environ.items() if k not in
                     ("ANTHROPIC_API_KEY", "OPENROUTER_API_KEY", "CLAUDE_API_KEY")}
        with patch.dict(os.environ, env_clean, clear=True):
            decision = driver.decide({"user": dangerous_text})
        assert decision.text == "Persona-Antwort hier"
        call = fake.calls[-1]
        assert dangerous_text not in call.argv, "Spielertext darf NIE in argv landen (Shell-Injektionsschutz)"
        assert call.stdin == dangerous_text
        assert call.cwd == workdir, "B1: Prozess muss im isolierten Arbeitsbereich laufen, nicht irgendwo"
        assert call.env.get("CLAUDE_WORKDIR") == workdir
        assert "PATH" in call.env, "B2: geerbte Umgebung (PATH) darf nicht ersetzt werden"


def test_claude_code_real_process_runner_actually_uses_cwd_and_inherited_env():
    """B1/B2, gegen den ECHTEN `_RealProcessRunner` (nicht die Fake-Variante):
    ein echter Kurzprozess muss tatsaechlich im isolierten Arbeitsverzeichnis
    laufen und PATH/HOME in seiner Umgebung vorfinden. Das ist genau der Pfad,
    den `FakeCLIProcess` bisher nie beruehrt hat (End-Critic B1/B2)."""
    with tempfile.TemporaryDirectory() as workdir:
        runner = _RealProcessRunner()
        env = {**os.environ, "CLAUDE_WORKDIR": workdir}
        rc, out, err = runner.run(
            [sys.executable, "-c", "import os; print(os.getcwd()); print(os.environ.get('PATH', ''))"],
            env=env,
            cwd=workdir,
        )
        assert rc == 0, f"echter Subprozess ist fehlgeschlagen: {err}"
        lines = out.splitlines()
        assert lines[0] == os.path.realpath(workdir), "cwd wurde NICHT an den echten Subprozess weitergereicht (B1)"
        assert lines[1] != "", "PATH fehlt im Kindprozess — env wurde ersetzt statt ergaenzt (B2)"


def main() -> int:
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
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
