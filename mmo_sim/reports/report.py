#!/usr/bin/env python3
"""
mmo_sim/reports/report.py — lokale Event-Reports + Issue-ENTWUERFE (M4,
02 §9, 03 §7, A13).

"Berichte ohne zusaetzliche Modellkosten grundsaetzlich lokal aus Events
generieren." Liest NUR `core/events.py`-Events — kein Modellcall in diesem
Adapter. Eine optionale modellgestuetzte Nachauswertung waere ein SEPARATER
Adapter mit eigenem Budget (nicht in diesem Bauauftrag umgesetzt, s.
WORKER-REPORT.md OFFEN-Liste)."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Report:
    total_events: int
    sl_turns: int
    sections_completed: int
    sections_rejected: int
    provider_errors: int
    rejection_reasons: list[str] = field(default_factory=list)


@dataclass
class IssueDraft:
    title: str
    body: str
    evidence_event_ids: list[str] = field(default_factory=list)


def generate_report(events: list[dict]) -> Report:
    """Rein lokal, deterministisch, keine Modellbewertung. `events` kommt
    aus `EventLog.read_all()`."""
    sl_turns = sum(1 for e in events if e["event_type"] == "sl_turn")
    completed = sum(1 for e in events if e["event_type"] == "section_completed")
    rejected_events = [e for e in events if e["event_type"] == "section_completion_rejected"]
    provider_errors = sum(1 for e in events if e["event_type"] in ("provider_error", "provider_auth_missing"))
    return Report(
        total_events=len(events), sl_turns=sl_turns, sections_completed=completed,
        sections_rejected=len(rejected_events), provider_errors=provider_errors,
        rejection_reasons=[e["payload"].get("reason", "") for e in rejected_events],
    )


@dataclass
class ProvenanceExcerpt:
    """A13 (WEGKARTE §8, 02 §9, 01 §M4): EIN unveraenderter Rohbeleg -- ein
    Ausschnitt aus einem tatsaechlichen `sl_turn`-Event-Text, der eine
    technische KEYWORD-Kategorie beruehrt (Ausruestung/Boss/Kampf/Drift/
    zaehe Passage). Dies ist eine simple lokale Textsuche, KEINE
    Modellbewertung ('Modellbewertungen als Modellbewertungen kennzeichnen',
    02 §9) -- ein positives/negatives Spielgefuehl wird hier NICHT
    behauptet, nur eine auffindbare Erwaehnung mit exakter Fundstelle."""

    category: str  # "ausruestung" | "boss" | "kampf" | "drift"
    event_id: str
    table_id: str | None
    section_id: str | None
    turn_idx: int | None
    persona_key: str | None
    excerpt: str  # unveraendertes Textfragment (max. 240 Zeichen um den Treffer)
    # A13 (02_AUFTRAG_A13.md §2, 2026-09-30): optionale, ausschliesslich
    # nachtraeglich vom A13-CLI-Pfad gesetzte Quellreferenz -- die
    # unveraenderte `extract_provenance_excerpts()` selbst liefert diese
    # Felder NIE (bleiben `None`, kompatible Erweiterung, kein API-Bruch).
    source_path: str | None = None
    source_sha256: str | None = None
    pointer: str | None = None
    char_offset_start: int | None = None
    char_offset_end: int | None = None
    excerpt_sha256: str | None = None


# A13: rein technische, deutschsprachige Stichwortkategorien -- keine
# Spassbewertung, nur eine auffindbare Erwaehnung. Bewusst schmal gehalten
# (kein Anspruch auf vollstaendige Erkennung); erweiterbar ohne API-Bruch.
_PROVENANCE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "ausruestung": ("ausrüstung", "ausruestung", "waffe", "rüstung", "ruestung", "gadget", "item"),
    "boss": ("boss", "endgegner", "anführer", "anfuehrer"),
    "kampf": ("kampf", "gefecht", "feuergefecht", "schuss", "schüsse", "schuesse", "verwundet"),
    "drift": ("wiederholt sich", "nichts passiert", "steht bereit und beobachtet", "erneut dasselbe"),
}


def extract_provenance_excerpts(events: list[dict], window: int = 120) -> list[ProvenanceExcerpt]:
    """Durchsucht NUR `sl_turn`-Event-Texte (bereits im Eventlog vorhanden,
    `core/runtime.py:submit` schreibt den unveraenderten SL-Antworttext
    mit) nach den obigen Kategorien. Liefert je Treffer GENAU EIN
    Textfragment um die Fundstelle (unveraendert, kein Modellurteil)."""
    out: list[ProvenanceExcerpt] = []
    for e in events:
        if e.get("event_type") != "sl_turn":
            continue
        payload = e.get("payload") or {}
        text = payload.get("content") or ""
        if not text:
            continue
        lowered = text.lower()
        for category, keywords in _PROVENANCE_KEYWORDS.items():
            for kw in keywords:
                idx = lowered.find(kw)
                if idx < 0:
                    continue
                start = max(0, idx - window // 2)
                end = min(len(text), idx + len(kw) + window // 2)
                out.append(ProvenanceExcerpt(
                    category=category, event_id=e.get("event_id", ""),
                    table_id=payload.get("table_id"), section_id=payload.get("section_id"),
                    turn_idx=payload.get("turn_idx"), persona_key=payload.get("origin_persona_key"),
                    excerpt=text[start:end],
                ))
                break  # ein Treffer pro Kategorie/Turn genuegt als Beleg.
    return out


def draft_issues(report: Report, events: list[dict]) -> list[IssueDraft]:
    """Erzeugt Issue-ENTWUERFE mit Belegstellen (Event-IDs) — KEINE
    automatischen GitHub-Issues, keine Aenderung am Spielkern (02 §9)."""
    drafts: list[IssueDraft] = []
    if report.provider_errors > 0:
        error_events = [e for e in events if e["event_type"] in ("provider_error", "provider_auth_missing")]
        drafts.append(IssueDraft(
            title=f"{report.provider_errors} Provider-Fehler im Lauf",
            body="Provider-/Auth-Fehler traten waehrend des Laufs auf — pruefen, ob Pause statt Fallback korrekt griff.",
            evidence_event_ids=[e["event_id"] for e in error_events],
        ))
    if report.sections_rejected > 0:
        rejected = [e for e in events if e["event_type"] == "section_completion_rejected"]
        drafts.append(IssueDraft(
            title=f"{report.sections_rejected} abgelehnte Abschnittsabschluesse",
            body="Abschnitte wurden nicht abgeschlossen (fehlender Marker/ungueltige Ernte) — Gruende: "
                 + "; ".join(report.rejection_reasons[:5]),
            evidence_event_ids=[e["event_id"] for e in rejected],
        ))
    return drafts


# ============================================================================
# A13 (02 §9, 04/A13, 03 §7, 2026-09-30; R1-R3-Nacharbeit 2026-09-30) —
# lokaler Operator-Quellenbericht fuer GENAU einen gewaehlten Tisch+
# Abschnitt, ueber `python scripts/mmo_sim.py report --data-dir ... --table
# ... --section ... --output-dir ...`. Rein lesend, KEIN Modellcall, KEIN
# neuer Event-/Buchungs-/Publikationsschreiber. In echten A23-Ablagen fehlt
# `events.jsonl` -- diese Erweiterung liest deshalb `table.sl_log` (bereits
# vorhandene oeffentliche Tischquelle) statt eines erfundenen `sl_turn`-
# Events. Alles oben (Report/IssueDraft/generate_report/ProvenanceExcerpt/
# extract_provenance_excerpts/draft_issues) bleibt UNVERAENDERT und wird hier
# nur aufgerufen/wiederverwendet -- keine zweite Stichwort-/Reportlogik.
#
# R1-R3-Nacharbeit (02_AUFTRAG_REST_A13.md, 2026-09-30): widerspruechliche
# Bindungen (Savehash/Guard-Persona/Final-Section) sind jetzt ein Hold
# (`A13SourceError`) statt eines stillen `COMPLETE`; die historische
# VORversion wird tatsaechlich aus `expected_prev_ref` (Plan) + `run_id`
# geladen (kein Fallback auf aktuellen Current); jeder Quellenread ist
# einheitlich root-gebunden (`_resolve_within_root`, auch Elternlinks);
# gelesene Quellen werden vor der Ausgabe erneut gehasht (Snapshot-Hold bei
# Aenderung); Request-Routen werden bereinigt (`_sanitize_route`); Feedback
# ist `private:true` mit auflösbarer Zeile/Offset/Hash; fehlende GM-Modell-/
# Prompt-/Regelmetadaten fuehren zu PARTIAL statt pauschal COMPLETE.
# ============================================================================

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit, urlunsplit

_ID_RE_A13 = re.compile(r"^[A-Za-z0-9_-]+\Z")


class A13SourceError(ValueError):
    """Ein A13-Quellproblem (unsicherer Pfad, unlesbare Pflichtquelle,
    widerspruechliche Bindung) -- fuehrt IMMER zu einem kontrollierten
    Fehler/Hold, nie zu einem stillen Vollbericht."""


def _sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _require_safe_id(value: str, label: str) -> str:
    """Nur `--table`/`--section`-Werte, die als Dateinamensbestandteil
    sicher sind (kein Traversal, kein Fremdpfad) -- vor jedem Dateizugriff."""
    if not value or not _ID_RE_A13.match(value):
        raise A13SourceError(
            f"{label} {value!r} enthaelt unzulaessige Zeichen (erlaubt: "
            f"[A-Za-z0-9_-]) -- kein Dateizugriff versucht."
        )
    return value


def _resolve_within_root(data_root: Path, rel: str) -> Path:
    """Loest `rel` (aus CLI-Argumenten oder -- nach Pruefung durch den
    Aufrufer -- aus bereits gelesenem JSON-Inhalt wie einer Guard-Datei)
    STRIKT innerhalb `data_root` auf. Lehnt absolute Pfade, `..`-Traversal
    und (ueber den aufgeloesten Realpfad) Symlink-Fluchten aus dem
    Datenroot ab -- 'Keine Pfade aus Modell-/Save-Text ausfuehren oder
    ausserhalb des Datenroots dereferenzieren' (02_AUFTRAG_A13.md §1)."""
    if not isinstance(rel, str) or not rel:
        raise A13SourceError(f"leerer/ungueltiger Quellenpfad: {rel!r}")
    pure = PurePosixPath(rel.replace("\\", "/"))
    if pure.is_absolute() or ".." in pure.parts:
        raise A13SourceError(f"unsicherer Quellenpfad (absolut/Traversal): {rel!r}")
    root_resolved = data_root.resolve()
    candidate = (data_root / rel)
    resolved = candidate.resolve()
    if resolved != root_resolved and root_resolved not in resolved.parents:
        raise A13SourceError(f"Quellenpfad verlaesst das Datenroot: {rel!r}")
    return candidate


