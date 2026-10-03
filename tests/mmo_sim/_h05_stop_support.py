"""H05 test-local barriers. No product imports or real provider calls.

An input is recorded when received. Output intent, successful write and durable
product reception are separate facts. Timeout/cancellation never releases a
scripted success. All journals belong to the current synthetic test directory.
"""
from __future__ import annotations
import base64
import hashlib
import json
import os
import stat
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


def make_stalling_handler(pre_block_bodies: list[dict], block_response_body: dict, *,
                          validators=None, wait_timeout=30.0, label="h05-stall", journal_path=None):
    block_event, release_event, cancel_event = threading.Event(), threading.Event(), threading.Event()
    receipts, validation_failures = [], []
    pre_block_bodies = list(pre_block_bodies)
    validators = validators or {}

    def journal(record, event):
        if journal_path is not None:
            with Path(journal_path).open("a", encoding="utf-8") as fh:
                fh.write(json.dumps({"event": event, **record}, ensure_ascii=False) + "\n")

    class Handler(BaseHTTPRequestHandler):
        _h05_cancel_event = cancel_event

        def log_message(self, *args):
            pass

        def _send(self, status, body, record):
            payload = json.dumps(body).encode("utf-8")
            record.update(egress_intended_status=status, egress_intended_body=body,
                          egress_intended_b64=base64.b64encode(payload).decode("ascii"),
                          egress_state="attempting", egress_attempt_wall_ts=time.time())
            journal(record, "write_attempt")
            try:
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                self.wfile.flush()
            except OSError as exc:
                record.update(egress_state="write_error", egress_error=repr(exc), egress_error_wall_ts=time.time())
                journal(record, "write_error")
                return
            record.update(egress_state="written", egress_status=status, egress_body=body,
                          egress_raw_b64=base64.b64encode(payload).decode("ascii"),
                          egress_sha256=hashlib.sha256(payload).hexdigest(),
                          egress_sent_monotonic=time.monotonic(), egress_sent_wall_ts=time.time())
            journal(record, "write_completed")

        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0) or 0)
            raw = self.rfile.read(length) if length else b""
            try:
                body = json.loads(raw) if raw else {}
            except (UnicodeDecodeError, json.JSONDecodeError):
                body = {"_raw_undecoded_base64": base64.b64encode(raw).decode("ascii")}
            idx = len(receipts)
            record = {"seq": idx, "label": label, "path": self.path, "content_length": length,
                      "body_sha256": hashlib.sha256(raw).hexdigest(), "body": body,
                      "body_raw_b64": base64.b64encode(raw).decode("ascii"),
                      "received_monotonic": time.monotonic(), "received_wall_ts": time.time(),
                      "egress_status": None, "egress_body": None, "egress_sha256": None,
                      "egress_sent_monotonic": None, "egress_state": "not_attempted"}
            receipts.append(record)
            journal(record, "input_received")
            validator = validators.get(idx)
            error = validator(body) if validator else None
            if error is not None:
                validation_failures.append({"seq": idx, "error": error})
                self._send(599, {"error": "H05_INPUT_VALIDATION_FAILED: " + error}, record)
                return
            if idx < len(pre_block_bodies):
                self._send(200, pre_block_bodies[idx], record)
                return
            if idx > len(pre_block_bodies):
                self._send(599, {"error": "H05_UNEXPECTED_FOLLOWUP_CALL_AFTER_STOP"}, record)
                return
            block_event.set()
            deadline = time.monotonic() + wait_timeout
            while not release_event.is_set() and not cancel_event.is_set():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    record["barrier_outcome"] = "timeout_without_release"
                    self._send(504, {"error": "H05_BARRIER_NOT_RELEASED"}, record)
                    return
                release_event.wait(min(0.02, remaining))
            if cancel_event.is_set() and not release_event.is_set():
                record.update(barrier_outcome="cancelled_without_release", egress_state="cancelled_no_send",
                              cancelled_wall_ts=time.time())
                journal(record, "cancelled_no_send")
                return
            record.update(barrier_outcome="explicitly_released", release_observed_wall_ts=time.time())
            self._send(200, block_response_body, record)

    return Handler, block_event, release_event, receipts, validation_failures


