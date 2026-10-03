#!/usr/bin/env python3
"""
mmo_sim/domain/zeitriss/community_creation.py — persona-getriebene
Community-Erstgeneration bis zur spielbereiten Persona (P2-Community-Block
2026-09-25, 01_COMMUNITY_AUFTRAG.md §3 C/D/E, MAIN-DATENWEGENTSCHEIDUNG.md).

`community_bootstrap.bootstrap_community` legt nur den EINMALIG gepinnten
Plan + Profil-ENTWUERFE an (`v=2`-Persona-State, `plays_char=
{"...":"NOCH_NICHT_ERSCHAFFEN"}` — kein Current-Save, keine Chrononaut-ID,
NICHT spielbereit). Dieses Modul fuehrt JEDE geplante Persona durch ihren
EIGENEN, fortsetzbaren SL-Erschaffungsdialog — denselben Kern wie
`ui/tui.py:_cmd_new_or_switch_character` fuer einen Menschen
(`core/creation_service.run_admitted_creation_dialog`), nur dass die
Antworten NICHT von `_readline` kommen, sondern von einem echten
Persona-Treiber (`adapters/persona_api.py`/`persona_claude_code.py`, in
Tests durch markierte Fake-Doubles ersetzt) — eigene Chat-Identitaet
`onboarding-<persona_key>`, D3-konform getrennt vom Spielverlauf.

Requestvertrag (Datenwegentscheidung §2c/e): JEDER Modellschritt (Persona-
Antwort UND GM-Frage) laeuft ueber `read_admission_block`+
`reservation_for_*`+`request_ledger.begin`, gebunden an
`table_id=community_id, section_id=f"gen{generation}", role=<Phase>,
turn_idx, participant=persona_key` — `request_ledger._operation_identity`
(unveraendert) verhindert damit bereits strukturell eine zweite
Reservierung/Buchung fuer denselben noch offenen Schritt bei einem lokalen
Retry/Neustart, ohne dass dieses Modul selbst einen neuen Idempotenz-
Mechanismus bauen muss.

Fehler/Ablehnung/Blockade EINER Persona darf die uebrigen Mitglieder NICHT
anhalten (02_ABNAHME 'Fehler/Abbruch vor Save ... gueltige andere Mitglieder
erhalten') — `advance_community_creation` iteriert alle geplanten Personas
und sammelt je einen eigenen Outcome, statt beim ersten Fehlschlag
abzubrechen. Eine bereits `completed` Persona (I4-Current-Autoritaet: ein
gueltiger Current-Save existiert bereits) wird NICHT neu erschaffen/
ueberschrieben — `onboarding.start_or_resume` liefert fuer sie sofort den
bereits abgeschlossenen Auftrag zurueck, kein zweiter Modellaufruf."""
from __future__ import annotations

import inspect
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from ...adapters.base import creation_pause_control_instruction, interpret_creation_pause_control
from ...core import request_ledger
from ...core import store as core_store
from ...core.admission import read_admission_block, reservation_for_request
from ...core.creation_service import ReplyResult, run_admitted_creation_dialog
from ...core.persona_state import PersonaStateStore
from . import catalog, onboarding
from . import saves as zeitriss_saves
from .policy import ZeitrissHarvestValidator


@dataclass
class PersonaCreationOutcome:
    persona_key: str
    status: str  # "already_ready" | "completed" | "paused" | "error" | "blocked" | "no_driver"
    chrononaut_id: str | None = None
    reason: str = ""


def _initial_outgoing(draft_state: dict) -> str:
    """Erste Nachricht dieser Persona an die SL — nennt das eigene, bereits
    gepinnte Profil (Archetyp/Spielstil/Charakterwunsch aus dem Bootstrap-
    Entwurf), damit die SL denselben regulaeren Erschaffungsdialog wie bei
    einem Menschen fuehren kann, OHNE dass der Harness selbst eine
    Spielentscheidung formuliert (01 §3 C: 'Ihr Text wird transportiert,
    nicht vom Harness als Spielentscheidung formuliert' — hier gilt das
    umgekehrt fuer den Harness-Anstoss: nur das bereits vom Bootstrap
    gepinnte Profil wird zitiert, keine neue Charaktereigenschaft erfunden)."""
    archetype = draft_state.get("archetype", "")
    play_style = draft_state.get("play_style", "")
    charwunsch = draft_state.get("charwunsch", "")
    return (
        "Ich moechte einen neuen Chrononauten erschaffen. Fuehre mich Schritt fuer Schritt "
        f"durch die Erschaffung. Mein Spielerprofil: Archetyp={archetype!r}, "
        f"Spielstil={play_style!r}, Charakterwunsch={charwunsch!r}."
    )


def _own_persona_context(draft_state: dict, own_steps: list[dict]) -> str:
    """C3 (P2-Community-Kontinuitaet 2026-09-25, MAIN-DATENWEGENTSCHEIDUNG.md
    §3): der tatsaechliche Entscheider bekommt sein GEPINNTES Profil
    (Archetyp/Spielstil/Charakterwunsch aus dem Bootstrap-Entwurf) UND seine
    eigenen, tatsaechlich bereits empfangenen/beantworteten Dialogschritte --
    NICHT nur Key + letzte Frage (REVIEW-COMMUNITY.md §5). `own_steps` stammt
    AUSSCHLIESSLICH aus dem Onboarding-Auftrag DIESER Persona (der Aufrufer
    liest ihn ueber `onboarding.peek(onboarding_dir, persona_key)`) -- nie
    aus fremden Teilnehmerdaten, keine Entwickler-/Reviewanweisungen, keine
    erfundene Erinnerung (nur tatsaechlich gefuehrter eigener Dialog)."""
    archetype = draft_state.get("archetype", "")
    play_style = draft_state.get("play_style", "")
    charwunsch = draft_state.get("charwunsch", "")
    lines = [
        "Dein eigenes, bereits gepinntes Spielerprofil (nicht neu erfinden, "
        "konsistent bleiben):",
        f"  Archetyp: {archetype}",
        f"  Spielstil: {play_style}",
        f"  Charakterwunsch: {charwunsch}",
    ]
    if own_steps:
        lines.append("")
        lines.append(
            "Dein bisheriger eigener Erschaffungsdialog mit der Spielleitung "
            "(nur deine eigenen, bereits gegebenen Antworten):"
        )
        for step in own_steps:
            lines.append(f"  SL: {step.get('question', '')}")
            lines.append(f"  Du: {step.get('answer', '')}")
    return "\n".join(lines)


