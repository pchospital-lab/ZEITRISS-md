#!/usr/bin/env python3
"""
mmo_sim/core/runtime.py — gemeinsame Runtime, von TUI UND headless Lab benutzt
(PLAN.md §3 Antwort 8: "beide bauen core/runtime.py; Paritaetstest liefert
denselben Offline-Dialog einmal per geskripteten Terminaleingaben, einmal
per Persona-Fake").

P2-Fertigstellung (I1, REVIEW-P2.md §I1): `run_full_section` ist jetzt eine
ECHTE Mehrfach-Turn-Schleife statt Anker->Gast-Import(e)->EIN Debrief-Turn.
Nach JEDEM GM-Turn wird SOFORT der Abschluss-Marker geprueft (A2-Invariante,
PLAN-CRITIC.md BLOCKER: kein zusaetzlicher Decision-Call vor der
Marker-Pruefung). Jede frische SL-Antwort fliesst ueber `store.persona_view`
in den Kontext der naechsten Entscheidung zurueck. Vor JEDEM Modellrequest
liest das Admission-Gate (`core/admission.py`, A1-BLOCKER) den persistierten
Lab-Stop-/Budget-Zustand FRISCH von der Platte — unabhaengig von einer zur
Konstruktionszeit injizierten LabRunner-Instanz.

Domaenenwissen (v7-Ernte-Extraktion, Marker-String) kommt ueber Callbacks/
Objekte von aussen (`harvest_extractor`, `marker`) — dieser Kern kennt sie
nicht (A1-Konsistenz)."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Callable

from . import request_ledger, store
from .admission import read_admission_block, reservation_for_request, reservation_for_wire_text
from .completion_marker import completion_marker_matches
from .controller import TableController
from .events import EventLog
from .persona_state import PersonaStateStore
from .store import HarvestValidator, TableSizePolicy

HarvestExtractor = Callable[[str, dict[str, str]], dict[str, dict]]
"""(debrief_text, chrononaut_id_to_persona) -> {persona_key: save_block}."""

DEFAULT_MAX_TURNS = 20
"""Strukturelle Sicherheitsgrenze UNABHAENGIG vom Lab-Budget (I1/A2): auch
ohne aktiven Lab-Lauf (kein `lab.status.json`) darf eine Szene ohne
Abschluss-Marker nicht endlos weiterlaufen. Ueberschreibbar per
`run_full_section(..., max_turns=...)` — z.B. fuer gezielt kurze Tests."""


@dataclass
class SectionOutcome:
    completion: store.CompletionResult
    harvested: dict = field(default_factory=dict)
    debrief_text: str = ""


class _GateBlocked(Exception):
    """F3 (K6/K8, WEGKARTE §6 A1): internes Signal, dass das Admission-Gate
    an einem der drei Pruefpunkte (vor Persona-Request, zwischen Persona-
    Request und GM-Request, vor Publish/Reflexion) blockiert hat. Wird
    ausschliesslich innerhalb von `run_full_section` gefangen."""

    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


def _embed_json_block(text: str, payload: dict) -> str:
    """F1 (K6/K7): bettet einen Payload (v7-Save ODER konsolidierte
    Tischnachrichten) als sichtbaren, mit `domain.zeitriss.saves.
    extract_all_saves`-kompatiblen Fenced-Block in den an den GM-Transport
    gehenden Wire-Text ein -- 'wie es der alte P1-Section-Aufrufer tat'
    (WEGKARTE §2 F1). Bleibt domaenenneutral (kennt kein 'v7', serialisiert
    nur ein beliebiges JSON-Objekt)."""
    return f"{text}\n\n```json\n{json.dumps(payload, ensure_ascii=False)}\n```"


class SectionRuntime:
    """Ein Abschnittslauf ueber einem Tisch. Gemeinsam von `ui/tui.py`
    (Mensch-Eingabe) und `lab/runner.py` (Persona-only) verwendet — beide
    NUR ueber `core/app_service.run_play_session` (I1/A4: Introspektions-
    /Spy-Test beweist den gemeinsamen Call-Pfad)."""

    def __init__(
        self,
        lobby: store.Lobby,
        table: store.Table,
        gm_transport,
        marker: str,
        harvest_validator: HarvestValidator,
        persona_state_store: PersonaStateStore,
        harvest_extractor: HarvestExtractor,
        event_log: EventLog | None = None,
    ):
        self.lobby = lobby
        self.table = table
        self.gm_transport = gm_transport
        self.marker = marker
        self.harvest_validator = harvest_validator
        self.persona_state_store = persona_state_store
        self.harvest_extractor = harvest_extractor
        self.event_log = event_log
        # A8 (WEGKARTE §6, groesstes Restrisiko): Resume-Phasenpersistenz.
        # `table` kann bereits einen persistierten `sl_log` mitbringen (ein
        # frischer Prozess laedt den Tisch ueber `store.create_table_from_
        # offer_log`s Resume-Zweig neu) -- Turn-Idx und "wer hat schon
        # geankert/importiert" werden dann aus dem echten Log rekonstruiert,
        # statt bei jeder neuen `SectionRuntime`-Instanz auf 0/None
        # zurueckzufallen (I1: "Resume legt Tisch/Phase/Turn/Chat nicht
        # wieder auf", Test 09/11). Best-effort: ein `sl_log`-Eintrag mit
        # `origin_persona_key == pk` heisst "pk hat bereits mindestens einen
        # Turn beigetragen (Anker bzw. Import)".
        self._turn_idx = len(table.sl_log)
        origins = {e.get("origin_persona_key") for e in table.sl_log}
        self._leader_anchored = table.leader in origins
        self._guests_imported = {m for m in table.members if m != table.leader and m in origins}
        self._consolidated_message_count = len(table.table_messages)
        self._current_section_id: str | None = None

    def _emit(self, event_type: str, ts: str, actor: str | None = None, payload: dict | None = None) -> None:
        if self.event_log is not None:
            self.event_log.append(event_type, ts, actor=actor, payload=payload)

    def _route_for(self, driver: object) -> str | None:
        """Q03 (PLAN-CRITIC F5/Auflage): die tatsaechliche Zielroute dieser
        konkreten Anfrage, falls der Treiber eine traegt (z.B.
        `PersonaApiConfig.base_url`) -- reine Namens-/Attributpruefung
        (duck typing, admission.py bleibt providerfrei), `None` fuer
        Treiber ohne Netzwerkroute (Hybrid-CLI, Human)."""
        cfg = getattr(driver, "config", None)
        return getattr(cfg, "base_url", None) if cfg is not None else None

    def _admitted_decision(
        self, role: str, controller: TableController, pk: str, ctx: dict,
        *, section_id: str | None = None,
    ):
        """I2-Nachzug (WEGKARTE §"EIN schlanker persistenter Requestauftrag",
        MAIN-ENTSCHEIDUNG A1-Ergaenzungen, Auflagen 1/5/6/7): EIN gemeinsamer
        Requestweg fuer JEDE Persona-Entscheidung (Einladung/Absprache/
        Spielzug/Reflexion, s. `act()`/`poll_guests_and_consolidate()`/
        `_collect_reflections()`) -- reserviert+committet VOR dem
        `controller.collect_decision(...)`-Aufruf (Case 05: ein verlorener
        Request darf Verbrauch/Verpflichtung nicht auf 0 zuruecksetzen) und
        persistiert einen Requestdatensatz (`core.request_ledger`). Wirft
        `_GateBlocked`, wenn das Admission-Gate NICHT freigibt -- der
        Aufrufer faengt das wie bisher.

        Menschliche Treiber (`_HumanDriver`, `is_human_driver`-Marker,
        `ui/tui.py`) verursachen laut Vertrag KEINE Modellkosten (A1/R06)
        und werden VOR jedem Reservierungs-/Ledger-Schritt erkannt -- fuer
        sie bleibt nur der reine Stop-/Pause-Gate-Check (Budget-neutral)
        erhalten, exakt wie vor diesem Umbau."""
        driver = controller.drivers.get(pk)
        is_human = getattr(driver, "is_human_driver", False)
        if is_human:
            reserved_usd, output_bound_known, route = None, True, None
        else:
            reserved_usd, output_bound_known = reservation_for_request(driver, ctx)
            route = self._route_for(driver)
        self._check_gate(reserved_usd, output_bound_known=output_bound_known, route=route)
        request_id = None
        if not is_human:
            cfg = getattr(driver, "config", None)
            request_id = request_ledger.begin(
                self.lobby.run_dir, role=role,
                content=json.dumps(ctx, ensure_ascii=False, sort_keys=True, default=str),
                reserved_usd=reserved_usd, route=route,
                output_limit_tokens=getattr(cfg, "max_tokens", None),
                table_id=self.table.table_id,
                section_id=section_id if section_id is not None else self._current_section_id,
            )
        t0 = time.monotonic()
        try:
            record = controller.collect_decision(pk, ctx)
        except Exception as exc:
            if request_id is not None:
                request_ledger.finish_error(self.lobby.run_dir, request_id, error=exc, seconds=time.monotonic() - t0)
            raise
        if request_id is not None:
            usage = (record.decision.meta or {}).get("usage")
            request_ledger.finish_received(self.lobby.run_dir, request_id, usage=usage, seconds=time.monotonic() - t0)
        return record

    def _check_gate(
        self, reserved_usd: float | None = None, *,
        output_bound_known: bool = True, route: str | None = None,
    ) -> None:
        """F3 (K6/K8, WEGKARTE §6 A1): liest den Admission-Block FRISCH von
        der Platte. A1-Klarstellung (Plan-Critic BLOCKER, bindend): dies ist
        AUSSCHLIESSLICH die bestehende Lab-Stop-/Budget-Semantik von
        `read_admission_block` (ohne `lab.status.json` -> `(False, None)`,
        unveraendert) -- KEIN separates Live-Go-Gate fuer echte
        Provideraufrufe (eigener, hier nicht beruehrter Vertrag, 03 §6).

        W2/I2-Ergaenzung (F..., Test 04/05): `reserved_usd`, wenn vom
        Aufrufer mitgegeben (s. `act()`s anfragebezogene Reservierung ueber
        `reservation_for_request`, Input+Output), ersetzt die
        Pauschalreservierung fuer DIESEN Gate-Check -- Default `None` bleibt
        fuer alle Aufrufer ohne bekannte Treiberkonfiguration/Kontext
        unveraendert. `output_bound_known`/`route` reichen die Q07-/Q03-
        Zusatzpruefungen an `read_admission_block` durch (Default bleibt
        unveraendert fuer Aufrufer ohne diese Information)."""
        blocked, reason = read_admission_block(
            self.lobby.run_dir, reserved_usd=reserved_usd,
            output_bound_known=output_bound_known, route=route,
        )
        if blocked:
            raise _GateBlocked(reason)

    def _collect_reflections(
        self, controller: TableController, section_id: str, ts: str,
        contexts_by_persona: dict, states_dir,
    ) -> bool:
        """Plan §1 Punkt 6: 'bei explizitem gueltigem Abschluss: private
        (Persona-)Reflexion bzw. freiwillige menschliche Notiz' — KEIN
        optionales Reportfeature (Plan §4: 'fehlende persoenliche
        Reflexionen sind aber KEINE optionale Reportauswertung'). Geht NICHT
        ueber `gm_transport` (privat, nie an die SL gesendet), wird lokal
        unter `reflections.jsonl` im `run_dir` abgelegt.

        F6/A4 (WEGKARTE §6, PLAN-CRITIC-DURCHSTICH.md WICHTIG): Mensch vs.
        KI wird ueber `ParticipantDecision.origin_source` unterschieden
        (Konvention im gesamten Bausatz: `"human:..."`-Praefix fuer
        menschliche Treiber, s. `ui/tui.py:_HumanDriver`). Fuer Menschen
        bleibt die Reflexion FREIWILLIG (Ablehnung/leere Notiz/Ausstieg
        blockiert nichts). Fuer KI-Personas ist der Reflexionsturn
        VORGESEHEN (Pflicht) -- ein Fehler oder eine leere Antwort wird NICHT
        stillschweigend uebergangen, sondern als `status=pending_recovery`-
        Eintrag im Archiv abgelegt (offener Zustand/Recovery statt
        Verschlucken). Der Reflexionskontext traegt zusaetzlich den eigenen
        Systemkontext (`own_context`) UND die aktuelle oeffentliche
        Tischsicht (`table_view`) -- vorher bekam die Reflexion nur einen
        Sentinel-Text, weder eigenen State noch Verlauf (Test 12).

        D4/A1 (K9, WEGKARTE §6, Test 09): das Admission-Gate gilt jetzt auch
        JE Reflexion -- ein Stop, der WAEHREND einer frueheren Reflexion
        desselben Abschlusses gesetzt wird, verhindert die NAECHSTE (kein
        separates Request-Gate nur fuer Spiel-/GM-Turns). D5/A3 (WEGKARTE §6
        BLOCKER, Test 10): Rueckgabewert `True` nur, wenn ALLE KI-Pflicht-
        reflexionen erfolgreich waren (Menschen bleiben freiwillig, zaehlen
        nie als Fehlschlag) -- der Aufrufer (`finalize`) darf den Abschnitt
        NUR bei `True` final schliessen (Lock-Release/`__final`/`closed`).

        End-Critic-Nacharbeit (WICHTIG, WEGKARTE §6): ein Retry nach
        partiellem Reflexionsfehler (Admission-Gate/Fehler/leere Antwort fuer
        EIN Mitglied haelt `finalize` offen, s. o.) darf Mitglieder, die in
        einem FRUEHEREN Aufruf bereits erfolgreich reflektiert haben, nicht
        erneut anfragen (unnoetiger Request, doppelter `pending_reflections`-
        Eintrag). Vor dem eigentlichen Turn wird darum `reflections.jsonl`
        auf einen bereits vorhandenen `kind=ai_required_reflection`-Eintrag
        fuer `(pk, section_id)` geprueft."""
        ok = True
        path = self.lobby.run_dir / "reflections.jsonl"
        already_reflected: set[str] = set()
        # A4/R08-Restintegrationsfix (WEGKARTE §7 A4, REVIEW-P2R.md R-D):
        # zusaetzlich zum bereits COMMITTETEN Dedup (`already_reflected`,
        # `kind=ai_required_reflection`) wird ein "empfangen, aber lokal
        # noch nicht committed"-Ledger gefuehrt (`kind=ai_reflection_
        # received`). Ein Retry nach einem Statewrite-Fehler prueft DIESES
        # Ledger VOR jedem erneuten Modellaufruf und verwendet die bereits
        # erhaltene Antwort direkt fuer den State-Write-Retry -- kein
        # zweiter Persona-Request, keine zweite Rundenzaehlung (Test 08:
        # `retry_persona_requests == 0`, `final_reflection == erste
        # Antwort`). received != published bleibt dadurch strukturell
        # getrennt (zwei verschiedene `kind`-Werte im selben Archiv).
        received_by_pk: dict[str, dict] = {}
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if entry.get("section_id") != section_id:
                    continue
                if entry.get("kind") == "ai_required_reflection":
                    already_reflected.add(entry.get("persona_key"))
                elif entry.get("kind") == "ai_reflection_received":
                    received_by_pk[entry.get("persona_key")] = entry
        for pk in self.table.members:
            if pk in already_reflected:
                continue
            pending_received = received_by_pk.get(pk)
            if pending_received is not None:
                # A4: bereits erhaltene Rohantwort wiederverwenden -- KEIN
                # erneuter Gate-Check/Modellaufruf fuer diesen Turn.
                origin_source = pending_received.get("origin_source") or ""
                is_human = origin_source.startswith("human:")
                text = (pending_received.get("text") or "").strip()
            else:
                base_ctx = contexts_by_persona.get(pk, {})
                ctx = {
                    "system": "PRIVATE_REFLECTION_SENTINEL",
                    "user": (
                        "Private Reflexion (optional fuer Menschen, vorgesehener "
                        "Pflicht-Reflexionsturn fuer KI-Personas -- wird NICHT an "
                        "die SL gesendet): Was nimmst du aus diesem Abschnitt mit?"
                    ),
                    "own_context": base_ctx.get("system", ""),
                    "table_view": store.persona_view(self.table, pk),
                }
                try:
                    # I2-Nachzug: derselbe reservierte+persistierte
                    # Requestweg wie jede andere Rolle (Auflage 6), s.
                    # `_admitted_decision`.
                    record = self._admitted_decision("reflection", controller, pk, ctx, section_id=section_id)
                except _GateBlocked as e:
                    ok = False
                    with path.open("a", encoding="utf-8") as fh:
                        fh.write(json.dumps({
                            "persona_key": pk, "section_id": section_id, "ts": ts,
                            "status": "pending_recovery",
                            "error": f"Admission-Gate blockiert: {e.reason}",
                        }, ensure_ascii=False) + "\n")
                    continue
                except Exception as exc:
                    ok = False
                    with path.open("a", encoding="utf-8") as fh:
                        fh.write(json.dumps({
                            "persona_key": pk, "section_id": section_id, "ts": ts,
                            "status": "pending_recovery", "error": str(exc),
                        }, ensure_ascii=False) + "\n")
                    continue
                origin_source = record.decision.origin_source or ""
                is_human = origin_source.startswith("human:")
                text = (record.decision.text or "").strip()
                if not is_human and text:
                    # A4: Rohbeleg SOFORT persistieren -- VOR dem lokalen
                    # Statewrite-Versuch, der als naechstes scheitern kann.
                    with path.open("a", encoding="utf-8") as fh:
                        fh.write(json.dumps({
                            "persona_key": pk, "section_id": section_id, "ts": ts, "text": text,
                            "origin_source": origin_source, "kind": "ai_reflection_received",
                        }, ensure_ascii=False) + "\n")
            if not text:
                if is_human:
                    continue  # freiwillige Notiz nicht abgegeben -- kein Fehler.
                ok = False
                with path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps({
                        "persona_key": pk, "section_id": section_id, "ts": ts,
                        "status": "pending_recovery",
                        "error": "KI-Pflichtreflexion leer zurueckgegeben.",
                    }, ensure_ascii=False) + "\n")
                continue
            if is_human:
                with path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps({
                        "persona_key": pk, "section_id": section_id, "ts": ts, "text": text,
                        "origin_source": origin_source, "kind": "human_note",
                    }, ensure_ascii=False) + "\n")
                continue
            # A2/D5 (WEGKARTE §8, Plan-Critic A2, Test 08): Archiv-Eintrag
            # `kind=ai_required_reflection` (der `already_reflected`-Dedup
            # oben ihn als Erledigungsnachweis liest) wird ERST NACH
            # erfolgreichem Pflicht-Statewrite geschrieben -- Archiv !=
            # Statecommit. Ein Statewrite-Fehler (Schema-Ablehnung, OSError,
            # ...) setzt `ok=False` und schreibt stattdessen einen
            # `pending_recovery`-Eintrag; er wird NICHT stillschweigend
            # verschluckt (kein Catch-all-`pass` mehr).
            try:
                state = self.persona_state_store.load_state(pk, states_dir=states_dir)
            except FileNotFoundError as exc:
                ok = False
                with path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps({
                        "persona_key": pk, "section_id": section_id, "ts": ts,
                        "status": "pending_recovery",
                        "error": f"Persona-State fuer Pflichtreflexion nicht gefunden: {exc}",
                    }, ensure_ascii=False) + "\n")
                continue
            pending_list = state.setdefault("pending_reflections", [])
            # W3-Fix (F..., Test 06 review_p2w_boundaries.py): idempotent
            # im PUBLIZIERTEN State selbst dedupliziert -- ein Retry nach
            # einem Statewrite, der ERFOLGREICH war, bevor der (getrennte)
            # `ai_required_reflection`-Archivbeleg unten geschrieben werden
            # konnte (z.B. Prozessabbruch dazwischen), laedt beim naechsten
            # Aufruf denselben bereits committeten State erneut -- ohne
            # diesen Check wuerde derselbe Commitauftrag (section_id, hier
            # sogar dieselbe Received-Antwort) ein ZWEITES Mal angehaengt.
            # Dedup-Schluessel ist `section_id` (ein Commitauftrag = eine
            # Pflichtreflexion je Abschnitt und Persona), nicht der Text --
            # Wiederholung desselben Commitauftrags wird zum No-op fuer den
            # State-Write, der State bleibt aber gueltig/aktuell
            # (`last_reflection` wird unten immer gesetzt).
            already_in_state = any(
                isinstance(e, dict) and e.get("section_id") == section_id for e in pending_list
            )
            if not already_in_state:
                pending_list.append({"section_id": section_id, "text": text, "ts": ts})
            state["last_reflection"] = text
            try:
                self.persona_state_store.save_state(pk, state, states_dir=states_dir)
            except Exception as exc:
                ok = False
                with path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps({
                        "persona_key": pk, "section_id": section_id, "ts": ts,
                        "status": "pending_recovery",
                        "error": f"Pflicht-Statewrite fehlgeschlagen: {exc}",
                    }, ensure_ascii=False) + "\n")
                continue
            # F6: KI-Reflexion fliesst in den gueltigen State-Verbund UND
            # (ueber `last_reflection`/`pending_reflections`) in den
            # NAECHSTEN Persona-Input ein -- Archivbeleg erst jetzt, nach
            # gesichertem Commit.
            with path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps({
                    "persona_key": pk, "section_id": section_id, "ts": ts, "text": text,
                    "origin_source": origin_source, "kind": "ai_required_reflection",
                }, ensure_ascii=False) + "\n")
        # A3/D5 (WEGKARTE §8, Plan-Critic A3, Test 09): expliziter DRITTER
        # Gate-Check NACH der letzten (erfolgreichen) Reflexionsantwort,
        # VOR der Rueckgabe an `finalize()` -- ein Stop, der WAEHREND der
        # einzigen/letzten Reflexion gesetzt wird (kein weiterer
        # Schleifendurchlauf mehr faellig), darf `finalize_section_after_
        # reflection` trotzdem nicht mehr erreichen. Die bereits erhaltene
        # Antwort bleibt im Archiv erhalten (oben bereits geschrieben);
        # nur die endgueltige Finalisierung wird verhindert.
        try:
            self._check_gate()
        except _GateBlocked as e:
            ok = False
            with path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps({
                    "persona_key": None, "section_id": section_id, "ts": ts,
                    "status": "pending_recovery",
                    "error": f"Admission-Gate blockiert nach letzter Reflexion: {e.reason}",
                }, ensure_ascii=False) + "\n")
        return ok

    def submit(
        self, controller: TableController, actor_persona_key: str, text: str, ts: str,
        origin_persona_key: str | None = None, origin_source: str | None = None,
        save_payload: dict | None = None, reserved_usd: float | None = None,
    ) -> dict:
        """Fuehrt EINEN Turn aus. `actor_persona_key` muss der Leader sein
        (durchgereicht an `store.submit_to_sl`, das die Leader-only-Pruefung
        haelt — keine Duplizierung der Regel hier).

        I2-Nachzug (Auflage 1/F2/F3, Test 06): `reserved_usd` -- vom
        Aufrufer AUS DEM TATSAECHLICH zu sendenden `text` berechnet (s.
        `admission.reservation_for_wire_text`, `act()`) -- wird VOR dem
        GM-Request persistiert+committet (`core.request_ledger.begin`,
        Case 05: kein Verbuchen erst NACH der Antwort mehr). Der GM-Turn ist
        damit derselbe Requestweg wie jede andere Rolle."""
        request_id = request_ledger.begin(
            self.lobby.run_dir, role="gm_turn", content=text, reserved_usd=reserved_usd,
            table_id=self.table.table_id, section_id=self._current_section_id,
        )
        t0 = time.monotonic()
        try:
            result = store.submit_to_sl(
                self.table, actor_persona_key, self.gm_transport, self._turn_idx, text,
                origin_persona_key=origin_persona_key, origin_source=origin_source,
                save_payload=save_payload,
            )
        except Exception as exc:
            request_ledger.finish_error(self.lobby.run_dir, request_id, error=exc, seconds=time.monotonic() - t0)
            raise
        # A9/D4 (WEGKARTE §8, Plan-Critic A9): echte/synthetische USD aus
        # `result["usage"]` (GM-Transport-Vertrag) fliesst als Audit-Beleg in
        # den Requestdatensatz ein -- `turns_used`/`usd_spent` wurden bereits
        # in `begin()` committet (kein Doppel-Anrechnen, Auflage 6).
        request_ledger.finish_received(
            self.lobby.run_dir, request_id, usage=result.get("usage"), seconds=time.monotonic() - t0,
        )
        self._emit("sl_turn", ts, actor=actor_persona_key, payload={
            "turn_idx": self._turn_idx,
            "origin_source": origin_source,
            "origin_persona_key": origin_persona_key if origin_persona_key is not None else actor_persona_key,
            "table_id": self.table.table_id,
            "section_id": self._current_section_id,
            "chat_id": result.get("chat_id"),
            "save_payload_present": save_payload is not None,
            # A13 (WEGKARTE §8, 02 §9/01 §M4): unveraenderter SL-Antworttext
            # als Rohbeleg fuer die lokale Berichtsauswertung (Ausruestung/
            # Boss/Kampf/Drift-Provenienz, s. reports/report.py) -- derselbe
            # Text, der bereits im Tisch-`sl_log` steht, wird zusaetzlich im
            # Eventlog referenzierbar (kein zweiter Datenpfad, kein Modell-
            # urteil hier).
            "content": result.get("content", ""),
        })
        self._turn_idx += 1
        return result

    def run_full_section(
        self, controller: TableController, section_id: str,
        contexts_by_persona: dict[str, dict], states_dir, today: str, ts: str,
        max_turns: int | None = None,
    ) -> SectionOutcome:
        """Voller Ablauf: Leader-Anker -> Gaeste einzeln (Import) -> WEITERE
        echte Spiel-/Abspracheturns (Leader-getragen, da nur der Leader an
        die SL sendet) -> Marker-Pruefung NACH JEDEM Turn -> Ernte ->
        `complete_section` -> Rueckkehr in Lobby.

        `contexts_by_persona` liefert je Mitglied den STARTKONTEXT; jeder
        weitere Turn erhaelt zusaetzlich die aktuell erlaubte Tischsicht
        (`store.persona_view`, inkl. der zuletzt empfangenen SL-Antwort) —
        das schliesst I1s "SL-Reply nicht rueckgefuehrt"-Befund.

        Szene ohne Abschluss-Marker = laufendes Spiel: die Schleife laeuft
        weiter bis Marker, Admission-Block oder `max_turns` (Default
        `DEFAULT_MAX_TURNS`, strukturelle Sicherheitsgrenze, I1/A2).

        `today` OHNE Default (A5): der Aufrufer MUSS das reale Tagesdatum
        angeben.

        F3 (K6/K8, WEGKARTE §6 A1): das Admission-Gate wird jetzt an DREI
        Punkten frisch von der Platte geprueft -- (1) vor jedem Persona-
        Request, (2) ZWISCHEN Persona-Request und GM-Request (ein Stop, der
        WAEHREND der Persona-Entscheidung gesetzt wird, verhindert den
        GM-Request derselben Runde, Test 05), (3) NACH dem GM-Request, VOR
        Marker-Pruefung/Publish/Reflexion (ein Stop, der WAEHREND des
        GM-Turns selbst gesetzt wird, verhindert Abschluss/Reflexion fuer
        diese Antwort -- der Rohbeleg im `sl_log` bleibt erhalten, Test 06).
        Alle drei Pruefpunkte werfen `_GateBlocked`, hier zentral gefangen.

        F2 (K5, WEGKARTE §6 A3): ab der ZWEITEN Runde der laufenden
        Spiel-/Abspracheturns (nicht der allerersten, die dem Import direkt
        folgt) werden Gaeste vor dem naechsten Leader-Turn ueber denselben
        `ParticipantDriver`-Vertrag befragt (`_poll_guests_and_consolidate`);
        ihre Antworten gehen ueber `store.post_table_message` in den Tisch
        UND werden -- konsolidiert durch den Leader -- in den naechsten an
        die SL gesendeten Wire-Text eingebettet (Leader-only-Konsolidierung,
        kein Re-Poll-Stub)."""
        max_turns = DEFAULT_MAX_TURNS if max_turns is None else max_turns
        leader = self.table.leader
        self._current_section_id = section_id
        debrief_text = ""
        turns_taken = 0

        def blocked_outcome(reason: str | None) -> SectionOutcome:
            completion = store.CompletionResult(
                success=False, already_completed=False, written=False,
                members_completed=[], missing=[],
                reason=f"Admission-Gate blockiert: {reason}",
            )
            self._emit("play_paused", ts, payload={"section_id": section_id, "reason": reason})
            return SectionOutcome(completion=completion, harvested={}, debrief_text=debrief_text)

        def finalize(text: str, resume_section_id: str | None = None) -> SectionOutcome:
            sid = resume_section_id if resume_section_id is not None else section_id
            cid_to_pk = self.table.chrononaut_id_to_persona()
            harvested = self.harvest_extractor(text, cid_to_pk) if text else {}
            # A3/D5 (PLAN-CRITIC-ABSCHLUSS.md BLOCKER, WEGKARTE §6, Test
            # 10): `complete_section` erledigt jetzt NUR NOCH PHASE 1
            # (Saves/States ernten, idempotent gepinnt) -- der endgueltige
            # Abschluss (Lock-Release/`__final`/`closed`, PHASE 2) erfolgt
            # ERST NACH erfolgreicher Pflicht-KI-Reflexion. Eine
            # fehlgeschlagene Pflicht-Reflexion haelt den Abschnitt
            # offen/wiederaufnehmbar -- die bereits geerntete Save-/
            # State-Ernte bleibt dabei gueltig (kein Doppelspiel bei einem
            # spaeteren Retry, A08 unveraendert). Bei `resume_section_id`
            # (A1/D5, Test 07) ist bereits ein `__plan.json` gepinnt --
            # `complete_section` nimmt dann den idempotenten Resume-Zweig
            # und ignoriert `harvested` (leer, da kein neuer GM-Turn noetig).
            harvest_completion = store.complete_section(
                self.lobby, self.table, sid, harvested, states_dir, today,
                self.harvest_validator, self.persona_state_store,
            )
            if not harvest_completion.success:
                self._emit("section_completion_rejected", ts, payload={"section_id": sid, "reason": harvest_completion.reason})
                return SectionOutcome(completion=harvest_completion, harvested=harvested, debrief_text=text)

            store.return_to_lobby(self.lobby, self.table)
            reflections_ok = self._collect_reflections(controller, sid, ts, contexts_by_persona, states_dir)
            if reflections_ok:
                completion = store.finalize_section_after_reflection(self.lobby, self.table, sid)
                self._emit("section_completed", ts, payload={"section_id": sid, "members": completion.members_completed})
            else:
                completion = store.CompletionResult(
                    success=False, already_completed=False, written=harvest_completion.written,
                    members_completed=harvest_completion.members_completed, missing=[],
                    reason=(
                        "Saves/States wurden geerntet, aber mindestens eine Pflicht-KI-Reflexion "
                        "ist fehlgeschlagen — Abschnitt bleibt offen/wiederaufnehmbar (kein "
                        "endgueltiger Abschluss, kein Lock-Release, kein Doppelspiel bei Recovery)."
                    ),
                )
                self._emit("section_completion_rejected", ts, payload={"section_id": sid, "reason": completion.reason})
            return SectionOutcome(completion=completion, harvested=harvested, debrief_text=text)

        def marker_hit(text: str) -> bool:
            return completion_marker_matches(text, self.marker, self.table.table_id, section_id)

        def act(pk: str, base_context: dict, attach_import_save: bool = False) -> None:
            nonlocal debrief_text, turns_taken
            ctx = dict(base_context)
            ctx["table_view"] = store.persona_view(self.table, pk)
            if pk == leader:
                # D2/K6 (WEGKARTE §6 A4, Test 11): der Leader bekommt eine
                # noch nicht konsolidierte private Tischabsprache VOR seiner
                # Entscheidung SICHTBAR gemacht (s. `ui/tui.py:_HumanDriver.
                # decide`) -- die Runtime haengt sie aber NICHT MEHR
                # automatisch an die vom Leader frei gewaehlte Antwort an
                # (das war der BLOCKER: 'Gastvorschlag ungefragt an
                # freigegebenen Leadertext angehaengt').
                pending_messages = self.table.table_messages[self._consolidated_message_count:]
                if pending_messages:
                    ctx["pending_table_messages"] = pending_messages
            # I2-Nachzug (Case 05, Auflage 6): reserviert+committet+
            # persistiert VOR dem Persona-Request (`_admitted_decision`,
            # anfragebezogen aus Input UND Output wie zuvor -- Treiber ohne
            # erkennbare Obergrenze/Human-Driver behandelt fair, s.
            # `reservation_for_request`s `output_bound_known`). Der
            # KONKRETE, bereits fertig gebaute `ctx` (inkl. table_view/
            # pending_table_messages) wird verwendet -- dieselbe Textmenge,
            # die tatsaechlich zum Empfaenger geht.
            record = self._admitted_decision("persona_decision", controller, pk, ctx)
            self._check_gate()  # F3: zwischen Persona-Request und GM-Request.
            wire_text = record.decision.text
            save_payload = record.decision.save_payload
            if save_payload is None and attach_import_save:
                # D3/A7 (K7, WEGKARTE §6): deterministische Save-Bindung
                # durch die Runtime -- ein echter Provider (API/CLI) liefert
                # NIE von sich aus einen `save_payload` (nur `_HumanDriver`
                # tut das); der eigene v7-Save des Teilnehmers wird bei
                # dessen Anker-/Importturn trotzdem real an den Wire
                # gebunden, aus dem vom Aufrufer uebergebenen Kontext
                # (`import_save_payload`), NICHT vom Modell erzeugt/
                # abgeschrieben.
                save_payload = base_context.get("import_save_payload")
            if save_payload is not None:
                wire_text = _embed_json_block(wire_text, save_payload)
            # I2 (Case 06, Auflage 1/F2/F3): GM-Reservierung AUS DEM
            # TATSAECHLICH zu sendenden `wire_text` (inkl. Save-/Hhistory-
            # Huelle) -- NICHT der starren Pauschale -- unmittelbar VOR dem
            # GM-Versand geprueft. Ein grosser konsolidierter Wire-Text darf
            # das Gesamtbudget nicht unterlaufen (Test 06).
            gm_reserved = reservation_for_wire_text(wire_text)
            self._check_gate(gm_reserved)  # F3/Q06: GM-Body-Reservierung vor Versand.
            result = self.submit(
                controller, leader, wire_text, ts,
                origin_persona_key=pk, origin_source=record.decision.origin_source,
                save_payload=save_payload, reserved_usd=gm_reserved,
            )
            if pk == leader:
                self._consolidated_message_count = len(self.table.table_messages)
            turns_taken += 1
            debrief_text = result["content"]

        def poll_guests_and_consolidate() -> None:
            """F2 (K5, WEGKARTE §6 A3): Gaeste werden ueber denselben
            `ParticipantDriver`-Vertrag befragt wie beim Import -- ihre
            Antwort geht als private Tischnachricht (`post_table_message`)
            in den Tisch, NICHT direkt an die SL (nur der Leader sendet,
            `act()` konsolidiert vor dem naechsten Leader-Turn)."""
            for pk in [m for m in self.table.members if m != leader]:
                base_ctx = contexts_by_persona.get(pk, {})
                ctx = dict(base_ctx)
                ctx["table_view"] = store.persona_view(self.table, pk)
                # I2-Nachzug: derselbe reservierte+persistierte Requestweg
                # wie jede andere Rolle (Auflage 6), s. `_admitted_decision`.
                record = self._admitted_decision("guest_poll", controller, pk, ctx)
                self._check_gate()
                text = (record.decision.text or "").strip()
                if text:
                    store.post_table_message(self.table, pk, text)

        # A1/D5 (WEGKARTE §8, Plan-Critic A1, Test 07): existiert fuer diesen
        # Tisch bereits ein offener Abschluss-Auftrag (`__plan.json` ohne
        # `__final.json` -- z.B. weil ein frueherer Prozess nach dem
        # GM-Abschlussturn, aber vor erfolgreicher Pflicht-Reflexion
        # abgebrochen ist), ist das KEIN normaler Spielzug mehr. Nur der
        # fehlende Abschlussschritt (idempotente Ernte + Reflexion +
        # Finalisierung) wird fortgesetzt -- OHNE GM-Replay/neuen
        # Spielzug (kein `TablePendingError` aus `store.submit_to_sl`).
        open_section_id = store.open_completion_order_for_table(self.lobby.run_dir, self.table.table_id)
        if open_section_id is not None:
            return finalize("", resume_section_id=open_section_id)

        try:
            # Leader-Anker -- nur, wenn dieser Tisch (Resume, A8) noch keinen
            # Anker-Turn hat.
            if not self._leader_anchored:
                act(leader, contexts_by_persona[leader], attach_import_save=True)
                self._check_gate()  # F3: vor Publish/Reflexion.
                if marker_hit(debrief_text):
                    return finalize(debrief_text)

            # Gaeste einzeln (Import) -- nur die, die noch nicht importiert haben.
            for pk in [m for m in self.table.members if m != leader]:
                if pk in self._guests_imported:
                    continue
                act(pk, contexts_by_persona[pk], attach_import_save=True)
                self._check_gate()  # F3: vor Publish/Reflexion.
                if marker_hit(debrief_text):
                    return finalize(debrief_text)

            # Weitere echte Spiel-/Abspracheturns, bis Marker/Admission-Block/max_turns.
            debrief_ctx = contexts_by_persona.get(f"{leader}__debrief", contexts_by_persona[leader])
            ongoing_round = 0
            while turns_taken < max_turns:
                if ongoing_round > 0:
                    poll_guests_and_consolidate()
                act(leader, debrief_ctx)
                self._check_gate()  # F3: vor Publish/Reflexion.
                if marker_hit(debrief_text):
                    return finalize(debrief_text)
                ongoing_round += 1
        except _GateBlocked as e:
            return blocked_outcome(e.reason)

        completion = store.CompletionResult(
            success=False, already_completed=False, written=False,
            members_completed=[], missing=[],
            reason=(
                f"max_turns ({max_turns}) erreicht ohne Abschluss-Marker — Szene bleibt "
                f"offen (kein Fixture-Abbruch, laeuft ggf. in einer Folgesitzung weiter)."
            ),
        )
        self._emit("section_completion_rejected", ts, payload={"section_id": section_id, "reason": completion.reason})
        return SectionOutcome(completion=completion, harvested={}, debrief_text=debrief_text)