def start_http_server(handler_cls):
    srv = HTTPServer(("127.0.0.1", 0), handler_cls)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    return srv, thread, f"http://{srv.server_address[0]}:{srv.server_address[1]}"


def stop_http_server(srv, thread):
    # Test teardown cancels a pending fixture, never turns it into a successful response.
    event = getattr(srv.RequestHandlerClass, "_h05_cancel_event", None)
    if event is not None:
        event.set()
    srv.shutdown()
    srv.server_close()
    thread.join(timeout=5)
    if thread.is_alive():
        raise RuntimeError("H05 owned HTTP receiver did not terminate")


_STALLING_FAKE_CLI_TEMPLATE = r'''__SHEBANG__
import base64, hashlib, json, os, signal, sys, time
from pathlib import Path
cfg = __CONFIG__
received = time.time()
consumed = 0
release_observed = None

def emit(rc, stdout_text, stderr_text, state="completed", kind="decision"):
    out = stdout_text.encode("utf-8")
    err = stderr_text.encode("utf-8")
    record = {"argv":sys.argv[1:], "cwd":os.getcwd(), "pid":os.getpid(), "consumed_index":consumed,
              "received_wall_ts":received, "release_observed_wall_ts":release_observed,
              "event_kind":kind, "rc":rc, "outcome":state,
              "egress_stdout_intended_b64":base64.b64encode(out).decode(),
              "egress_stderr_intended_b64":base64.b64encode(err).decode()}
    try:
        sys.stdout.buffer.write(out); sys.stdout.buffer.flush()
        sys.stderr.buffer.write(err); sys.stderr.buffer.flush()
    except OSError as exc:
        record.update(write_state="write_error", write_error=repr(exc), egress_status="write_failed", rc=74)
        rc=74
        # Prevent another implicit buffered flush from masking the recorded failure.
        try:
            fd=os.open(os.devnull,os.O_WRONLY); os.dup2(fd,sys.stdout.fileno()); os.dup2(fd,sys.stderr.fileno()); os.close(fd)
        except OSError:
            pass
    else:
        record.update(write_state="written", egress_status="exit_0_success" if rc==0 else "exit_nonzero",
                      egress_stdout_b64=base64.b64encode(out).decode(), egress_stderr_b64=base64.b64encode(err).decode(),
                      egress_stdout_sha256=hashlib.sha256(out).hexdigest(), egress_stderr_sha256=hashlib.sha256(err).hexdigest(),
                      egress_stdout_bytes_len=len(out), egress_stderr_bytes_len=len(err))
    record["egress_sent_wall_ts"]=time.time()
    dest=cfg["egress_path"] if kind=="decision" else cfg["egress_path"]+".help-version.jsonl"
    with open(dest,"a",encoding="utf-8") as f: f.write(json.dumps(record,ensure_ascii=False)+"\n")
    raise SystemExit(rc)

if "--help" in sys.argv or "--version" in sys.argv:
    text=("Usage: fake-claude [options]\n  --permission-mode <mode> restrict tools\n  --safe-mode skip hooks\n"
          if "--help" in sys.argv else "fake-claude 0.0.0-h05-stop-test\n")
    emit(0,text,"",kind="help" if "--help" in sys.argv else "version")

def terminate(sig,frame):
    emit(128+sig,"",f"H05 controlled fake CLI terminated by signal {sig}\n",state="terminated_before_success")
signal.signal(signal.SIGTERM,terminate)
raw=sys.stdin.buffer.read()
stdin_text=raw.decode("utf-8")
with open(cfg["capture_path"],"a",encoding="utf-8") as f:
    f.write(json.dumps({"argv":sys.argv[1:],"stdin":stdin_text,"stdin_raw_b64":base64.b64encode(raw).decode(),
                       "stdin_sha256":hashlib.sha256(raw).hexdigest(),"cwd":os.getcwd(),"pid":os.getpid(),
                       "received_wall_ts":received},ensure_ascii=False)+"\n")
queue=json.loads(Path(cfg["queue_path"]).read_text())
if not queue: emit(2,"","H05 unexpected additional fake CLI request\n",state="queue_exhausted")
if Path(cfg["consumed_path"]).exists(): consumed=int(Path(cfg["consumed_path"]).read_text())
item=queue[0]
missing=[s for s in (item.get("expect_all") or []) if s not in stdin_text]
phase=item.get("expect_phase_marker")
if phase and phase not in stdin_text: missing.append("phase: "+phase)
length=item.get("expect_sl_log_len")
if length is not None:
    try:
        marker="[OEFFENTLICHE_TISCHSICHT]\n"
        offset=stdin_text.rfind(marker)
        if offset<0: raise ValueError("missing public table view")
        view=json.loads(stdin_text[offset+len(marker):])
        if view.get("table_id") != item["expect_table_id"]: raise ValueError("wrong table_id")
        log=view.get("sl_log") or []
        if len(log)!=length: raise ValueError("wrong sl_log length")
        journal=Path(item["expect_gm_journal"])
        rows=[json.loads(l) for l in journal.read_text().splitlines()] if journal.exists() else []
        sent=[r for r in rows if r.get("send_ok") is True]
        expected=[r["response_body"]["choices"][0]["message"]["content"] for r in sent]
        if len(expected)!=length or [r["content"] for r in log]!=expected:
            raise ValueError("public GM prefix differs from actual successful GM outputs")
    except (ValueError, KeyError, TypeError, OSError) as exc:
        missing.append(str(exc))
if missing: emit(9,"","H05_INPUT_VALIDATION_FAILED: "+repr(missing)+"\n",state="invalid_input")
if consumed==cfg["block_at_index"]:
    Path(cfg["block_marker_path"]).write_text(json.dumps({"pid":os.getpid(),"argv":sys.argv[1:],"received_wall_ts":time.time()}))
    deadline=time.monotonic()+cfg["wait_timeout"]
    while not Path(cfg["release_marker_path"]).exists():
        if time.monotonic()>=deadline:
            emit(3,"","H05_BARRIER_NOT_RELEASED\n",state="timeout_without_release")
        time.sleep(.02)
    release_observed=time.time()
queue.pop(0)
Path(cfg["queue_path"]).write_text(json.dumps(queue))
Path(cfg["consumed_path"]).write_text(str(consumed+1))
response=json.dumps({"type":"result","subtype":"success","is_error":False,"result":item.get("result",""),"usage":{}})+"\n"
emit(0,response,"")
'''