def _read_json_source(path: Path) -> tuple["dict | list | None", "str | None", "str | None"]:
    """STRIKT lesender Parser: liefert (Inhalt, SHA256-der-Rohbytes, Fehlertext).
    Erzeugt NIE ein Verzeichnis/eine Datei (anders als `EventLog.__init__`/
    `_requests_dir`, s. A13_SOURCE_MAP.json) und ueberspringt NIE still einen
    Parsefehler -- ein Fehler wird als Text zurueckgegeben, nicht verschluckt."""
    try:
        if path.is_symlink():
            return None, None, "abgelehnt: Symlink als Quelle"
        if not path.is_file():
            return None, None, "fehlt"
    except OSError as exc:
        return None, None, f"Lesefehler: {exc!r}"
    try:
        raw = path.read_bytes()
    except OSError as exc:
        return None, None, f"Lesefehler: {exc!r}"
    sha = _sha256_bytes(raw)
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, sha, f"Parsefehler: {exc!r}"
    return data, sha, None


def _read_jsonl_source(path: Path) -> tuple[list[dict], int, "str | None"]:
    """Wie `_read_json_source`, aber JSONL: liefert (gueltige Zeilen,
    Anzahl uebersprungener kaputter Zeilen, Fehlertext falls Datei fehlt/
    unlesbar). Kaputte EINZELNE Zeilen werden gezaehlt statt (wie
    `EventLog.read_all`) still verschluckt -- die Zaehlung fliesst in
    PARTIAL-Gruende ein."""
    try:
        if path.is_symlink():
            return [], 0, "abgelehnt: Symlink als Quelle"
        if not path.is_file():
            return [], 0, None  # optionale Quelle: Abwesenheit ist kein Fehler
    except OSError as exc:
        return [], 0, f"Lesefehler: {exc!r}"
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [], 0, f"Lesefehler: {exc!r}"
    except UnicodeDecodeError as exc:
        return [], 0, f"Lesefehler: {exc!r}"
    out: list[dict] = []
    skipped = 0
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            skipped += 1
    return out, skipped, None