def _persona_get_reply_factory(
    *, run_dir: Path, persona_driver, community_id: str, generation: int,
    persona_key: str, draft_state: dict, onboarding_dir: Path,
    print_fn: Callable[[str], None],
    onboarding_participant_key: str | None = None,
) -> Callable[[int, str], ReplyResult]:
    # Gate-B-Ergaenzung (02_PERSONA_NEUER_CHRONONAUT.md, Zusatzfigur-
    # Einladungsweg, s. `advance_additional_persona_creation` unten):
    # `onboarding_participant_key` ist ausschliesslich die interne
    # Onboarding-/Requestledger-Buchhaltungskennung fuer DIESEN
    # Erschaffungsversuch -- Default `persona_key` (unveraendertes Verhalten
    # fuer `advance_one_persona_creation`, die reale Teilnehmeridentitaet
    # UND die Buchhaltungskennung sind dort identisch). Fuer eine
    # ZUSAETZLICHE Figur einer bereits spielenden Persona traegt sie eine
    # EIGENE, von der Persona-Hauptkennung getrennte Kennung (`gen<N>`-
    # Suffix) -- NUR fuer Onboarding-Scratch/Requestledger-Buchung, NIEMALS
    # fuer den tatsaechlichen, an den Modellprompt gehenden Personatext
    # (der bleibt unveraendert `persona_key`, s.u.) oder fuer Katalog-/
    # Current-/Persona-State-Autoritaet (die bleiben IMMER `persona_key`).
    onboarding_participant_key = onboarding_participant_key or persona_key
    persona_role = "community_creation_persona"
    section_id = f"gen{generation}"

    def _reply_for_text(text: str, request_id: str | None) -> ReplyResult:
        # C4 (P2-Community-Ergebnisuebergabe 2026-09-25, 01_AUFTRAG §3 C4,
        # 11 §8 "koennen auch ablehnen, pausieren oder andere Ziele
        # waehlen"): der echte Entscheider (Persona-Driver) signalisiert
        # eine bewusste Pause NUR ueber die exakte, strukturelle
        # Kontrollzeile (s. `adapters.base.interpret_creation_pause_control`)
        # -- keine Keywordliste, keine Umdeutung einer gewoehnlichen
        # Figurenantwort. Gilt identisch fuer einen frisch empfangenen UND
        # einen durabel wiederhergestellten Text (Idempotenz: derselbe
        # bereits abgerechnete Turn liefert bei jeder Wiederaufnahme
        # dasselbe Ergebnis, kein neuer Modellaufruf).
        if interpret_creation_pause_control(text):
            return ReplyResult(
                kind="paused",
                reason=(
                    f"Persona {persona_key!r} hat den Erschaffungsdialog bewusst pausiert "
                    "(struktureller Kontrollvertrag) -- Fortschritt bleibt erhalten."
                ),
                request_id=request_id,
            )
        return ReplyResult(kind="answer", text=text, request_id=request_id)

    def _get_reply(turn_idx: int, sl_text: str) -> ReplyResult:
        # C2 (P2-Community-Ergebnisuebergabe 2026-09-25,
        # MAIN-DATENWEGENTSCHEIDUNG.md §3): bevor irgendein neuer
        # Persona-Request reserviert/gesendet wird, ZUERST pruefen, ob fuer
        # GENAU DIESE Operationsidentitaet bereits eine Antwort dauerhaft
        # abgerechnet ist (der Aufrufer, `core.creation_service.run_
        # admitted_creation_dialog`, ruft `_get_reply` erneut auf, wenn der
        # lokale `onboarding.record_pending_answer`-Checkpoint-Write nach
        # einer bereits erhaltenen Antwort an einem gewoehnlichen `OSError`
        # gescheitert ist -- s. `request_ledger.find_durable_result`
        # Docstring). Kein Kontextaufbau, keine Reservierung, kein
        # Driver-Aufruf in diesem Fall -- die bereits empfangene Antwort
        # wird 1:1 wiederverwendet.
        recovered = request_ledger.find_durable_result(
            run_dir, table_id=community_id, section_id=section_id, role=persona_role,
            turn_idx=turn_idx, participant=onboarding_participant_key,
        )
        if recovered is not None:
            # R1 (Community-Recovery 2026-09-25, REVIEW-COMMUNITY-RECOVERY.md
            # §3): dieselbe Settlement-Pflicht wie auf der GM-Seite (s.
            # `core.creation_service.run_admitted_creation_dialog`) -- ein
            # `received`-Treffer wird GENAU EINMAL nachbebucht, BEVOR sein
            # Text als bereits erledigte Personaantwort weiterverwendet
            # wird. Ein Fehler propagiert ungefangen (kontrolliert offen).
            if recovered.get("state") == "received":
                recovered = request_ledger.settle_received(run_dir, recovered)
                # A1 (Altformat-Recovery-Nachzug 2026-09-25,
                # MAIN-DATENWEGENTSCHEIDUNG.md A1): `settle_received`
                # transitioniert NICHT nach `accounted`, wenn die
                # Originaldauer unbekannt ist (Schluessel `received_seconds`
                # abwesend, Altrecord vor R1). Kein `completed`/
                # `already_ready`, kein abhaengiger Modellaufruf -- die
                # Persona-Antwort bleibt kontrolliert offen.
                if recovered.get("state") != "accounted":
                    return ReplyResult(
                        kind="paused",
                        reason=(
                            f"Persona {persona_key!r}: Originaldauer der bereits empfangenen "
                            "Antwort unbekannt (Altformat-Recovery) -- kein weiterer "
                            "Modellaufruf, Fortschritt bleibt erhalten."
                        ),
                        request_id=recovered.get("id"),
                    )
            recovered_text = recovered["result_text"]
            # R4 (Community-Recovery 2026-09-25, REVIEW-COMMUNITY-RECOVERY.md
            # §6): eine bereits durabel abgerechnete STRUKTURELLE
            # Pause-Kontrollzeile ist KEIN wiederverwendbarer Antworttext --
            # der reale Pause-Request hat gekostet (Record bleibt fuer die
            # Buchung erhalten, s.o.), wird aber nicht erneut als Antwort
            # ausgespielt. Ein ausdruecklich veranlasster spaeterer
            # Wiederaufnahmeversuch (dieser Aufruf von `_get_reply` fuer
            # GENAU DIESEN `turn_idx`) faellt stattdessen unten durch und
            # erhaelt GENAU EINEN neuen Entscheidungsversuch -- keine alte
            # GM-Frage wird dafuer erneut gesendet (sie stammt bereits aus
            # dem wiederverwendeten `sl_text`-Argument), kein Keywordveto,
            # keine automatische Aufhebung der urspruenglichen Pause.
            if not interpret_creation_pause_control(recovered_text):
                print_fn(
                    f"[{persona_key}] {recovered_text} (durabel aus dem Requestledger "
                    "wiederhergestellt -- lokaler Checkpoint-Write war zuvor fehlgeschlagen, "
                    "kein erneuter Persona-Request)"
                )
                return _reply_for_text(recovered_text, recovered["id"])
            print_fn(
                f"[{persona_key}] vorheriger Versuch fuer diesen Schritt war eine bewusste "
                "Pause (Kontrollzeile, bereits durabel abgerechnet) -- ausdrueckliche "
                "Fortsetzung erhaelt jetzt einen neuen Entscheidungsversuch, keine "
                "Wiederholung der alten Pause."
            )
        # A2 (Altformat-Recovery-Nachzug 2026-09-25, MAIN-DATENWEGENTSCHEIDUNG.md
        # A2): `find_durable_result` fand oben entweder gar keinen Treffer
        # oder nur einen bereits durabel abgerechneten strukturellen
        # Pause-Text (fallthrough). In BEIDEN Faellen kann trotzdem ein
        # Alt-Record fuer GENAU DIESE Operationsidentitaet existieren, der
        # bereits erfolgreich gesendet+verbucht wurde, aber nie einen Text
        # persistiert hat (10024452-Stand) -- ohne diesen Check wuerde eine
        # bereits beantwortete Operation blind ein zweites Mal angefragt.
        answered_without_text = request_ledger.find_answered_without_text(
            run_dir, table_id=community_id, section_id=section_id, role=persona_role,
            turn_idx=turn_idx, participant=onboarding_participant_key,
        )
        if answered_without_text is not None:
            return ReplyResult(
                kind="paused",
                reason=(
                    f"Persona {persona_key!r}: bereits gesendete/verbuchte Anfrage ohne "
                    "erhaltenen Text (Altformat-Recovery) -- keine neue Anfrage, Fortschritt "
                    "bleibt erhalten."
                ),
                request_id=answered_without_text.get("id"),
            )
        # C3: der identische, gepruefte Kontext (Profil + eigene bisherige
        # Antworten aus dem bereits persistierten Onboarding-Auftrag DIESER
        # Persona) bestimmt sowohl die Inputreservierung (unten,
        # `reservation_for_request` misst `own_context` bereits mit) als
        # auch den tatsaechlichen Wire an den Persona-Empfaenger
        # (`adapters.base.render_public_wire_text` serialisiert
        # `ctx["own_context"]` zusaetzlich in den realen HTTP-/CLI-Body).
        own_state = onboarding.peek(onboarding_dir, onboarding_participant_key)
        own_steps = own_state.steps if own_state is not None else []
        # Gate-B-Ergaenzung: eine ZUSAETZLICHE Figur (onboarding_participant_key
        # != persona_key) wird dem Modell EHRLICH als weitere, nicht als
        # "erste" Erschaffung angekuendigt (02 'keine erfundene Zustimmung,
        # kein verdeckter Ersatz') -- der eigentliche Personatext/own_context
        # bleibt unveraendert an die REALE `persona_key`-Identitaet gebunden.
        ordinal_hint = "ersten" if onboarding_participant_key == persona_key else "ZUSAETZLICHEN"
        ctx = {
            "system": (
                f"Du bist die Spieler-Persona '{persona_key}' der Community '{community_id}' "
                f"(Generation {generation}). Du erschaffst gerade deinen eigenen {ordinal_hint} "
                "Chrononauten in einem eigenen, privaten SL-Dialog -- beantworte die Fragen "
                "der Spielleitung in deiner eigenen Stimme, konsistent zu deinem Profil.\n\n"
                f"{creation_pause_control_instruction()}"
            ),
            "user": sl_text,
            "own_context": _own_persona_context(draft_state, own_steps),
        }
        # I2/W2 (wie jeder andere Persona-Request): anfragebezogene
        # Reservierung AUS Input+Output, nicht die starre Pauschale.
        reserved_usd, output_bound_known = reservation_for_request(persona_driver, ctx)
        route = getattr(getattr(persona_driver, "config", None), "base_url", None)
        blocked, reason = read_admission_block(
            run_dir, reserved_usd=reserved_usd, output_bound_known=output_bound_known, route=route,
        )
        if blocked:
            return ReplyResult(kind="paused", reason=str(reason))
        request_id = request_ledger.begin(
            run_dir, role=persona_role, content=sl_text,
            reserved_usd=reserved_usd, route=route,
            output_limit_tokens=getattr(getattr(persona_driver, "config", None), "max_tokens", None),
            table_id=community_id, section_id=section_id,
            turn_idx=turn_idx, participant=onboarding_participant_key,
        )
        t0 = time.monotonic()
        try:
            decision = persona_driver.decide(ctx)
        except Exception as e:
            request_ledger.finish_error(run_dir, request_id, error=e, seconds=time.monotonic() - t0)
            return ReplyResult(kind="error", reason=str(e))
        # C2: der empfangene Text wird BEREITS HIER (im selben atomaren
        # Requestledger-Write, der `state=accounted` setzt) dauerhaft an
        # diese Operationsidentitaet gebunden -- BEVOR der separate lokale
        # Checkpoint-Write (`onboarding.record_pending_answer`, im Aufrufer)
        # versucht wird und ggf. fehlschlaegt.
        request_ledger.finish_received(
            run_dir, request_id, usage=(decision.meta or {}).get("usage"), seconds=time.monotonic() - t0,
            result_text=decision.text,
        )
        print_fn(f"[{persona_key}] {decision.text}")
        return _reply_for_text(decision.text, request_id)

    return _get_reply


