#!/usr/bin/env python3
"""
tests/mmo_sim/test_r3_community_choices_real_subprocess.py — dauerhafte
Regressionstests fuer R3 (Community-Recovery 2026-09-25,
REVIEW-COMMUNITY-RECOVERY.md §5, `ui/tui.py:_cmd_community`). Adaptiert aus
der einmaligen Review-Probe `tests-review/review_community_choices.py`
(Ausgangsbefund dort: 2 PASS / 2 FAIL / 0 ERROR) in einen dauerhaften
In-Repo-Test -- exakt dieselben Faelle/Assertions, repo-uebliche `main()`/
Exitcode-Form statt `--output-dir`-Dump.

Echte, EIGENSTAENDIGE `scripts/mmo_sim.py`-Subprozesse (kein In-Prozess-
`TuiSession`-Aufruf) gegen zwei echte private Loopback-HTTP-Server (GM +
Persona, openai-/OWUI-kompatibel) -- derselbe Aufbau wie
`test_p2_community_creation_real_subprocess.py`.

Test 01: explizite produktive Neuanlage (`p`) + begrenztes, im neuen
Prozess fortsetzbares Limit -- bereits bestehende Regression (04_ABNAHME
'Pflichtpositive'), hier als eigener Beleg gegen den ECHTEN CLI-Weg.
Test 02: eine bestehende, ohne Live-Anbindung entstandene Demo-Gemeinschaft
darf bei jetzt konfigurierter Live-Anbindung NICHT ohne eine gesonderte
Uebernahmeentscheidung in echte Modellerschaffung uebergehen. Die
Vorbedingung "Bestandsgemeinschaft ohne Adoptionsmarker" wird ueber einen
direkten `bootstrap_community()`-Seed hergestellt (nicht ueber
`configured=False` am CLI-Entrypoint): End-Critic-Befund 2026-09-25 §5b
zeigte, dass `scripts/mmo_sim.py` die echten `gm_transport_factory`/
`persona_driver_factory`-Closures IMMER (auch ohne Env-Konfiguration)
uebergibt -- sie werfen erst lazy beim tatsächlichen Aufruf, wodurch
`_cmd_community`s `live_configured` ueber die reale CLI unabhaengig von der
Env-Konfiguration immer wahr ist. Der urspruengliche `configured=False`-Aufbau
erreichte den beabsichtigten "Fortsetzen einer noch nicht bewusst
uebernommenen Bestandsgemeinschaft"-Codepfad deshalb nie (bestand aus einem
anderen Grund: zweimal derselbe "neue Community, ungueltige Eingabe"-Fall).
Test 03: `x` an der echten `[d/p]`-Rueckfrage ist KEINE Zustimmung (kein
Modellaufruf).
Test 04: `MMO_SIM_COMMUNITY_STEP_LIMIT=abc` bleibt abgelehnt, requestfrei."""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import threading
import traceback
from collections import Counter
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss.community_bootstrap import bootstrap_community  # noqa: E402

SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
ANSWER = "SYNTHETIC CHOICE: Mein Chrononaut hat leichte Ruestung."


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *_a):
        return

    def do_POST(self):
        length = int(self.headers["Content-Length"])
        body = json.loads(self.rfile.read(length))
        server = self.server
        kind = "gm" if "chat_id" in body else "persona"
        server.calls.append({"kind": kind, "body": body})
        if kind == "persona":
            text = ANSWER
        else:
            ident = server.ids.setdefault(body["chat_id"], len(server.ids) + 1)
            last = body["messages"][-1]["content"]
            if last == ANSWER:
                save = {"v": 7, "save_id": f"SYNTHETIC-CHOICE-{ident}",
                        "characters": [{"char_id": f"SYNTHETIC-CHOICE-CHR-{ident}", "name": "Synthetic",
                                        "callsign": str(ident), "level": 1}]}
                text = "```json\n" + json.dumps(save) + "\n```"
            else:
                text = "SYNTHETIC QUESTION: Welche Grundausstattung?"
        raw = json.dumps({"choices": [{"message": {"content": text}}],
                           "usage": {"prompt_tokens": 5, "completion_tokens": 5}, "sources": []}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


@contextmanager
def _serving():
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    server.calls = []
    server.ids = {}
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        t.join()


def _call(b: Path, s, stdin_text: str, configured: bool = True, limit: str = "1") -> dict:
    env = dict(os.environ)
    for k in list(env):
        if k.startswith(("OPENWEBUI_", "MMO_SIM_", "ANTHROPIC_", "OPENAI_", "OPENROUTER_")):
            env.pop(k, None)
    if configured:
        url = f"http://127.0.0.1:{s.server_port}"
        env.update({
            "OPENWEBUI_URL": url, "OPENWEBUI_API_KEY": "SYNTHETIC_KEY",
            "MMO_SIM_PERSONA_API_BASE_URL": url, "MMO_SIM_PERSONA_API_KEY": "SYNTHETIC_KEY",
            "MMO_SIM_PERSONA_API_MODEL": "synthetic", "MMO_SIM_GM_OUTPUT_LIMIT_TOKENS": "50",
            "MMO_SIM_COMMUNITY_STEP_LIMIT": limit,
        })
    n = len(s.calls)
    proc = subprocess.Popen(
        [sys.executable, str(_REPO_ROOT / "scripts" / "mmo_sim.py"), "--participant", "synthetic_choice_caller",
         "--data-dir", str(b)],
        cwd=b, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    out, err = proc.communicate(stdin_text, timeout=40)
    plan = b / "run/community/bootstrap__plan.json"
    data = json.loads(plan.read_text(encoding="utf-8")) if plan.exists() else None
    return {
        "pid": proc.pid, "exit": proc.returncode, "stdin": stdin_text, "stdout": out, "stderr": err,
        "calls": s.calls[n:], "counts": dict(Counter(x["kind"] for x in s.calls[n:])), "plan": data,
        "plan_sha256": hashlib.sha256(plan.read_bytes()).hexdigest() if plan.exists() else None,
        "current_files": sorted(x.name for x in (b / "run/current_saves").glob("*.json")),
    }


def test_01_explicit_production_and_limited_resume():
    with tempfile.TemporaryDirectory() as td, _serving() as s:
        b = Path(td)
        write_test_profile(b / "run", max_turns=100)
        x = _call(b, s, "c\np\nx\n")
        y = _call(b, s, "c\nx\n")
        assert x["exit"] == y["exit"] == 0, (x, y)
        assert x["counts"] == {"gm": 2, "persona": 1}, x
        assert y["counts"] == {"gm": 2, "persona": 1}, y
        assert x["plan_sha256"] == y["plan_sha256"], "gepinnter Plan darf sich beim Fortsetzen nicht aendern"


def test_02_existing_demo_requires_adoption_choice():
    with tempfile.TemporaryDirectory() as td, _serving() as s:
        b = Path(td)
        community_id = "community-synthetic_choice_caller"
        draft = {
            "real_name": "Legacy Demo", "archetype": "LEGACY_ARCH", "play_style": "LEGACY_STYLE",
            "charwunsch": "LEGACY_WISH",
            "plays_char": {
                "save_file": "NOCH_NICHT_ERSCHAFFEN", "character_id": "NOCH_NICHT_ERSCHAFFEN",
                "name": "NOCH_NICHT_ERSCHAFFEN", "callsign": "NOCH_NICHT_ERSCHAFFEN",
            },
        }
        ps_store = PersonaStateStore(schema_path=SCHEMA)
        today = datetime.date.today().isoformat()
        # Vorbedingung "Bestandsgemeinschaft ohne Adoptionsmarker" real
        # herstellen -- direkter bootstrap_community()-Seed statt
        # `configured=False` am CLI-Entrypoint (s. Moduldocstring).
        bootstrap_community(
            b / "run/community", community_id, 1, {"legacy_persona": draft}, ps_store, b / "states", today,
        )
        write_test_profile(b / "run", max_turns=100)
        y = _call(b, s, "c\nx\nx\n")
        assert not y["calls"], (
            f"eine bestehende Demo-Gemeinschaft darf ohne gesonderte Uebernahmeentscheidung nicht "
            f"sofort in echte Modellerschaffung uebergehen: {y}"
        )
        assert "Fortsetzen der noch nicht bewusst uebernommenen Bestandsgemeinschaft" in y["stdout"], (
            f"der Test muss tatsaechlich den 'Fortsetzen einer Bestandsgemeinschaft'-Codepfad erreichen, "
            f"nicht nur zufaellig 0 Modellanfragen zeigen: {y}"
        )


def test_03_invalid_choice_is_not_consent():
    with tempfile.TemporaryDirectory() as td, _serving() as s:
        b = Path(td)
        write_test_profile(b / "run", max_turns=100)
        x = _call(b, s, "c\nx\nx\n")
        assert not x["calls"], (
            f"ein ungueltiges `x` an der [d/p]-Rueckfrage darf nicht als bewusstes `d` umgedeutet "
            f"werden und keine Modellanfrage ausloesen: {x}"
        )


def test_04_invalid_limit_sends_nothing():
    with tempfile.TemporaryDirectory() as td, _serving() as s:
        b = Path(td)
        write_test_profile(b / "run", max_turns=100)
        x = _call(b, s, "c\np\nx\n", limit="abc")
        assert not x["calls"], x
        assert "abgelehnt" in x["stdout"].lower(), x["stdout"]


def main() -> int:
    tests = [
        test_01_explicit_production_and_limited_resume, test_02_existing_demo_requires_adoption_choice,
        test_03_invalid_choice_is_not_consent, test_04_invalid_limit_sends_nothing,
    ]
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