def _read_jsonl_with_positions(path: Path):
    """Wie `_read_jsonl_source`, liefert aber je gueltiger Zeile zusaetzlich
    Zeilennummer (1-basiert), Zeichenoffsets im rohen Dateitext und den
    SHA256 der eigenen Zeile -- fuer eine auflösbare eigene Quellreferenz je
    exportiertem Eintrag (02_AUFTRAG_REST_A13.md §R2: 'genaue eigene Quelle/
    Zeile/Offsets/Hash'). Rueckgabe: (rows, skipped, error, datei_sha256)
    mit rows = Liste aus (line_no, char_start, char_end, obj, line_sha256)."""
    try:
        if path.is_symlink():
            return [], 0, "abgelehnt: Symlink als Quelle", None
        if not path.is_file():
            return [], 0, None, None
    except OSError as exc:
        return [], 0, f"Lesefehler: {exc!r}", None
    try:
        raw = path.read_bytes()
    except OSError as exc:
        return [], 0, f"Lesefehler: {exc!r}", None
    sha = _sha256_bytes(raw)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return [], 0, f"Lesefehler: {exc!r}", sha
    out = []
    skipped = 0
    offset = 0
    line_no = 0
    for raw_line in text.splitlines(keepends=True):
        line_no += 1
        start = offset
        stripped = raw_line.rstrip("\n").rstrip("\r")
        end = start + len(stripped)
        offset += len(raw_line)
        content = stripped.strip()
        if not content:
            continue
        try:
            row = json.loads(content)
        except json.JSONDecodeError:
            skipped += 1
            continue
        out.append((line_no, start, end, row, hashlib.sha256(stripped.encode("utf-8")).hexdigest()))
    return out, skipped, None, sha


def _sanitize_route(route: "str | None") -> "str | None":
    """R2 (02_AUFTRAG_REST_A13.md §Eingangsroot): keine Userinfo/Passwoerter/
    Querytoken/Fragmente in report.json/md/source-index/issue-drafts -- nur
    Schema+Host+Port+Pfad. Reine Textzerlegung der bereits persistierten
    Route, KEIN Netzwerkzugriff/Upstream-Sanitizer."""
    if route is None:
        return None
    if not isinstance(route, str) or not route:
        return "[route: ungueltiger Wert, redigiert]"
    try:
        parts = urlsplit(route)
        if not parts.scheme or not parts.hostname:
            return "[route: kein Schema/Host, redigiert]"
        netloc = parts.hostname
        if parts.port is not None:
            netloc = f"{netloc}:{parts.port}"
        return urlunsplit((parts.scheme, netloc, parts.path, "", ""))
    except ValueError:
        return "[route: nicht parsebar, redigiert]"


def _sl_log_events(table_data: dict, table_id: str) -> list[dict]:
    """Baut aus `table.sl_log` (bereits vorhandene, tatsaechlich
    persistierte oeffentliche Tischquelle) eine In-Memory-Ansicht im
    `EventLog`-Eventformat, NUR um die bestehenden, unveraenderten
    Funktionen `extract_provenance_excerpts`/`generate_report`/
    `draft_issues` wiederzuverwenden (keine zweite Stichwortlogik). Die
    `event_id` ist BEWUSST als Tischstellen-Pointer erkennbar
    (`sl_log#<table_id>#<turn_idx>`), niemals ein erfundenes
    `events.jsonl`-Ereignis mit eigener Identitaet."""
    out: list[dict] = []
    for entry in table_data.get("sl_log") or []:
        turn_idx = entry.get("turn_idx")
        out.append({
            "event_id": f"sl_log#{table_id}#{turn_idx}",
            "event_type": "sl_turn",
            "actor": entry.get("origin_persona_key"),
            "payload": {
                "content": entry.get("content") or "",
                "table_id": table_id,
                "section_id": None,  # `table.sl_log` traegt keinen Section-Bezug je Zeile.
                "turn_idx": turn_idx,
                "origin_persona_key": entry.get("origin_persona_key"),
            },
            "ts": None,
        })
    return out


def _enrich_excerpt_with_pointer(
    excerpt: ProvenanceExcerpt, table_data: dict, source_rel_path: str, source_sha256: str,
) -> None:
    """Ergaenzt EINEN von der unveraenderten `extract_provenance_excerpts`
    gelieferten Treffer um die geforderte auflösbare Quellreferenz
    (relativer Pfad + Quelldatei-SHA256 + JSON-Pointer + Zeichenpositionen
    + Texthash, 02_AUFTRAG_A13.md §2). Mutiert nur die NEUEN, optionalen
    Felder -- das bestehende Dataclass-Verhalten/-API bleibt unveraendert."""
    turn_idx = excerpt.turn_idx
    excerpt.source_path = source_rel_path
    excerpt.source_sha256 = source_sha256
    if turn_idx is None:
        return
    sl_log = table_data.get("sl_log") or []
    if not (0 <= turn_idx < len(sl_log)):
        return
    excerpt.pointer = f"/sl_log/{turn_idx}/content"
    content = sl_log[turn_idx].get("content") or ""
    start = content.find(excerpt.excerpt)
    if start >= 0:
        excerpt.char_offset_start = start
        excerpt.char_offset_end = start + len(excerpt.excerpt)
    excerpt.excerpt_sha256 = hashlib.sha256(excerpt.excerpt.encode("utf-8")).hexdigest()


def _save_diff(before: "dict | None", after: "dict | None") -> dict:
    """Rein strukturelle Differenz zweier Save-Bloecke (Zeichenkontenliste)
    -- KEIN Regelmotor, nur ein technischer Feldvergleich fuer das
    Quellenpaar (02_AUFTRAG_REST_A13.md §R1: 'Verknuepfe ... Saveaenderungen
    mit ... Szenenstellen als technische Quellenpaare')."""
    def chars_by_id(block: "dict | None") -> dict:
        out: dict = {}
        for c in (block or {}).get("characters") or []:
            if isinstance(c, dict) and c.get("char_id"):
                out[c["char_id"]] = c
        return out

    before_chars = chars_by_id(before)
    after_chars = chars_by_id(after)
    return {
        "chars_added": sorted(set(after_chars) - set(before_chars)),
        "chars_removed": sorted(set(before_chars) - set(after_chars)),
        "chars_changed": sorted(
            cid for cid in (set(before_chars) & set(after_chars)) if before_chars[cid] != after_chars[cid]
        ),
    }


def _a13_check_save_identity(save: object, expected_cid: str, label: str) -> dict:
    """Validate the already-persisted personal-save identity; do not repair it."""
    if not isinstance(save, dict):
        raise A13SourceError(f"{label}: persoenliches Saveobjekt fehlt/ungueltig -- Hold.")
    characters = save.get("characters")
    if not isinstance(characters, list) or len(characters) != 1 or not isinstance(characters[0], dict):
        raise A13SourceError(f"{label}: kein eindeutig persoenlicher Ein-Figuren-Save -- Hold.")
    char = characters[0]
    actual = char.get("char_id") or char.get("id")
    if actual != expected_cid or any(char.get(k) not in (None, expected_cid) for k in ("char_id", "id")):
        raise A13SourceError(f"{label}: Figurenbindung widerspricht dem ausgewaehlten Tisch -- Hold.")
    return save