def _publication_reconcile(
    *,
    run_dir: Path,
    states_dir: Path,
    onboarding_dir: Path,
    catalog_dir: Path,
    persona_key: str,
    final_save: dict,
    ps_store: PersonaStateStore,
) -> PersonaCreationOutcome:
    """C1 (P2-Community-Kontinuitaet 2026-09-25, MAIN-DATENWEGENTSCHEIDUNG.md
    §3, REVIEW-COMMUNITY.md §3): `onboarding.completed`/`final_save` allein
    ist KEIN Readybeleg (W1). Bereitschaft = I4-Current-Autoritaet
    (`load_current_save_or_raise`) UND Katalogeintrag UND Figurablage UND
    Persona-State-Identitaet UND aktive Bindung -- zusammen, nicht nur der
    Onboarding-Status. Fehlt eine dieser Publikationswirkungen trotz
    bereits erhaltenem validiertem `final_save`, wird sie HIER wiederholsicher
    nachgeholt -- OHNE neuen Modellaufruf (dieselben Primitiven wie der
    menschliche Pfad in `ui/tui.py:_cmd_new_or_switch_character`, kein
    zweiter Store). Ein Fehler beim STRENGEN Current-Lesen (`Current
    SaveUnavailableError`) ist unklar (blockiert), NIE 'fehlt/neu
    veroeffentlichen'. Ein bereits vorhandener (auch neuerer) Current wird
    NIE mit dem alten `final_save` ueberschrieben -- `publish_current_save`
    wird ausschliesslich aufgerufen, wenn (noch) GAR KEIN Current existiert
    (02_ABNAHME 'Neuere gueltige Fassung ... kein unnoetiger zweiter
    Publisherwrite'). Ist bereits ALLES vorhanden (Reentry nach gesunder
    Fertigstellung), werden GAR KEINE Schreibvorgaenge ausgefuehrt
    (savebyte-stabil, requestfrei)."""
    try:
        current = core_store.load_current_save_or_raise(run_dir, persona_key, ps_store, states_dir)
    except core_store.CurrentSaveUnavailableError as e:
        return PersonaCreationOutcome(
            persona_key, "blocked",
            reason=(
                "Current-Save-Autoritaet gerade nicht strengt lesbar -- unklar, keine "
                f"Publikation/Readymeldung ohne geklaerten Stand: {e}"
            ),
        )
    if current is not None:
        chrononaut_id = zeitriss_saves.block_char_id(current) or zeitriss_saves.block_char_id(final_save)
    else:
        chrononaut_id = zeitriss_saves.block_char_id(final_save)
    if chrononaut_id is None:
        return PersonaCreationOutcome(
            persona_key, "blocked",
            reason="abgeschlossener Onboarding-Auftrag ohne auswertbare Chrononaut-ID im final_save.",
        )

    catalog_entries = catalog.list_for_participant(catalog_dir, persona_key)
    has_catalog_entry = any(e.chrononaut_id == chrononaut_id for e in catalog_entries)
    has_figure_save = catalog.load_figure_save(catalog_dir, persona_key, chrononaut_id) is not None
    try:
        persona_state = ps_store.load_state(persona_key, states_dir=states_dir)
        has_persona_state = (
            persona_state.get("persona_key") == persona_key
            and (persona_state.get("plays_char") or {}).get("character_id") == chrononaut_id
        )
    except FileNotFoundError:
        has_persona_state = False
    has_binding = catalog.active_chrononaut_id(catalog_dir, persona_key) == chrononaut_id

    if current is not None and has_catalog_entry and has_figure_save and has_persona_state and has_binding:
        return PersonaCreationOutcome(persona_key, "already_ready", chrononaut_id=chrononaut_id)

    if not has_catalog_entry:
        catalog.register(catalog_dir, catalog.CatalogEntry(
            participant_id=persona_key, chrononaut_id=chrononaut_id, persona_key=persona_key,
        ))
    if not has_figure_save:
        catalog.store_figure_save(catalog_dir, persona_key, chrononaut_id, final_save)
    if not has_persona_state:
        onboarding.ensure_participant_persona_state(ps_store, states_dir, persona_key, chrononaut_id, final_save)
    if current is None:
        core_store.publish_current_save(run_dir, persona_key, final_save, ps_store, states_dir)
    if not has_binding:
        catalog.bind_for_section(catalog_dir, persona_key, chrononaut_id, has_open_section=False)
    return PersonaCreationOutcome(persona_key, "completed", chrononaut_id=chrononaut_id)