def write_stalling_fake_cli(root: Path, *, capture_path: Path, queue: list[dict], block_at_index: int,
                            wait_timeout: float = 30.0):
    queue_path = root / f"fake_cli_queue_{capture_path.stem}.json"
    consumed = root / f"fake_cli_consumed_{capture_path.stem}.txt"
    block = root / f"fake_cli_block_{capture_path.stem}.json"
    release = root / f"fake_cli_release_{capture_path.stem}.json"
    egress = root / f"fake_cli_egress_{capture_path.stem}.jsonl"
    path = root / f"fake_claude_{capture_path.stem}.py"
    for p in (queue_path, consumed, block, release, egress, path):
        if p.exists():
            raise FileExistsError(f"H05 fake CLI case collision: {p}")
    queue_path.write_text(json.dumps(queue), encoding="utf-8")
    cfg = {"capture_path":str(capture_path), "queue_path":str(queue_path), "consumed_path":str(consumed),
           "block_marker_path":str(block), "release_marker_path":str(release), "egress_path":str(egress),
           "block_at_index":block_at_index, "wait_timeout":wait_timeout}
    path.write_text(_STALLING_FAKE_CLI_TEMPLATE.replace("__SHEBANG__",f"#!{sys.executable}").replace("__CONFIG__",repr(cfg)),encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return path, block, release, egress


def wait_for_marker(path: Path, timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.exists():
            return True
        time.sleep(.02)
    return path.exists()


def release_marker(path: Path) -> None:
    path.write_text(json.dumps({"released_wall_ts":time.time()}), encoding="utf-8")