def _load_completion(
    data_root: Path, table_id: str, section_id: str, members: list[str],
    chrononaut_ids: dict[str, str], run_id_value: "str | None",
    excerpts: list[ProvenanceExcerpt], source_reads: list,
) -> dict:
    """Resolve the existing plan/guard references, not current/highest versions.

    Missing optional evidence is PARTIAL. Contradictory identity, hash or unsafe
    path is a source Hold. All reads stay in the selected root. No store writes.
    """
    out = {"plan": None, "final": None, "guards": {}, "sources": {}, "partial_reasons": []}

    def read_relative(rel, label):
        path = _resolve_within_root(data_root, rel)  # Never downgrade an unsafe path.
        if path.is_symlink():
            raise A13SourceError(f"{label}: Symlink als Quelle abgelehnt -- Hold.")
        data, digest, error = _read_json_source(path)
        if digest is not None:
            source_reads.append((path, digest))
        return data, digest, error

    for kind in ("plan", "final"):
        rel = f"completion/{section_id}__{kind}.json"
        data, digest, error = read_relative(rel, f"completion-{kind}")
        if error == "fehlt":
            out["partial_reasons"].append(f"{rel} fehlt -- Abschlussquelle nicht aufgezeichnet.")
            continue
        if error or not isinstance(data, dict):
            raise A13SourceError(f"completion-{kind} unlesbar/ungueltig -- Hold.")
        if data.get("table_id") != table_id:
            raise A13SourceError(f"completion-{kind}: Bindungsfehler: widerspruechliche Tischbindung -- Hold.")
        if (kind == "final" or "section_id" in data) and data.get("section_id") != section_id:
            raise A13SourceError(f"completion-{kind}: widerspruechliche Bindung der Section -- Hold.")
        if "run_id" in data and run_id_value is not None and data["run_id"] != run_id_value:
            raise A13SourceError(f"completion-{kind}: widerspruechliche Runbindung -- Hold.")
        bound = data.get("members")
        valid_type = isinstance(bound, dict) if kind == "plan" else isinstance(bound, list)
        if not valid_type or len(bound) != len(members) or set(bound) != set(members):
            raise A13SourceError(f"completion-{kind}: Mitglieder widersprechen dem ausgewaehlten Tisch -- Hold.")
        out[kind] = data
        out["sources"][kind] = {"path": rel, "sha256": digest}

    plan_members = (out["plan"] or {}).get("members", {})
    for pk in members:
        cid = chrononaut_ids[pk]
        member_plan = plan_members.get(pk)
        if member_plan is not None:
            if not isinstance(member_plan, dict):
                raise A13SourceError(f"Planmitglied {pk!r} ungueltig -- Hold.")
            _a13_check_save_identity(member_plan.get("save"), cid, f"Plan-Save {pk!r}")
        guard_rel = f"completion/{cid}__{section_id}.json"
        guard, guard_sha, error = read_relative(guard_rel, f"Guard {pk!r}")
        if error == "fehlt":
            out["partial_reasons"].append(f"Abschluss-Guard fuer {pk!r} fehlt -- nicht aufgezeichnet.")
            continue
        if error or not isinstance(guard, dict):
            raise A13SourceError(f"Abschluss-Guard fuer {pk!r} unlesbar/ungueltig -- Hold.")
        for field, expected in (("persona_key", pk), ("chrononaut_id", cid), ("section_id", section_id), ("table_id", table_id)):
            if guard.get(field) != expected:
                raise A13SourceError(f"Guard {pk!r}: {field} widerspricht der vorhandenen Bindung -- Hold.")
        if "run_id" in guard and run_id_value is not None and guard["run_id"] != run_id_value:
            raise A13SourceError(f"Guard {pk!r}: widerspruechliche Runbindung -- Hold.")
        if guard.get("current_save_path") not in (None, f"current_saves/{pk}.json"):
            raise A13SourceError(f"Guard {pk!r}: fremde Currentreferenz -- Hold.")
        entry = {"guard": guard, "source": {"path": guard_rel, "sha256": guard_sha}}
        save_rel = guard.get("save_path")
        if save_rel:
            _resolve_within_root(data_root, save_rel)
            if not isinstance(save_rel, str) or not re.fullmatch(r"current_saves/" + re.escape(pk) + r"__versions/[0-9]+\.json", save_rel):
                raise A13SourceError(f"Guard {pk!r}: Endsave verweist nicht auf die eigene historische Version -- Hold.")
            data, digest, error = read_relative(save_rel, f"Endsave {pk!r}")
            if error:
                entry["section_end_save"] = None
                entry["section_end_save_error"] = error
                out["partial_reasons"].append(f"Endsave {save_rel} fuer {pk!r} fehlt/ist unlesbar -- Quellenpaar unvollstaendig.")
            else:
                if guard.get("save_sha256") != digest:
                    raise A13SourceError(f"Guard {pk!r}: save_sha256 des publizierten Endsaves widerspricht Quelldatei -- Hold.")
                data = _a13_check_save_identity(data, cid, f"Endsave {pk!r}")
                if member_plan is not None and member_plan["save"] != data:
                    raise A13SourceError(f"Plan und publizierter Endsave fuer {pk!r} widersprechen einander -- Hold.")
                entry.update(section_end_save=data, section_end_save_sha256=digest,
                             section_end_save_sha256_matches_guard=True,
                             section_end_save_source={"path": save_rel, "sha256": digest})
        else:
            out["partial_reasons"].append(f"Endsave fuer {pk!r} nicht referenziert -- Quellenpaar unvollstaendig.")
        if guard.get("status") != "completed":
            out["partial_reasons"].append(f"Guard fuer {pk!r} bestaetigt keinen completed-Zustand.")

        prev = member_plan.get("expected_prev_ref") if member_plan else None
        if prev is None:
            out["partial_reasons"].append(f"Historische Vorversion fuer {pk!r} nicht referenziert -- kein vollstaendiges Quellenpaar.")
        elif not isinstance(prev, dict) or not isinstance(prev.get("seq"), int) or isinstance(prev["seq"], bool) or prev["seq"] < 1:
            raise A13SourceError(f"Historische Vorreferenz fuer {pk!r} ungueltig -- Hold.")
        elif run_id_value is None or prev.get("run_id") is None:
            out["partial_reasons"].append(f"Historische Vorversion fuer {pk!r} mangels Run-ID nicht eindeutig zuordenbar.")
        else:
            if prev["run_id"] != run_id_value:
                raise A13SourceError(f"Historische Vorreferenz fuer {pk!r}: fremde Run-ID -- Hold.")
            rel = f"current_saves/{pk}__versions/{prev['seq']:04d}.json"
            data, digest, error = read_relative(rel, f"Historische Vorversion {pk!r}")
            if error:
                out["partial_reasons"].append(f"historische Vorversion {rel} fehlt/ist unlesbar -- Quellenpaar unvollstaendig.")
            else:
                entry["section_start_save"] = _a13_check_save_identity(data, cid, f"Historische Vorversion {pk!r}")
                entry["section_start_save_source"] = {"path": rel, "sha256": digest}
        if entry.get("section_start_save") is not None and entry.get("section_end_save") is not None:
            entry["technical_source_pair"] = {
                "before": entry["section_start_save_source"], "after": entry["section_end_save_source"],
                "save_diff": _save_diff(entry["section_start_save"], entry["section_end_save"]),
                "linked_scene_excerpts": [
                    {"category": ex.category, "pointer": ex.pointer, "source_path": ex.source_path,
                     "source_sha256": ex.source_sha256, "excerpt": ex.excerpt,
                     "char_offset_start": ex.char_offset_start, "char_offset_end": ex.char_offset_end,
                     "excerpt_sha256": ex.excerpt_sha256}
                    for ex in excerpts if ex.persona_key == pk
                ],
                "disclaimer": "Rein technisches Quellenpaar aus Save-Differenz + Szenenausschnitt -- KEIN Kauf-/Erfolgs-/Spassbeweis.",
            }
        out["guards"][pk] = entry
    return out


