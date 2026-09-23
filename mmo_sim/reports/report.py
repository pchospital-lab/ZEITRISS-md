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