def advance_one_persona_creation(
    *,
    run_dir: str | Path,
    states_dir: str | Path,
    schema_path: str | Path,
    onboarding_dir: str | Path,
    catalog_dir: str | Path,
    community_id: str,
    generation: int,
    persona_key: str,
    gm_transport_factory,
    persona_driver_factory,
    print_fn: Callable[[str], None] = lambda s: None,
) -> PersonaCreationOutcome:
    """Fuehrt GENAU EINEN Erschaffungsversuch (bis Save ODER Pause/Fehler)
    fuer EINE Persona aus — idempotent/fortsetzbar bei Wiederholung (Resume
    laedt denselben Onboarding-Auftrag ueber `persona_key` weiter, exakt wie
    `_cmd_new_or_switch_character` fuer einen Menschen). Eine bereits
    `completed` Persona wird NICHT blind als bereit gemeldet (C1) --
    `_publication_reconcile` prueft/vervollstaendigt die tatsaechliche
    Bereitschaft OHNE neuen Modellaufruf.

    Ein unerwarteter, bislang ungefangener `OSError` (z.B. aus
    `onboarding._write` innerhalb eines lokalen Checkpoint-Writes, ODER aus
    `request_ledger.finish_received()`s interner Kosten-/Latenznachbuchung)
    propagiert weiterhin UNGEFANGEN aus dieser Funktion -- GENAU EIN
    Erschaffungsversuch bricht dabei kontrolliert (kein Datenverlust, alle
    bereits durabel geschriebenen Requestledger-/Onboarding-Zwischenschritte
    bleiben erhalten) mit einer propagierenden Ausnahme ab, exakt wie die
    bestehenden C1/C2-Regressionstests (`tests/mmo_sim/test_p2c_community_
    continuity_subprocess.py`) das fuer die drei Checkpoint-Write-Naehte
    bewusst pruefen (ein neuer Prozess/Aufruf setzt ueber `onboarding.
    start_or_resume`/`request_ledger.find_durable_result` an derselben
    Stelle fort). `advance_community_creation()` (unten) faengt diese
    Ausnahme deshalb selbst PRO PERSONA ab -- NICHT diese Funktion --, damit
    eine einzelne Persona in einem Mehrpersonen-Batch die uebrigen nicht
    anhaelt, ohne das Verhalten dieser Funktion bei einem direkten/
    einzelnen Aufruf zu aendern (C2-Nacharbeit, End-Critic-Befund 1,
    2026-09-25)."""
    run_dir = Path(run_dir)
    states_dir = Path(states_dir)
    schema_path = Path(schema_path)
    onboarding_dir = Path(onboarding_dir)
    catalog_dir = Path(catalog_dir)

    ps_store = PersonaStateStore(schema_path=schema_path)
    state = onboarding.start_or_resume(onboarding_dir, persona_key)
    if state.status == "completed":
        return _publication_reconcile(
            run_dir=run_dir, states_dir=states_dir, onboarding_dir=onboarding_dir,
            catalog_dir=catalog_dir, persona_key=persona_key, final_save=state.final_save,
            ps_store=ps_store,
        )
    if gm_transport_factory is None or persona_driver_factory is None:
        return PersonaCreationOutcome(
            persona_key, "no_driver",
            reason=(
                "Community-Erstgeneration erfordert eine konfigurierte SL-Anbindung "
                "(gm_transport_factory) UND Persona-Anbindung (persona_driver_factory) — "
                "hier nicht konfiguriert, kein Dialogstart."
            ),
        )
    blocked, reason = read_admission_block(run_dir)
    if blocked:
        return PersonaCreationOutcome(persona_key, "blocked", reason=str(reason))
    try:
        draft_state = ps_store.load_state(persona_key, states_dir=states_dir)
    except FileNotFoundError:
        return PersonaCreationOutcome(
            persona_key, "error", reason=f"kein Bootstrap-Profilentwurf fuer {persona_key!r} gefunden.",
        )

    onboarding_chat_id = f"onboarding-{persona_key}"
    try:
        accepts_id = len(inspect.signature(gm_transport_factory).parameters) >= 1
    except (TypeError, ValueError):
        accepts_id = False
    try:
        gm_transport = gm_transport_factory(onboarding_chat_id) if accepts_id else gm_transport_factory()
    except Exception as e:
        return PersonaCreationOutcome(persona_key, "error", reason=f"SL-Anbindung nicht verfuegbar: {e}")
    try:
        persona_driver = persona_driver_factory(persona_key)
    except Exception as e:
        return PersonaCreationOutcome(persona_key, "error", reason=f"Persona-Anbindung nicht verfuegbar: {e}")

    turn_idx = len(state.steps)
    initial_outgoing = state.steps[-1]["answer"] if state.steps else _initial_outgoing(draft_state)
    get_reply = _persona_get_reply_factory(
        run_dir=run_dir, persona_driver=persona_driver, community_id=community_id,
        generation=generation, persona_key=persona_key, draft_state=draft_state,
        onboarding_dir=onboarding_dir, print_fn=print_fn,
    )
    outcome = run_admitted_creation_dialog(
        run_dir=run_dir, onboarding_dir=onboarding_dir, participant_id=persona_key,
        turn_idx_start=turn_idx, initial_outgoing=initial_outgoing, gm_transport=gm_transport,
        get_reply=get_reply, harvest_validator=ZeitrissHarvestValidator(), print_fn=print_fn,
        role="community_creation_gm", table_id=community_id, section_id=f"gen{generation}",
    )
    if outcome.status != "completed":
        return PersonaCreationOutcome(persona_key, outcome.status, reason=outcome.reason)

    # Publikation -- dieselbe gemeinsame Reconcile-Hilfe wie ein Reentry
    # (C1): dieselben Primitiven wie der menschliche Pfad (`ui/tui.py:
    # _cmd_new_or_switch_character`), OHNE Aktivfiguren-Lock/-Sync (eine
    # Community-Erstgeneration-Persona hat strukturell NIE einen vorherigen
    # Current-Save). `onboarding.complete_with_save` (innerhalb von
    # `run_admitted_creation_dialog`) hat `state.status="completed"` bereits
    # gesetzt -- ein Absturz GENAU zwischen hier und einer vollstaendigen
    # Publikation wird beim naechsten Aufruf ueber denselben `already_
    # completed`-Zweig oben durch `_publication_reconcile` nachgeholt (kein
    # zweiter, abweichender Publikationsweg).
    result = _publication_reconcile(
        run_dir=run_dir, states_dir=states_dir, onboarding_dir=onboarding_dir,
        catalog_dir=catalog_dir, persona_key=persona_key, final_save=outcome.save_block,
        ps_store=ps_store,
    )
    if result.status in ("completed", "already_ready"):
        print_fn(f"[{persona_key}] Erschaffung abgeschlossen: char_id={result.chrononaut_id}. Figur ist tischbereit.")
    return result


def advance_community_creation(
    *,
    run_dir: str | Path,
    states_dir: str | Path,
    schema_path: str | Path,
    onboarding_dir: str | Path,
    catalog_dir: str | Path,
    community_id: str,
    generation: int,
    planned_persona_keys: list[str],
    gm_transport_factory,
    persona_driver_factory,
    print_fn: Callable[[str], None] = lambda s: None,
    limit: int | None = None,
) -> list[PersonaCreationOutcome]:
    """Iteriert ALLE geplanten Personas (Reihenfolge des gepinnten Bootstrap-
    Plans) und versucht je EINEN vollstaendigen Erschaffungsversuch. Eine
    blockierte/abgelehnte/fehlgeschlagene Persona haelt die UEBRIGEN nicht
    an — jede Persona bekommt ihren EIGENEN frischen Admission-Gate-Check
    (globales Budget/Stop blockiert dann konsistent ALLE noch offenen
    Personas, ohne dass dieses Modul das selbst nachbilden muss).

    C4 (P2-Community-Kontinuitaet 2026-09-25, 01_AUFTRAG §3 C4: 'ein
    begrenzter Fortschrittsschritt ... erlaubt Rueckkehr/Abbruch/Fortsetzen,
    ohne erst saemtliche acht Dialoge absolvieren zu muessen'): `limit`
    (Default `None` == unveraendertes Verhalten, ALLE geplanten Personas
    werden wie bisher in einem Aufruf bis Fertig/Pause/Fehler getrieben)
    begrenzt, wie viele Personas, die NOCH NICHT abgeschlossen sind (also
    tatsaechlich einen neuen Dialogschritt/Modellrequest ausloesen wuerden),
    in DIESEM Aufruf versucht werden -- bereits `completed` Personas werden
    IMMER (kostenfrei, kein Modellaufruf, s. `_publication_reconcile`)
    mitgepflegt/gemeldet, sie verbrauchen das Limit nicht. Personas, die das
    Limit erreicht haben, bevor sie an der Reihe waeren, bekommen den
    Status `deferred` (unveraendert offen, requestfrei, beim naechsten
    Aufruf an genau dieser Stelle fortsetzbar) -- eine Betreiber-/
    Startkonfiguration (01 §3 A), keine feste Populationsregel."""
    outcomes: list[PersonaCreationOutcome] = []
    attempts_used = 0
    for pk in planned_persona_keys:
        prior = onboarding.peek(onboarding_dir, pk)
        needs_attempt = prior is None or prior.status == "in_progress"
        if needs_attempt and limit is not None and attempts_used >= limit:
            outcomes.append(PersonaCreationOutcome(
                pk, "deferred",
                reason=(
                    f"begrenzter Fortschrittsschritt (limit={limit}) fuer diesen Aufruf "
                    "erreicht -- bleibt offen, requestfrei, beim naechsten Aufruf an "
                    "dieser Stelle fortsetzbar."
                ),
            ))
            continue
        if needs_attempt:
            attempts_used += 1
        # C2-Nacharbeit (End-Critic-Befund 1, 2026-09-25): `advance_one_
        # persona_creation` propagiert einen unerwarteten `OSError` (z.B.
        # aus `request_ledger.finish_received()`s interner Kosten-/
        # Latenznachbuchung, MAIN-DATENWEGENTSCHEIDUNG.md §6s viertes
        # Fenster "vor/nach received/accounted") bewusst UNGEFANGEN (s.
        # deren Docstring) -- GENAU DIESE Stelle, nicht die einzelne
        # Persona-Funktion selbst, haelt das oben dokumentierte
        # Isolationsversprechen ein: der Fehlschlag EINER Persona wird HIER
        # in einen eigenen `error`-Outcome umgewandelt, die Schleife laeuft
        # fuer die UEBRIGEN geplanten Personas unveraendert weiter. Ein
        # direkter Einzelaufruf von `advance_one_persona_creation` (z.B. die
        # bestehenden Subprozess-Regressionstests fuer die drei Checkpoint-
        # Write-Naehte) ist von diesem Catch nicht betroffen -- er sitzt
        # ausschliesslich hier, in der Batch-Iteration.
        try:
            outcomes.append(advance_one_persona_creation(
                run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
                onboarding_dir=onboarding_dir, catalog_dir=catalog_dir,
                community_id=community_id, generation=generation, persona_key=pk,
                gm_transport_factory=gm_transport_factory, persona_driver_factory=persona_driver_factory,
                print_fn=print_fn,
            ))
        except Exception as e:
            outcomes.append(PersonaCreationOutcome(
                pk, "error",
                reason=(
                    f"unerwarteter Fehler waehrend des Erschaffungsversuchs fuer "
                    f"{pk!r} ({type(e).__name__}: {e}) -- Fortschritt (bereits durabel "
                    "geschriebene Requestledger-/Onboarding-Schritte) bleibt erhalten, "
                    "ein spaeterer Aufruf setzt an derselben Stelle fort; die uebrigen "
                    "geplanten Personas werden von diesem Fehlschlag nicht angehalten."
                ),
            ))
    return outcomes