def _load_requests(
    data_root: Path, table_id: str, section_id: str, source_reads: list,
) -> tuple[list[dict], list[str], "str | None"]:
    """Nur `requests/*.json`, deren `table_id`/`section_id` EXAKT zum
    gewaehlten Abschnitt gehoeren (02_AUFTRAG_REST_A13.md §R1: Route
    bereinigt, sent/received/accounted unterscheiden, reservierter Betrag
    != realer Gesamtpreis). Abwesenheit des Ordners ist keine Fehlerquelle
    (optionale Quelle). Eine kaputte/unlesbare Requestdatei wird NICHT still
    uebersprungen -- sie landet in `unreadable` (konkreter PARTIAL-Grund),
    nicht bloss als fehlender Treffer. `requests/` selbst geht durch den
    einheitlichen Rootcheck (auch Elternlink-Escape)."""
    try:
        requests_dir = _resolve_within_root(data_root, "requests")
    except A13SourceError as exc:
        raise A13SourceError(f"requests/ unsicherer Pfad: {exc}") from exc
    if requests_dir.is_symlink():
        raise A13SourceError("requests/: Symlink als Quelle abgelehnt -- Hold.")
    if not requests_dir.is_dir():
        return [], [], None
    out: list[dict] = []
    unreadable: list[str] = []
    for p in sorted(requests_dir.glob("*.json")):
        try:
            safe_p = _resolve_within_root(data_root, f"requests/{p.name}")
        except A13SourceError as exc:
            raise A13SourceError("Requestquelle verlaesst das Datenroot -- Hold.") from exc
        if safe_p.is_symlink():
            raise A13SourceError("Symlink als Requestquelle abgelehnt -- Hold.")
        data, sha, err = _read_json_source(safe_p)
        if sha is not None:
            source_reads.append((safe_p, sha))
        if err:
            unreadable.append(f"requests/{p.name} ({err})")
            continue
        if not isinstance(data, dict):
            unreadable.append(f"requests/{p.name} (kein Requestobjekt)")
            continue
        if data.get("table_id") != table_id or data.get("section_id") != section_id:
            continue
        out.append({
            "id": data.get("id"),
            "role": data.get("role"),
            "route": _sanitize_route(data.get("route")),
            "state": data.get("state"),
            "turn_idx": data.get("turn_idx"),
            "participant": data.get("participant"),
            "reserved_usd": data.get("reserved_usd"),
            "dollar_billed": data.get("dollar_billed"),
            "usage": data.get("usage"),
            "content_chars": data.get("content_chars"),
            "content_sha256": data.get("content_sha256"),
            "received_seconds": data.get("received_seconds"),
            "source": {"path": f"requests/{p.name}", "sha256": sha},
        })
    out.sort(key=lambda r: (r.get("turn_idx") if r.get("turn_idx") is not None else -1, r.get("id") or ""))
    return out, unreadable, None


def _load_reflections(
    data_root: Path, section_id: str, members: list[str], source_reads: list,
) -> tuple[list[dict], int, "str | None"]:
    """NUR `kind=ai_reflection_received`-Eintraege, deren `section_id`
    exakt dem gewaehlten Abschnitt entspricht UND deren `persona_key` zu
    den gewaehlten Tischmitgliedern gehoert (02_AUFTRAG_A13.md §3: 'nur
    eigene passende Abschnittsreflexionen der gewaehlten Personas').
    `kind`-Allowlist (nur `ai_reflection_received`) statt Denylist: in
    derselben `reflections.jsonl` liegen auch echte menschliche
    Privatnotizen mit `kind="human_note"` (geschrieben von
    `core/runtime.py`) -- diese existieren in der Quelle sehr wohl, werden
    aber durch die exakte Kind-Allowlist strukturell ausgeschlossen, nicht
    weil sie fehlen. Jede exportierte Reflexion traegt `private:true` plus
    eine auflösbare eigene Quelle (Pfad/Zeile/Offsets/Hash,
    02_AUFTRAG_REST_A13.md §R2) und einen Hinweis, dass `origin_source`
    KEINE Modellidentitaets-/Nutzungsbestaetigung ist."""
    try:
        path = _resolve_within_root(data_root, "reflections.jsonl")
    except A13SourceError as exc:
        raise A13SourceError("Reflexionsquelle verlaesst das Datenroot -- Hold.") from exc
    if path.is_symlink():
        raise A13SourceError("Symlink als Reflexionsquelle abgelehnt -- Hold.")
    rows, skipped, err, sha = _read_jsonl_with_positions(path)
    if err:
        return [], 0, err
    if sha is not None:
        source_reads.append((path, sha))
    out = []
    for line_no, start, end, row, line_sha in rows:
        if row.get("kind") != "ai_reflection_received":
            continue
        if row.get("section_id") != section_id:
            continue
        if row.get("persona_key") not in members:
            continue
        out.append({
            "persona_key": row.get("persona_key"), "section_id": row.get("section_id"),
            "text": row.get("text"), "origin_source": row.get("origin_source"),
            "origin_source_note": "origin_source ist keine Modellidentitaets-/Nutzungsbestaetigung.",
            "ts": row.get("ts"),
            "private": True,
            "source": {
                "path": "reflections.jsonl", "line": line_no,
                "char_offset_start": start, "char_offset_end": end, "sha256": line_sha,
            },
        })
    return out, skipped, None