# ---------------------------------------------------------------------------
# Gate B (02_PERSONA_NEUER_CHRONONAUT.md, Terminal-Bestand/Neustart-Auftrag
# 2026-10-02): eine bereits spielende, bekannte Persona (vorhandene aktive
# Figur) erschafft auf ausdrueckliche Einladung einen ZUSAETZLICHEN eigenen
# Chrononauten fuer einen gemeinsamen Level-1-Frischstart. Im Unterschied zu
# `advance_one_persona_creation` oben (Community-ERSTgeneration, Persona hat
# strukturell NIE einen vorherigen Current-Save) MUSS dieser Weg eine
# bereits vorhandene aktive Figur unveraendert erhalten koennen -- dieselbe
# Bindungssicherheit wie der menschliche Mehrfigurenweg
# (`ui/tui.py:_cmd_new_or_switch_character`/`_switch_active_figure`), nur
# an der Domaenenebene wiederverwendet (UI-Aktion und headless Aktion
# benutzen denselben Anwendungs-/Storeweg, 01_AUFTRAG_UND_GRENZEN.md §Gate
# B). Reine Wiederverwendung vorhandener Primitiven (`onboarding.
# start_or_resume(force_new=...)` wie beim Menschen, `catalog`-Mehrfiguren-
# Katalog, `core.store`-Current-Autoritaet, `request_ledger`-Idempotenz) --
# kein neuer Store, kein neuer Adapter, kein neues Unterprodukt.
# ---------------------------------------------------------------------------


def _additional_onboarding_key(persona_key: str, generation: int) -> str:
    """Eigene, von der Persona-Hauptkennung GETRENNTE Onboarding-/
    Requestledger-Buchhaltungskennung fuer EINEN Zusatzfigur-Versuch
    (`generation` vom Aufrufer gewaehlt, s. `advance_additional_persona_
    creation`-Docstring). Loest strukturell die Mehrdeutigkeit auf, die ein
    blosses `force_new` auf der UNVERAENDERTEN `persona_key`-Onboardingdatei
    haette (ein bereits abgeschlossener Auftrag dort koennte entweder die
    ALTE, laengst aktive Figur oder eine bereits fertige, nur noch nicht
    vollstaendig publizierte ZUSAETZLICHE Figur sein) -- mit einer EIGENEN
    Datei pro `generation` ist diese Unterscheidung nie noetig, resume/
    reconcile bleiben dadurch einfache, bereits vorhandene `onboarding.
    start_or_resume(force_new=False)`-Semantik. NUR fuer Onboarding-Scratch/
    Requestledger-Buchung -- Katalog/Current/Persona-State bleiben IMMER an
    der realen `persona_key`-Identitaet gebunden (s. `_publication_
    reconcile_additional`)."""
    return f"{persona_key}__additional_gen{generation}"


def _additional_creation_pending_key(persona_key: str) -> str:
    """R1-Nacharbeit MUSS-2 (2026-10-02, 04_NAECHSTE_SESSION.md §2 Persona-
    Aequivalent): stabile, NUR von `persona_key` abhaengige Vorgangsbindungs-
    Kennung fuer `onboarding.bind_attempt`/`resolve_attempt` -- GETRENNT von
    `_additional_onboarding_key`s generation-spezifischer Dialog-
    Scratchdatei. Der Aufrufer (`ui/tui.py:_invite_persona_fresh_start`,
    Zeile ~692) leitet seine `generation` unveraendert weiter aus der
    Kataloganzahl ab (Rueckwaertskompatibilitaet, s. `onboarding.
    bind_attempt`-Docstring); schlaegt `catalog.store_figure_save` NACH
    einem bereits erfolgreichen `catalog.register` fehl (gewoehnlicher
    `OSError`), ist diese Ableitung beim naechsten Aufruf um 1 verschoben --
    die neue, aber noch unvollstaendige Figur zaehlt dort bereits mit
    (dieselbe Fehlerklasse wie B1 beim Menschen vor dessen Fix). `bind_
    attempt` auf DIESEM Schluessel haelt die tatsaechlich fuer den Dialog-
    Scratch verwendete Generation stabil, bis die Katalogpersistenz
    (`catalog.register` UND `catalog.store_figure_save`) vollstaendig
    nachgeholt ist (s. Aufrufstellen unten, `result.chrononaut_id is not
    None` als Signal fuer 'durabel persistiert')."""
    return f"{persona_key}__additional_pending"


def find_resumable_additional_creation(onboarding_dir: str | Path) -> list[dict]:
    """E2E-Nacharbeit B1-MENUE (2026-10-02, 02_B1B2_NACHZUG.md §C): reine
    Lesefunktion (kein Seiteneffekt, analog `catalog.find_registration`) --
    scant die bestehenden `_additional_creation_pending_key`-Ledgerdateien
    (`attempt__<persona_key>__additional_pending.json`, von `onboarding.
    bind_attempt` angelegt) nach NICHT abgeschlossenen (`resolved: False`)
    Zusatzfigur-Vorgaengen, deren zugehoeriger Onboarding-Dialog bereits
    VOLLSTAENDIG abgeschlossen ist (`status == "completed"`, d.h. der SL-
    Dialog selbst ist durch -- es fehlt nur noch die Katalogpersistenz nach
    einem gewoehnlichen `register`/`store_figure_save`-I/O-Fehler, s.
    `advance_additional_persona_creation`). NUR fuer GENAU diesen Fall liefert
    ein Aufruf von `advance_additional_persona_creation` mit der hier
    zurueckgegebenen `generation` **0 weitere SL-/Einladungsaufrufe** --
    ein noch NICHT abgeschlossener Dialog (SL-Turn haengt noch) wird bewusst
    NICHT als 'fortsetzbar' gemeldet (ein reiner Katalog-/Save-Nachtrag ist
    etwas anderes als eine fortzusetzende Modellinteraktion, fuer die
    `ui/tui.py` weiterhin den regulaeren Einladungs-/Erschaffungsweg nutzt).

    Liefert eine Liste von `{"persona_key": str, "generation": int}`, sortiert
    nach `persona_key` fuer eine deterministische Anzeige. Leere Liste, wenn
    `onboarding_dir` nicht existiert oder kein passender Datensatz gefunden
    wird."""
    onboarding_dir = Path(onboarding_dir)
    results: list[dict] = []
    if not onboarding_dir.is_dir():
        return results
    suffix = "__additional_pending"
    for path in sorted(onboarding_dir.glob("attempt__*__additional_pending.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict) or data.get("resolved", True):
            continue
        key = data.get("key")
        generation = data.get("generation")
        if not isinstance(key, str) or not key.endswith(suffix) or not isinstance(generation, int):
            continue
        persona_key = key[: -len(suffix)]
        if not persona_key:
            continue
        onboarding_key = _additional_onboarding_key(persona_key, generation)
        state = onboarding.peek(onboarding_dir, onboarding_key)
        if state is not None and state.status == "completed":
            results.append({"persona_key": persona_key, "generation": generation})
    return results


def advance_additional_persona_creation(
    *,
    run_dir: str | Path,
    states_dir: str | Path,
    schema_path: str | Path,
    onboarding_dir: str | Path,
    catalog_dir: str | Path,
    community_id: str,
    generation: int,
    persona_key: str,
    gm_transport_factory,
    persona_driver_factory,
    print_fn: Callable[[str], None] = lambda s: None,
) -> PersonaCreationOutcome:
    """Fuehrt GENAU EINEN Erschaffungsversuch fuer eine ZUSAETZLICHE Figur
    einer bereits spielenden Persona aus (02 'Erschaffung': 'Bestehende
    Engine und vorhandener Erschaffungsservice stellen Fragen, Persona
    beantwortet sie selbst ... Neue technische Auftragsidentitaet pro
    weiterer Erschaffung, getrennt von vorherigen abgeschlossenen
    Auftraegen'). Der Aufrufer (z.B. `ui/tui.py`, NACH einer echten,
    protokollierten Zusage der Persona zu einer konkreten Einladung --
    Einladung != Zustimmung, derselbe Vertrag wie `_cmd_local_round`) MUSS
    fuer `persona_key` bereits mindestens EINE registrierte Figur
    (`catalog.list_for_participant`) vorfinden; ohne eine solche ist dies
    kein Zusatzfigur-Fall, sondern der reguläre Erstfigur-/Community-
    Bootstrap-Weg (`advance_one_persona_creation`/`advance_community_
    creation`) -- `generation` MUSS der Aufrufer so waehlen, dass sie fuer
    DIESEN `persona_key` noch nie verwendet wurde (z.B. `len(catalog.
    list_for_participant(...)) + 1`, stabil ueber Resume-Aufrufe hinweg,
    solange die neue Figur noch nicht registriert ist); dieselbe
    `community_id`/`generation`-Kombination ist bei einem Resume/Retry
    DERSELBEN noch offenen Zusatzfigur-Anfrage erneut zu uebergeben (kein
    Doppelrequest, s. `_additional_onboarding_key`-Docstring).

    Fehler/Level/Katalog/Abschnittsgrenzen-Semantik (02, verbindlich):
    KEIN `level=1`-Patch an einem alten Save, KEINE Uebernahme alter
    Wallets/Inventare/Save-Refs -- die KI-SL liefert ueber denselben
    Erschaffungsdialog wie ein Mensch einen vollstaendigen, EIGENEN
    synthetischen Level-1-Save (`run_admitted_creation_dialog`,
    unveraendert). Die alte aktive Figur bleibt bei einem offenen
    Abschnitt/Abschlussauftrag unveraendert aktiv -- die neue Figur wird
    dann registriert+gesichert, aber NICHT aktiviert (s. `_publication_
    reconcile_additional`), kein Umgehungswrite, kein KI-Ersatz. Community-
    IDs/Roster/fremde Persona-Daten werden von dieser Funktion nicht
    beruehrt (sie schreibt ausschliesslich Onboarding-/Katalog-/Current-/
    Persona-State-Dateien fuer `persona_key` selbst)."""
    run_dir = Path(run_dir)
    states_dir = Path(states_dir)
    schema_path = Path(schema_path)
    onboarding_dir = Path(onboarding_dir)
    catalog_dir = Path(catalog_dir)

    ps_store = PersonaStateStore(schema_path=schema_path)
    if not catalog.list_for_participant(catalog_dir, persona_key):
        return PersonaCreationOutcome(
            persona_key, "error",
            reason=(
                f"{persona_key!r} hat noch keine bestehende Figur -- kein Zusatzfigur-Fall "
                "(regulaerer Erstfigur-/Community-Bootstrap-Weg ist zustaendig, s. "
                "advance_one_persona_creation/advance_community_creation)."
            ),
        )
    # B1-Fix (R1-Nacharbeit 2026-10-02): nur wenn die vom Aufrufer
    # uebergebene `generation` fuer `persona_key` noch NIE als Dialog-
    # Scratch angelegt wurde (`onboarding.peek` == None, reine Lesepruefung
    # ohne Seiteneffekt), wird `bind_attempt` konsultiert -- existiert
    # DAFUER bereits ein vorhandener Onboarding-Datensatz (gleich welchen
    # Status, insbesondere eine explizite, bewusste Wiederverwendung
    # derselben `generation` wie bei einer bereits abgeschlossenen
    # Zusatzfigur), bleibt das bisherige, direkte Verhalten BYTEGLEICH
    # erhalten (kein Eingriff in bestehende Idempotenz-/Resume-Vertraege).
    # Nur fuer eine GENUIN NEUE generation-Zahl kann `bind_attempt` eine
    # fruehere, noch nicht vollstaendig katalogpersistierte Generation
    # DIESER Persona zurueckliefern und damit verhindern, dass ein
    # Katalog-I/O-Fehler nach `catalog.register` beim naechsten Aufruf eine
    # dritte, neue Figur anstoesst, waehrend die zweite fuer immer
    # verwaist bleibt (s. `_additional_creation_pending_key`-Docstring).
    if onboarding.peek(onboarding_dir, _additional_onboarding_key(persona_key, generation)) is None:
        try:
            generation = onboarding.bind_attempt(
                onboarding_dir, _additional_creation_pending_key(persona_key),
                seed_generation=generation,
            )
        except (OSError, ValueError) as e:
            return PersonaCreationOutcome(
                persona_key, "error",
                reason=f"Vorgangsbindung fuer Zusatzerschaffung fehlgeschlagen: {e}",
            )
    onboarding_key = _additional_onboarding_key(persona_key, generation)
    state = onboarding.start_or_resume(onboarding_dir, onboarding_key)
    if state.status == "completed":
        result = _publication_reconcile_additional(
            run_dir=run_dir, states_dir=states_dir,
            catalog_dir=catalog_dir, onboarding_dir=onboarding_dir, persona_key=persona_key,
            final_save=state.final_save, generation=generation,
            ps_store=ps_store,
        )
        # B1-Fix (Fortsetzung), IA-1-Nachzug (BRIEF-IA1.md, ehrlicher
        # Abschlussstatus): `resolve_attempt` erst NACH bestaetigter
        # Katalogpersistenz -- `result.chrononaut_id is not None` ist bei
        # JEDEM `_publication_reconcile_additional`-Rueckgabepfad AUSSER den
        # "blocked"-Faellen gesetzt (fehlende ID, B2-Identitaetskonflikt,
        # Auftragsbindung-Claim-Mismatch, Current-Save nicht lesbar, CC-1-
        # UND IA-1-Inhaltskonflikt) -- keiner dieser echten Konflikte darf
        # die Generation als erledigt markieren, s. dortige Docstrings.
        if result.chrononaut_id is not None:
            onboarding.resolve_attempt(
                onboarding_dir, _additional_creation_pending_key(persona_key), generation,
            )
        return result
    if gm_transport_factory is None or persona_driver_factory is None:
        return PersonaCreationOutcome(
            persona_key, "no_driver",
            reason=(
                "Zusatzfigur-Erschaffung erfordert eine konfigurierte SL-Anbindung "
                "(gm_transport_factory) UND Persona-Anbindung (persona_driver_factory) — "
                "hier nicht konfiguriert, kein Dialogstart."
            ),
        )
    blocked, reason = read_admission_block(run_dir)
    if blocked:
        return PersonaCreationOutcome(persona_key, "blocked", reason=str(reason))
    try:
        # C3: dasselbe, bereits gepinnte Profil (Archetyp/Spielstil/
        # Charakterwunsch) der REALEN Persona -- "Die Persona bleibt
        # dieselbe simulierte Person mit demselben Profil" (02). Dies ist
        # der ETABLIERTE Persona-State (nicht der Bootstrap-ENTWURF), er
        # existiert fuer eine bereits spielende Persona bereits vollstaendig.
        draft_state = ps_store.load_state(persona_key, states_dir=states_dir)
    except FileNotFoundError:
        return PersonaCreationOutcome(
            persona_key, "error", reason=f"kein Persona-Profil fuer {persona_key!r} gefunden.",
        )

    onboarding_chat_id = f"onboarding-{onboarding_key}"
    try:
        accepts_id = len(inspect.signature(gm_transport_factory).parameters) >= 1
    except (TypeError, ValueError):
        accepts_id = False
    try:
        gm_transport = gm_transport_factory(onboarding_chat_id) if accepts_id else gm_transport_factory()
    except Exception as e:
        return PersonaCreationOutcome(persona_key, "error", reason=f"SL-Anbindung nicht verfuegbar: {e}")
    try:
        persona_driver = persona_driver_factory(persona_key)
    except Exception as e:
        return PersonaCreationOutcome(persona_key, "error", reason=f"Persona-Anbindung nicht verfuegbar: {e}")

    turn_idx = len(state.steps)
    initial_outgoing = state.steps[-1]["answer"] if state.steps else (
        "Ich moechte einen ZUSAETZLICHEN eigenen Chrononauten erschaffen (meine bisherige "
        "Figur bleibt davon unberuehrt). Fuehre mich Schritt fuer Schritt durch die "
        "Erschaffung. Mein Spielerprofil: "
        f"Archetyp={draft_state.get('archetype', '')!r}, "
        f"Spielstil={draft_state.get('play_style', '')!r}, "
        f"Charakterwunsch={draft_state.get('charwunsch', '')!r}."
    )
    get_reply = _persona_get_reply_factory(
        run_dir=run_dir, persona_driver=persona_driver, community_id=community_id,
        generation=generation, persona_key=persona_key, draft_state=draft_state,
        onboarding_dir=onboarding_dir, print_fn=print_fn,
        onboarding_participant_key=onboarding_key,
    )
    outcome = run_admitted_creation_dialog(
        run_dir=run_dir, onboarding_dir=onboarding_dir, participant_id=onboarding_key,
        turn_idx_start=turn_idx, initial_outgoing=initial_outgoing, gm_transport=gm_transport,
        get_reply=get_reply, harvest_validator=ZeitrissHarvestValidator(), print_fn=print_fn,
        role="community_creation_gm", table_id=community_id, section_id=f"gen{generation}",
    )
    if outcome.status != "completed":
        return PersonaCreationOutcome(persona_key, outcome.status, reason=outcome.reason)
    result = _publication_reconcile_additional(
        run_dir=run_dir, states_dir=states_dir,
        catalog_dir=catalog_dir, onboarding_dir=onboarding_dir, persona_key=persona_key,
        final_save=outcome.save_block, generation=generation,
        ps_store=ps_store,
    )
    # B1-Fix (s. Docstring/Kommentar an der oberen Aufrufstelle): erst JETZT,
    # NACH bestaetigter Katalogpersistenz, gilt diese generation fuer
    # `bind_attempt` als abgeschlossen -- der NAECHSTE, genuin neue
    # Zusatzfigur-Versuch fuer `persona_key` bekommt dadurch eine WEITERE,
    # neue Generation (kein Wiederaufnehmen dieses jetzt fertigen Vorgangs).
    if result.chrononaut_id is not None:
        onboarding.resolve_attempt(
            onboarding_dir, _additional_creation_pending_key(persona_key), generation,
        )
    if result.status == "completed":
        print_fn(
            f"[{persona_key}] Zusatzfigur-Erschaffung abgeschlossen: char_id={result.chrononaut_id}. "
            f"{result.reason or 'Figur ist jetzt tischbereit.'}"
        )
    return result


def _publication_reconcile_additional(
    *,
    run_dir: Path,
    states_dir: Path,
    catalog_dir: Path,
    onboarding_dir: Path,
    persona_key: str,
    final_save: dict,
    generation: int,
    ps_store: PersonaStateStore,
) -> PersonaCreationOutcome:
    """Analog zu `_publication_reconcile` oben, aber fuer eine ZUSAETZLICHE
    Figur einer bereits spielenden Persona: im Unterschied zur Bootstrap-
    Annahme dort ('eine Community-Erstgeneration-Persona hat strukturell
    NIE einen vorherigen Current-Save') MUSS hier mit einem bereits
    vorhandenen, von `final_save` VERSCHIEDENEN Current gerechnet werden --
    `chrononaut_id` wird deshalb IMMER aus `final_save` selbst bestimmt
    (niemals aus `current`, das hier die ALTE Figur tragen kann).

    Aktivierung folgt DERSELBEN Bindungssicherheit wie der menschliche
    Mehrfigurenweg (`ui/tui.py:_cmd_new_or_switch_character`, I4 Luecke 1/2):
    hat die bisherige aktive Figur einen offenen Abschnitt/Abschlussauftrag
    (`core.store.chrononaut_active_binding`/`chrononaut_open_completion_
    order`), bleibt die neue Figur registriert+mit eigenen Savebytes
    gesichert, aber INAKTIV -- kein Ueberschreiben eines gebundenen
    Currents, kein KI-Ersatz, keine automatische Vollgruppenbildung (02
    'Abschnittsgrenzen'). Idempotent/wiederholsicher wie `_publication_
    reconcile`: bereits vollstaendig durchgefuehrte Schritte werden nicht
    doppelt ausgefuehrt, ein bereits erreichter Endzustand erzeugt keinen
    weiteren Schreibvorgang.

    B2-Fix (R1-Nacharbeit 2026-10-02, derselbe Schutz wie `ui/tui.py:
    _finish_new_character_creation` + `catalog.find_registration`): VOR
    jeder ueberschreibenden Publikation (`store_figure_save` UND
    `publish_current_save`) wird geprueft, ob `chrononaut_id` BEREITS (bei
    IRGENDEINEM Teilnehmer -- der eigenen Persona selbst ODER einer
    fremden) real gespeicherte, ABWEICHENDE Bytes traegt. `not has_
    figure_save` schuetzt zwar bereits `store_figure_save` (s.u.), NICHT
    aber `publish_current_save`, das bisher BEDINGUNGSLOS lief -- eine neue
    Erschaffungsantwort mit einer bereits vergebenen `chrononaut_id` UND
    abweichendem Inhalt konnte dadurch den aktiven Current mit Fremdinhalt
    ueberschreiben, waehrend das eigene Figur-Save-Archiv unter derselben ID
    den ALTEN Stand behielt (Archiv/Current liefen auseinander, kein HOLD).
    Die EIGENE, bereits teilregistrierte neue Figur (noch KEIN Save ODER
    bereits IDENTISCHE Bytes, z.B. B1-Resume nach einem `store_figure_save`-
    Fehler mit bereits erfolgreichem `register`) bleibt davon klar
    unterschieden -- nur ein bereits real gespeicherter, ABWEICHENDER Stand
    haelt an (kein False-HOLD)."""
    chrononaut_id = zeitriss_saves.block_char_id(final_save)
    if chrononaut_id is None:
        return PersonaCreationOutcome(
            persona_key, "blocked",
            reason="abgeschlossener Zusatzauftrag ohne auswertbare Chrononaut-ID im final_save.",
        )
    existing_registration = catalog.find_registration(catalog_dir, chrononaut_id)
    if existing_registration is not None:
        if existing_registration.participant_id != persona_key:
            # E2E-Nacharbeit B2-OWNER (2026-10-02, 02_B1B2_NACHZUG.md §B):
            # bekannte FREMDE Eigentuemerschaft haelt UNABHAENGIG von
            # Save-Inhaltsgleichheit oder einem fehlenden Archivsave --
            # weder Byte-Gleichheit noch ein fehlender Fremd-Save beweist
            # eine eigene Auftragszugehoerigkeit zu dieser ID. Dieselbe
            # Pruefung wie im menschlichen Pfad (`ui/tui.py:_finish_new_
            # character_creation`), hier fuer den Persona-Zusatzfigur-Pfad.
            return PersonaCreationOutcome(
                persona_key, "blocked",
                reason=(
                    f"char_id={chrononaut_id} ist bereits einem anderen Teilnehmer "
                    f"({existing_registration.participant_id!r}) zugeordnet -- kontrollierter "
                    "Konflikt, kein automatisches Uebernehmen/Umbenennen. Vorgang bleibt offen, "
                    "kein zweiter Modellaufruf."
                ),
            )
        # Auftragsbindung-Nachzug (2026-10-02,
        # 02_RESTNACHZUG_AUFTRAGSBINDUNG.md §2, ersetzt die vorherige
        # inhaltsbasierte B2-CURRENT-Aequivalent/"abweichend"-Pruefung
        # vollstaendig, analog `ui/tui.py:_finish_new_character_creation`):
        # eine bestehende EIGENE Registrierung ist NUR dann diesem Aufruf
        # zuzurechnen, wenn `onboarding.attempt_claim_matches` belegt, dass
        # GENAU `chrononaut_id` bereits unter GENAU `generation` (demselben
        # Schluessel wie `_additional_creation_pending_key`, s. dort)
        # beansprucht wurde. Blosse Inhaltsgleichheit mit dem Archiv, ein
        # fehlendes Archiv ODER ein aktiver Katalogzeiger sind KEIN Ersatz
        # dafuer -- eine bereits vollstaendig abgeschlossene (resolvte)
        # fruehere Generation + ein bewusst NEUER Auftrag, dessen SL
        # zufaellig dieselbe ID/denselben Inhalt liefert, erfuellt den
        # Claim NICHT (er nennt noch die ALTE Generation) -- HOLD. Ein
        # legitimer B1-Resume erfuellt ihn SEHR WOHL, weil der Claim bereits
        # beim ERSTEN Durchlauf DIESER Generation geschrieben wurde (s.u.),
        # BEVOR irgendein ueberschreibender Write passierte.
        if not onboarding.attempt_claim_matches(
            onboarding_dir, _additional_creation_pending_key(persona_key),
            generation=generation, char_id=chrononaut_id,
        ):
            return PersonaCreationOutcome(
                persona_key, "blocked",
                reason=(
                    f"char_id={chrononaut_id} gehoert nicht nachweislich zu diesem offenen "
                    "Zusatzfigur-Auftrag (bereits vorhandene eigene Registrierung ohne passende "
                    "Auftragsbindung -- gleicher Teilnehmer, gleicher Inhalt oder ein fehlendes "
                    "Archiv beweisen keine Zugehoerigkeit) -- kontrollierter Konflikt, kein "
                    "automatischer Erfolg. Vorgang bleibt offen, kein zweiter Modellaufruf."
                ),
            )
    # Auftragsbindung JETZT dauerhaft festhalten -- VOR dem ersten
    # ueberschreibenden Write unten (Register/Figursave/Current). Idempotent
    # bei Reentry derselben Generation/ID (I/O-Fehler zwischen hier und
    # `resolve_attempt`).
    onboarding.record_attempt_claim(
        onboarding_dir, _additional_creation_pending_key(persona_key),
        generation=generation, char_id=chrononaut_id,
    )
    entries = catalog.list_for_participant(catalog_dir, persona_key)
    has_catalog_entry = any(e.chrononaut_id == chrononaut_id for e in entries)
    # IA-1-Nachzug (BRIEF-IA1.md, archiv-resume-nachzug): derselbe geladene
    # Wert (`own_archive_before`, NICHT nur sein Vorhandensein) wird WEITER
    # UNTEN zusaetzlich fuer den Ziel-Archiv-Inhaltsvergleich (IA-1-Guard)
    # wiederverwendet -- kein zweiter Lesevorgang noetig.
    own_archive_before = catalog.load_figure_save(catalog_dir, persona_key, chrononaut_id)
    has_figure_save = own_archive_before is not None
    try:
        persona_state = ps_store.load_state(persona_key, states_dir=states_dir)
        has_persona_state = (
            persona_state.get("persona_key") == persona_key
            and (persona_state.get("plays_char") or {}).get("character_id") == chrononaut_id
        )
    except FileNotFoundError:
        has_persona_state = False
    active_now = catalog.active_chrononaut_id(catalog_dir, persona_key)
    has_binding = active_now == chrononaut_id

    if has_catalog_entry and has_figure_save and has_binding and has_persona_state:
        return PersonaCreationOutcome(persona_key, "already_ready", chrononaut_id=chrononaut_id)

    if not has_catalog_entry:
        catalog.register(catalog_dir, catalog.CatalogEntry(
            participant_id=persona_key, chrononaut_id=chrononaut_id, persona_key=persona_key,
        ))
    if not has_figure_save:
        catalog.store_figure_save(catalog_dir, persona_key, chrononaut_id, final_save)

    if active_now == chrononaut_id:
        # Bereits aktiv (Reentry nach einer vorher erfolgreich
        # durchgefuehrten Aktivierung, deren Persona-State-Schreibschritt
        # danach noch offen war) -- ohne erneuten Current-Write nachholen.
        if not has_persona_state:
            onboarding.ensure_participant_persona_state(
                ps_store, states_dir, persona_key, chrononaut_id, final_save,
            )
        return PersonaCreationOutcome(persona_key, "completed", chrononaut_id=chrononaut_id)

    try:
        current = core_store.load_current_save_or_raise(run_dir, persona_key, ps_store, states_dir)
    except core_store.CurrentSaveUnavailableError as e:
        return PersonaCreationOutcome(
            persona_key, "blocked",
            reason=(
                "Current-Save-Autoritaet der bisherigen aktiven Figur gerade nicht strengt "
                f"lesbar -- unklar, keine Aktivierung ohne geklaerten Stand: {e}"
            ),
        )
    # I4-Nachzug-Parität (`_resolve_real_active_chrononaut_id`): massgeblich
    # ist die real veroeffentlichte Current-Fassung, nicht der ggf.
    # veraltete Katalogzeiger -- bei Abweichung hier konsistent nachgezogen.
    active_before = active_now
    if current is not None:
        real_active_id = zeitriss_saves.block_char_id(current)
        if real_active_id is not None and real_active_id != active_before:
            try:
                catalog.bind_for_section(catalog_dir, persona_key, real_active_id, has_open_section=False)
            except catalog.ActiveBindingError:
                pass
            active_before = real_active_id

    locked = False
    if active_before is not None and active_before != chrononaut_id:
        locked = (
            core_store.chrononaut_active_binding(run_dir, active_before)
            or core_store.chrononaut_open_completion_order(run_dir, active_before)
        )
    if locked:
        return PersonaCreationOutcome(
            persona_key, "completed", chrononaut_id=chrononaut_id,
            reason=(
                f"Aktive Figur '{active_before}' hat einen offenen Abschnitt/Abschlussauftrag -- "
                "Zusatzfigur bleibt INAKTIV registriert (Savebytes gesichert)."
            ),
        )
    # CC-1-Fix (02_CLAIM_CURRENT_NACHZUG.md, UNABHAENGIGER Current-/
    # Standautoritaets-Schutz ZUSAETZLICH zum Claim-Gate oben): der
    # vorherige Katalogzeiger-Reparaturschritt kann `active_before` genau
    # auf `chrononaut_id` setzen, obwohl `current` NICHT mehr die hier zu
    # schreibenden `final_save`-Bytes traegt, sondern einen seither real
    # fortgeschrittenen Stand DERSELBEN Figur (Resume eines eigenen,
    # claim-bestaetigten Auftrags NACH einem bereits spaeter publizierten
    # Fortschritt). Ein passender Claim beweist nur die Zugehoerigkeit zu
    # `chrononaut_id`, NICHT dass `final_save` noch der aktuelle Stand ist
    # -- deshalb Inhaltsvergleich gegen den real geladenen Current derselben
    # Figur, unabhaengig von Claim/Katalogzeiger. Bei Abweichung: fail-closed
    # HOLD (nicht publizieren, Current bleibt erhalten, kein zweiter Modell-/
    # Einladungsaufruf). Bei Gleichheit (echter idempotenter Teilabschluss):
    # normal fertigstellen, keine maskierte No-op-Loesung.
    if (
        current is not None
        and zeitriss_saves.block_char_id(current) == chrononaut_id
        and current != final_save
    ):
        return PersonaCreationOutcome(
            persona_key, "blocked",
            reason=(
                f"char_id={chrononaut_id} hat bereits einen abweichenden, spaeter erspielten "
                "aktuellen Spielstand -- kontrollierter Konflikt, kein automatisches "
                "Ueberschreiben. Vorgang bleibt offen, kein zweiter Modellaufruf."
            ),
        )
    # IA-1-Fix (BRIEF-IA1.md, archiv-resume-nachzug): der CC-1-Guard oben
    # greift NUR, wenn `chrononaut_id` SELBST die aktuell aktive Figur ist
    # -- bei einem normalen Wegwechsel (eine ANDERE Figur ist aktiv) gehoert
    # `current` nicht `chrononaut_id`, CC-1 feuert nicht. Ein Claim beweist
    # nur Auftragseigentum, ein vorhandenes Archiv (G1-Paritaet oben) nur
    # dessen Existenz -- KEINES der beiden beweist, dass `final_save` noch
    # der aktuelle Stand DIESER (dann inaktiven) Figur ist. Deshalb HIER ein
    # vom Claim/von CC-1/G1 UNABHAENGIGER Ziel-Archiv-Inhaltsvergleich:
    # existiert `own_archive_before` (derselbe oben bereits geladene Wert)
    # UND weicht er inhaltlich von `final_save` ab (die Figur ist also,
    # UNABHAENGIG davon, welche ANDERE Figur gerade aktiv ist, selbst
    # bereits fortgeschritten) -> fail-closed HOLD: NICHT aktivieren/
    # publizieren, Archiv UND Current bleiben unberuehrt, kein zweiter
    # Modell-/Einladungsaufruf. KEIN `chrononaut_id` im Rueckgabewert (analog
    # zum CC-1-/O1-/B2-OWNER-Block oben) -- der Aufrufer (`advance_additional_
    # persona_creation`) ruft `onboarding.resolve_attempt` NUR bei gesetztem
    # `chrononaut_id` auf; ein HOLD darf die Generation NICHT als erledigt
    # markieren (ehrlicher Abschlussstatus, s. `ui/tui.py`-Pendant). Erst-
    # Erschaffung (kein Archiv) und B1-Resume-nach-store-Fehler (Archiv
    # ABSENT) sowie ein echter idempotenter Teilabschluss (Archiv ==
    # final_save) sind davon unberuehrt und laufen normal durch. Kein Level-
    # Heuristik/Merge/Downgrade.
    if own_archive_before is not None and own_archive_before != final_save:
        return PersonaCreationOutcome(
            persona_key, "blocked",
            reason=(
                f"char_id={chrononaut_id} hat bereits ein abweichendes, eigenes, fortgeschrittenes "
                "Figuren-Archiv -- kontrollierter Konflikt, kein automatisches Ueberschreiben. "
                "Vorgang bleibt offen, kein zweiter Modellaufruf."
            ),
        )
    # I4 Luecke 1 (`_sync_outgoing_active_figure`-Paritaet): die bisherige
    # aktive Figur wird mit ihrem zuletzt real veroeffentlichten Stand in
    # ihrer EIGENEN Katalog-Persistenz gesichert, BEVOR Current ueberschrieben
    # wird (A -> B -> A bleibt dadurch unveraendert erhalten).
    if active_before is not None and active_before != chrononaut_id and current is not None:
        catalog.store_figure_save(catalog_dir, persona_key, active_before, current)
    if not has_persona_state:
        onboarding.ensure_participant_persona_state(ps_store, states_dir, persona_key, chrononaut_id, final_save)
    core_store.publish_current_save(run_dir, persona_key, final_save, ps_store, states_dir)
    try:
        catalog.bind_for_section(catalog_dir, persona_key, chrononaut_id, has_open_section=False)
    except catalog.ActiveBindingError:
        pass  # Defensiv, kein Doppelpfad -- der reale Sperr-Check oben haette dies bereits abgefangen.
    return PersonaCreationOutcome(persona_key, "completed", chrononaut_id=chrononaut_id)