def _provenance_issue_drafts(excerpts: list[ProvenanceExcerpt]) -> list[IssueDraft]:
    """A13 §3: eine Ausruestungs-/Boss-/Kampf-/Drift-Erwaehnung ist ein
    technischer Befund, KEIN bewiesener Kauf/Erfolg -- der Entwurf sagt das
    woertlich und traegt NUR auflösbare sl_log-Pointer als Beleg, niemals
    private Reflexionstexte."""
    by_category: dict[str, list[ProvenanceExcerpt]] = {}
    for ex in excerpts:
        by_category.setdefault(ex.category, []).append(ex)
    drafts: list[IssueDraft] = []
    for category, items in sorted(by_category.items()):
        drafts.append(IssueDraft(
            title=f"{len(items)} technische Erwaehnung(en) der Kategorie '{category}'",
            body=(
                f"Lokale Stichwortsuche fand {len(items)} Fundstelle(n) der Kategorie {category!r} im "
                "oeffentlichen sl_log. Das ist eine technische Erwaehnung, KEIN bewiesener Kauf, Einsatz "
                "oder Erfolg -- eine Besitzaenderung (Save-Vergleich) muesste separat belegt werden."
            ),
            evidence_event_ids=[ex.event_id for ex in items],
        ))
    return drafts


def build_source_report(
    data_dir: "str | Path", table_id: str, section_id: str, *, include_persona_feedback: bool = False,
    generated_at: "str | None" = None,
) -> dict:
    """Baut den vollstaendigen A13-Quellenbericht als reines, JSON-
    serialisierbares dict. Rein lesend (s. Modulkopf); wirft
    `A13SourceError` bei einer Pflichtquelle/Bindung, die NICHT einfach
    'optional fehlend' ist (dann PARTIAL statt Fehler)."""
    _require_safe_id(table_id, "--table")
    _require_safe_id(section_id, "--section")
    data_root = Path(data_dir)
    if not data_root.is_dir():
        raise A13SourceError(f"--data-dir {data_dir!r} ist kein vorhandenes Verzeichnis.")
    data_root = data_root.resolve()

    partial_reasons: list[str] = []
    # R2 (02_AUFTRAG_REST_A13.md §Eingangsroot): jede waehrend der Sammlung
    # erfolgreich gelesene Quelle wird hier vermerkt (Pfad + gelesener
    # SHA256) und am Ende erneut gelesen -- eine beobachtete Aenderung ist
    # ein konkreter Snapshot-Hold, kein `COMPLETE` auf gemischten Staenden.
    source_reads: list[tuple[Path, str]] = []

    run_path = _resolve_within_root(data_root, "run_id.json")
    if run_path.is_symlink():
        raise A13SourceError("Symlink als Run-ID-Quelle abgelehnt -- Hold.")
    run_data, run_sha, run_err = _read_json_source(run_path)
    if run_err:
        partial_reasons.append(f"run_id.json nicht auswertbar ({run_err}) -- Run-Bezug nicht aufgezeichnet.")
        run_id_value = None
        run_source = None
    else:
        run_id_value = run_data.get("run_id") if isinstance(run_data, dict) else None
        run_source = {"path": "run_id.json", "sha256": run_sha}
        source_reads.append((run_path, run_sha))

    # Pflichtquelle: EINHEITLICHER Rootcheck (auch Elternlinks von `tables/`)
    # -- eine Verzeichnislink-Flucht aus dem Datenroot wird VOR dem Read
    # abgewiesen, nicht erst am (womoeglich verlinkten) Endergebnis erkannt.
    table_path = _resolve_within_root(data_root, f"tables/{table_id}.json")
    table_data, table_sha, table_err = _read_json_source(table_path)
    if table_err:
        # Pflichtquelle: unlesbar/fehlend ist ein kontrollierter Fehler, kein
        # leerer gesunder Bericht (02_AUFTRAG_A13.md §4).
        raise A13SourceError(f"Pflichtquelle tables/{table_id}.json unlesbar/fehlend: {table_err}")
    if table_data.get("table_id") != table_id:
        raise A13SourceError(
            f"tables/{table_id}.json enthaelt table_id={table_data.get('table_id')!r} -- Bindungsfehler."
        )
    source_reads.append((table_path, table_sha))
    members = list(table_data.get("members") or [])
    chrononaut_ids = dict(table_data.get("chrononaut_ids") or {})
    if (not members or len(members) != len(set(members))
            or table_data.get("leader") not in members or set(chrononaut_ids) != set(members)):
        raise A13SourceError("Tischmitglieder/Figurenzuordnung unvollstaendig oder widerspruechlich -- Hold.")
    for pk in members:
        _require_safe_id(pk, "Persona")
        _require_safe_id(chrononaut_ids[pk], "Figur")

    # R1: fehlende GM-Modell-/Prompt-/Regelquellenmetadaten explizit
    # unbekannt/nicht aufgezeichnet halten -- Vollstaendigkeitsurteil daran
    # ausrichten (PARTIAL statt pauschal COMPLETE), keine ENV-Ergaenzung.
    metadata_keys = {
        "GM-Modell": ("gm_model", "model"),
        "Prompt": ("prompt_version", "prompt_sha256", "prompt_hash"),
        "Regelquelle": ("ruleset_version", "rules_sha256", "ruleset_sha256"),
    }
    metadata_rows = table_data.get("sl_log") or []
    for label, keys in metadata_keys.items():
        missing = [i for i, row in enumerate(metadata_rows)
                   if not isinstance(row, dict) or not any(
                       isinstance(row.get(k), str) and row[k].strip() for k in keys)]
        if not metadata_rows or missing:
            partial_reasons.append(
                f"{label}-Metadaten nicht aufgezeichnet/inhaltlich leer fuer SL-Stellen {missing}; "
                "keine ENV-Ergaenzung. Ein origin_source-Label ist kein Modellbeweis."
            )

    sl_events = _sl_log_events(table_data, table_id)
    try:
        events_path = _resolve_within_root(data_root, "events.jsonl")
    except A13SourceError as exc:
        raise A13SourceError("Eventquelle verlaesst das Datenroot -- Hold.") from exc
    else:
        if events_path.is_symlink():
            raise A13SourceError("Symlink als Eventquelle abgelehnt -- Hold.")
        events_present = events_path.is_file()
        if events_present:
            # A13 bleibt auf table.sl_log als Turnquelle begrenzt
            # (02_AUFTRAG_A13.md §1, keine Doppelzaehlung); ein vorhandenes
            # events.jsonl wird trotzdem tatsaechlich gelesen, um eine
            # beschaedigte Quelle konkret auszuweisen statt sie generisch
            # als "vorhanden, aber nicht gelesen" zu verstecken.
            ev_rows, ev_skipped, ev_err, ev_sha = _read_jsonl_with_positions(events_path)
            if ev_sha is not None:
                source_reads.append((events_path, ev_sha))
            if ev_err:
                partial_reasons.append(
                    f"events.jsonl beschaedigt/unlesbar ({ev_err}) -- Quelle bleibt table.sl_log, keine Doppelzaehlung."
                )
            elif ev_skipped:
                partial_reasons.append(
                    f"events.jsonl enthaelt {ev_skipped} beschaedigte/unparsebare Zeile(n) (Parsefehler) -- "
                    "Quelle bleibt table.sl_log, keine Doppelzaehlung; beschaedigte Zeilen wurden nicht verwendet."
                )
            else:
                partial_reasons.append(
                    "events.jsonl ist in dieser Datenkopie vorhanden und wurde auf Lesbarkeit geprueft (keine "
                    "beschaedigten Zeilen gefunden); A13 nutzt sie dennoch NICHT als Turnquelle (Quelle bleibt "
                    "table.sl_log, keine Doppelzaehlung)."
                )
    local_report = generate_report(sl_events)
    excerpts = extract_provenance_excerpts(sl_events)
    for ex in excerpts:
        _enrich_excerpt_with_pointer(ex, table_data, f"tables/{table_id}.json", table_sha)

    completion = _load_completion(
        data_root, table_id, section_id, members, chrononaut_ids, run_id_value, excerpts, source_reads,
    )
    partial_reasons.extend(completion.pop("partial_reasons"))

    requests, unreadable_requests, requests_err = _load_requests(data_root, table_id, section_id, source_reads)
    if requests_err:
        partial_reasons.append(f"requests/ nicht vollstaendig auswertbar: {requests_err}")
    if unreadable_requests:
        # R1: kaputte/unlesbare Requestdateien NICHT still uebergehen --
        # konkret benennen, nicht in den zugeordneten Records enthalten.
        partial_reasons.append(
            f"{len(unreadable_requests)} Requestdatei(en) nicht auswertbar (Zuordnung zu Tisch/Abschnitt "
            f"unklar, nicht in den {len(requests)} zugeordneten Records enthalten): " + "; ".join(unreadable_requests)
        )

    reflections: list[dict] = []
    if include_persona_feedback:
        reflections, skipped, refl_err = _load_reflections(data_root, section_id, members, source_reads)
        if refl_err:
            partial_reasons.append(f"reflections.jsonl nicht auswertbar: {refl_err}")
        elif skipped:
            partial_reasons.append(f"reflections.jsonl: {skipped} beschaedigte Zeile(n) uebersprungen.")

    issue_drafts = draft_issues(local_report, sl_events) + _provenance_issue_drafts(excerpts)

    # R2: Snapshot-Hold -- ALLE waehrend der Sammlung gelesenen Quellen
    # werden HIER (nach dem letzten Read, VOR jeder Ausgabe) erneut
    # gelesen; eine beobachtete Aenderung ist ein konkreter Hold, kein
    # `COMPLETE` auf gemischten Staenden. Keine Sperre, kein Retry, keine
    # Powerloss-/Atomaritaetsgarantie -- nur der belegte Nachvergleich.
    for checked_path, expected_sha in source_reads:
        try:
            _resolve_within_root(data_root, checked_path.relative_to(data_root).as_posix())
            if checked_path.is_symlink():
                raise OSError(f"Quelle wurde nach dem Lesen durch einen Symlink ersetzt: {checked_path}")
            actual_raw = checked_path.read_bytes()
        except OSError as exc:
            raise A13SourceError(
                f"Snapshot-Hold: Quelle {checked_path} ist beim Abschlussvergleich nicht mehr in der gelesenen "
                f"Form verfuegbar ({exc!r}) -- kein Bericht auf gemischten Staenden."
            ) from exc
        actual_sha = _sha256_bytes(actual_raw)
        if actual_sha != expected_sha:
            raise A13SourceError(
                f"Snapshot-Hold: Quelle {checked_path} hat sich waehrend der Berichterstellung veraendert "
                f"(gelesen={expected_sha}, jetzt={actual_sha}) -- kein Bericht auf gemischten Staenden."
            )

    generated_at = generated_at or datetime.now(timezone.utc).isoformat()
    status = "PARTIAL" if partial_reasons else "COMPLETE"

    return {
        "report_kind": "a13_local_operator_source_report",
        "generated_at_utc": generated_at,
        "generated_at_note": "Zeitpunkt der BERICHTERSTELLUNG, kein damaliges Spielereignis.",
        "scope": {
            "data_dir": str(data_root), "table_id": table_id, "section_id": section_id,
            "include_persona_feedback": include_persona_feedback,
        },
        "status": status,
        "partial_reasons": partial_reasons,
        "source_files": [
            {"path": p.relative_to(data_root).as_posix(), "sha256": digest}
            for p, digest in dict(source_reads).items()
        ],
        "run": {"run_id": run_id_value, "source": run_source},
        "table": {
            "table_id": table_data.get("table_id"), "leader": table_data.get("leader"),
            "members": members, "chrononaut_ids": chrononaut_ids, "status": table_data.get("status"),
            "source": {"path": f"tables/{table_id}.json", "sha256": table_sha},
        },
        "sl_log": {
            "turns": local_report.total_events, "source": "table.sl_log",
            "events_jsonl_present_but_unused": events_present,
        },
        "provenance_excerpts": [ex.__dict__ for ex in excerpts],
        "completion": completion,
        "requests": requests,
        "reflections": reflections,
        "issue_drafts": [d.__dict__ for d in issue_drafts],
    }


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _write_output_files(output_dir: Path, report_data: dict) -> list[Path]:
    """Schreibt AUSSCHLIESSLICH in `output_dir` (neu, vom Aufrufer bereits
    auf Kollision/Lage geprueft): report.json, report.md, issue-drafts.md,
    source-index.json, SHA256SUMS. Keine andere Datei wird beruehrt."""
    output_dir.mkdir(parents=True, exist_ok=False)
    written: list[Path] = []

    report_json_path = output_dir / "report.json"
    report_json_path.write_text(json.dumps(report_data, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    written.append(report_json_path)

    scope = report_data["scope"]
    lines = [
        f"# A13-Quellenbericht: {scope['table_id']} / {scope['section_id']}",
        "",
        f"Erstellt (Berichtszeit, kein Spielereignis): {report_data['generated_at_utc']}",
        f"Status: {report_data['status']}",
        "",
    ]
    if report_data["partial_reasons"]:
        lines.append("## Unvollstaendigkeiten")
        lines.extend(f"- {r}" for r in report_data["partial_reasons"])
        lines.append("")
    lines.append(f"## Tisch: {report_data['table']['table_id']} (Leader: {report_data['table']['leader']})")
    lines.append(f"Mitglieder: {', '.join(report_data['table']['members'])}")
    lines.append(f"SL-Runden (Quelle: table.sl_log): {report_data['sl_log']['turns']}")
    lines.append("")
    lines.append("## Quellenbelegte Ausschnitte")
    for ex in report_data["provenance_excerpts"]:
        lines.append(
            f"- [{ex['category']}] {ex.get('source_path')} {ex.get('pointer')} "
            f"(sha256={ex.get('source_sha256')}): \"{ex['excerpt']}\""
        )
    lines.append("")
    if report_data["reflections"]:
        lines.append("## Freigegebene Persona-Reflexionen (PRIVAT, subjektiv, kein Tischwissen)")
        for r in report_data["reflections"]:
            lines.append(f"- {r['persona_key']} ({r['section_id']}, privat={r['private']}): {r['text']}")
        lines.append("")
    report_md_path = output_dir / "report.md"
    report_md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    written.append(report_md_path)

    issue_lines = ["# Issue-ENTWUERFE (lokal, technisch, quellengestuetzt -- KEINE automatischen GitHub-Issues)", ""]
    for d in report_data["issue_drafts"]:
        issue_lines.append(f"## {d['title']}")
        issue_lines.append(d["body"])
        issue_lines.append(f"Belege: {', '.join(d['evidence_event_ids'])}")
        issue_lines.append("")
    issue_drafts_path = output_dir / "issue-drafts.md"
    issue_drafts_path.write_text("\n".join(issue_lines) + "\n", encoding="utf-8")
    written.append(issue_drafts_path)

    # Vollstaendiger Quellenindex fuer wirklich verwendete Quellen
    # (02_AUFTRAG_REST_A13.md §R1): auch Guards, historische Vor-/
    # Nachsaves und die freigegebene Feedbackquelle -- keine Voll-Dumps
    # unnoetiger Registry/States.
    guard_sources: dict = {}
    for pk, g in (report_data["completion"].get("guards") or {}).items():
        idx: dict = {}
        if g.get("source"):
            idx["guard"] = g["source"]
        if g.get("section_end_save_source"):
            idx["section_end_save"] = g["section_end_save_source"]
        if g.get("section_start_save_source"):
            idx["section_start_save"] = g["section_start_save_source"]
        if idx:
            guard_sources[pk] = idx

    source_index = {
        "files": report_data["source_files"],
        "table": report_data["table"]["source"],
        "run": report_data["run"]["source"],
        "completion": report_data["completion"].get("sources", {}),
        "guards": guard_sources,
        "requests": [r["source"] for r in report_data["requests"]],
        "provenance_excerpts": [
            {"pointer": ex.get("pointer"), "source_path": ex.get("source_path"), "source_sha256": ex.get("source_sha256")}
            for ex in report_data["provenance_excerpts"]
        ],
        "reflections": [r["source"] for r in report_data["reflections"] if r.get("source")],
    }
    source_index_path = output_dir / "source-index.json"
    source_index_path.write_text(json.dumps(source_index, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    written.append(source_index_path)

    sums_path = output_dir / "SHA256SUMS"
    sums_lines = [f"{_sha256_file(p)}  {p.name}" for p in written]
    sums_path.write_text("\n".join(sums_lines) + "\n", encoding="utf-8")
    return written


def main(argv: list[str], repo_root: "str | Path") -> int:
    """`python scripts/mmo_sim.py report ...` -- der neue fruehe
    Dispatcherzweig (DISPATCH-INSERTION.json) ruft GENAU diese Funktion vor
    jeder Teilnehmer-/TUI-/Adapterkonstruktion auf. KEIN Modellcall, KEIN
    neuer Event-/Booking-/Publikationsschreiber; Ausgabe ausschliesslich im
    neuen, vom Aufrufer angegebenen `--output-dir`."""
    parser = argparse.ArgumentParser(
        prog="mmo_sim.py report",
        description="A13: lokaler Operator-Quellenbericht zu genau einem Tisch+Abschnitt (keine Report-KI, keine Modellaufrufe).",
    )
    parser.add_argument("--data-dir", required=True, help="vorhandene synthetische/uebernommene Datenkopie (run_dir)")
    parser.add_argument("--table", required=True, help="Tisch-ID (tables/<id>.json)")
    parser.add_argument("--section", required=True, help="Abschnitts-ID (completion/<id>__plan.json etc.)")
    parser.add_argument("--output-dir", required=True, help="NEUER, noch nicht vorhandener externer Ausgabeordner")
    parser.add_argument(
        "--include-persona-feedback", action="store_true",
        help="bewusste Operatorfreigabe: eigene Abschnittsreflexionen der gewaehlten Tischpersonas mit exportieren "
             "(niemals menschliche Privatnotizen, niemals in Issue-Entwuerfen).",
    )
    args = parser.parse_args(argv)  # --help/fehlende Pflichtargumente: argparse beendet HIER, vor jedem Datenzugriff.

    output_dir = Path(args.output_dir)
    if output_dir.exists():
        print(f"A13-Report: --output-dir {output_dir} existiert bereits -- keine Ueberschreibung, kein Bericht.", file=sys.stderr)
        return 2

    repo_root_resolved = Path(repo_root).resolve()
    data_dir_path = Path(args.data_dir)
    try:
        data_root_for_check = data_dir_path.resolve() if data_dir_path.exists() else data_dir_path.absolute()
    except OSError:
        data_root_for_check = data_dir_path.absolute()
    # .resolve() statt .absolute(): loest Symlink-Bestandteile im (ggf. noch
    # nicht vollstaendig existierenden) --output-dir-Pfad auf, damit der
    # folgende Vergleich nicht durch einen Symlink-Umweg in den geschuetzten
    # Baum umgangen werden kann (strict=False funktioniert auch, bevor
    # `output_dir` selbst existiert).
    output_abs = output_dir.resolve()
    for guarded_root, label in ((repo_root_resolved, "Repoquellbaum"), (data_root_for_check, "Datenverzeichnis")):
        try:
            guarded_resolved = guarded_root.resolve()
        except OSError:
            guarded_resolved = guarded_root
        # Reiner Praefixvergleich (funktioniert auch, bevor `output_dir` existiert).
        if output_abs == guarded_resolved:
            print(f"A13-Report: --output-dir darf nicht im {label} liegen ({output_dir}).", file=sys.stderr)
            return 2
        try:
            output_abs.relative_to(guarded_resolved)
            print(f"A13-Report: --output-dir darf nicht im {label} liegen ({output_dir}).", file=sys.stderr)
            return 2
        except ValueError:
            pass

    try:
        report_data = build_source_report(
            args.data_dir, args.table, args.section, include_persona_feedback=args.include_persona_feedback,
        )
    except A13SourceError as exc:
        print(f"A13-Report: {exc}", file=sys.stderr)
        return 3

    try:
        written = _write_output_files(output_dir, report_data)
    except OSError as exc:
        print(f"A13-Report: Schreibfehler im Ausgabeordner -- kein vollstaendiger Bericht gemeldet: {exc!r}", file=sys.stderr)
        return 4

    print(
        f"A13-Report: {report_data['status']} -- {len(written)} Dateien unter {output_dir} "
        f"(Tisch={args.table}, Abschnitt={args.section})."
    )
    return 0
