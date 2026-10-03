#!/usr/bin/env python3
"""
mmo_sim/domain/zeitriss/onboarding.py — geführter, fortsetzbarer
Einzel-Erschaffungsabschnitt (11 §3, M2/A17).

"Ohne Save bietet die UI 'Neuen Chrononauten erschaffen' an. Sie legt
zunaechst NUR die menschliche Teilnehmeridentitaet und einen technischen,
fortsetzbaren Erschaffungsauftrag an." Abbruch vor erstem gueltigem Save:
Erschaffung bleibt unvollstaendig, KEINE Spielrunde zaehlt, KEIN leerer
v7-Save wird als fertig veroeffentlicht. Fortsetzen nimmt DIESELBE
Erschaffung wieder auf (kein unbemerktes Duplikat).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from ...core.store import HarvestValidator


@dataclass
class OnboardingState:
    participant_id: str
    status: str  # "in_progress" | "completed" | "abandoned"
    steps: list[dict] = field(default_factory=list)
    final_save: dict | None = None
    # C2 (P2-Community-Kontinuitaet 2026-09-25, MAIN-DATENWEGENTSCHEIDUNG.md
    # §3): der SL-Reply UND die Personaantwort des GERADE offenen, noch
    # nicht als `steps`-Eintrag abgeschlossenen Dialogschritts -- persistiert
    # SOFORT bei Empfang (VOR dem jeweils naechsten Modellrequest), damit ein
    # Absturz/Neustart zwischen "SL-Antwort erhalten" und "Personaantwort
    # erhalten" bzw. zwischen "beide erhalten" und `record_step()` keinen der
    # beiden bereits beantworteten/abgerechneten Requests wiederholt. `None`
    # ausserhalb eines offenen Zwischenschritts. Wird von `record_step()`/
    # `complete_with_save()` geleert, sobald der Schritt final uebernommen
    # ist -- reines Scratch-Feld, kein zweites Archiv (`steps` bleibt die
    # einzige dauerhafte Dialoghistorie).
    pending_step: dict | None = None


def _path(onboarding_dir: Path, participant_id: str) -> Path:
    safe = participant_id.replace("/", "_")
    return onboarding_dir / f"onboarding__{safe}.json"


def _load(path: Path) -> OnboardingState | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return OnboardingState(**data)


def _write(path: Path, state: OnboardingState) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(state.__dict__, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def peek(onboarding_dir: str | Path, participant_id: str) -> OnboardingState | None:
    """Reine Lesefunktion OHNE Seiteneffekt (I3-Fertigstellung): liefert den
    vorhandenen Auftrag oder `None` -- im Gegensatz zu `start_or_resume`
    legt `peek` NIEMALS einen neuen leeren Auftrag an. Fuer Stellen wie
    `ui/tui.py`s Fortsetzen-Karte, die nur PRUEFEN wollen, ob bereits
    Fortschritt existiert, ohne beim blossen Anzeigen des Menues bereits
    einen Erschaffungsauftrag zu erzeugen."""
    return _load(_path(Path(onboarding_dir), participant_id))


def start_or_resume(onboarding_dir: str | Path, participant_id: str, *, force_new: bool = False) -> OnboardingState:
    """Ein fehlender Charakter ist ein zulaessiger Onboardingzustand (11 §3)
    — legt bei erstem Aufruf einen leeren `in_progress`-Auftrag an, bei
    Wiederaufruf wird DERSELBE Auftrag zurueckgegeben (kein Duplikat).

    W4-Ergaenzung (F4, "zweite Erschaffung möglich", `ui/tui.py:_cmd_new_
    or_switch_character`): `force_new=True` startet BEWUSST einen frischen
    Erschaffungsauftrag, selbst wenn bereits ein `completed`-Auftrag
    vorliegt -- fuer eine EXPLIZIT gewaehlte weitere Figur. Dieser Auftrag
    bleibt (wie zuvor) ein reines fortsetzbares SCRATCH-Objekt fuer den
    GERADE laufenden Erschaffungsdialog ("Onboarding ≠ Mehrfigurenarchiv",
    WEGKARTE W4) -- die durable Mehrfigurenarchivierung uebernimmt
    `catalog.store_figure_save` (bereits abgeschlossene Figuren verlieren
    dabei NICHTS, ihre Bytes liegen dort bereits getrennt)."""
    onboarding_dir = Path(onboarding_dir)
    path = _path(onboarding_dir, participant_id)
    existing = _load(path)
    if not force_new:
        if existing is not None and existing.status == "in_progress":
            return existing
        if existing is not None and existing.status == "completed":
            return existing
    state = OnboardingState(participant_id=participant_id, status="in_progress")
    _write(path, state)
    return state


def record_pending_reply(
    onboarding_dir: str | Path, participant_id: str, *, sl_reply: str, sl_request_id: str | None,
) -> OnboardingState:
    """C2: persistiert die SOEBEN empfangene SL-Antwort SOFORT -- BEVOR die
    Personaantwort eingeholt wird. Ein Wiederaufruf, der `pending_step.
    sl_reply` bereits gesetzt (und `persona_answer` noch `None`) vorfindet,
    darf die urspruengliche SL-Frage NICHT erneut senden, sondern muss mit
    genau diesem bereits erhaltenen `sl_reply` direkt bei der Personaantwort
    fortsetzen (s. `core/creation_service.run_admitted_creation_dialog`).

    Korrektur (P2-Community-Ergebnisuebergabe 2026-09-25,
    MAIN-DATENWEGENTSCHEIDUNG.md §3, End-Critic-Befund i4ck-Review): DIESE
    Funktion ist NICHT mehr die einzige durable Bindung des empfangenen
    Texts. `core.creation_service.run_admitted_creation_dialog` schreibt den
    empfangenen SL-Text bereits VOR diesem Aufruf durabel in den
    Requestledger-Datensatz (`request_ledger.finish_received(...,
    result_text=...)`, Uebergang nach `state=accounted`). Ein gewoehnlicher
    `OSError` WAEHREND dieses hier beschriebenen lokalen Schreibvorgangs
    verliert den Text deshalb NICHT mehr unwiederbringlich: ein Folgeprozess
    prueft VOR jeder neuen Reservierung/jedem neuen Versand zuerst
    `request_ledger.find_durable_result()` fuer dieselbe Operationsidentitaet
    und findet den bereits abgerechneten Text dort wieder -- kein zweiter
    SL-Request fuer denselben bereits empfangenen Schritt. Diese Funktion
    bleibt der SCHNELLE lokale Pfad (kein Requestledger-Scan noetig, sobald
    sie einmal erfolgreich geschrieben hat); ihr eigener Schreibfehler ist
    kein Powerloss-/fsync-Risikoakzeptanzfall mehr, sondern ein normaler,
    durch die Ledger-Bindung bereits abgesicherter Zwischenzustand."""
    onboarding_dir = Path(onboarding_dir)
    path = _path(onboarding_dir, participant_id)
    state = _load(path)
    if state is None or state.status != "in_progress":
        raise ValueError(f"kein offener Erschaffungsauftrag fuer {participant_id!r}")
    state.pending_step = {
        "sl_reply": sl_reply, "sl_request_id": sl_request_id,
        "persona_answer": None, "persona_request_id": None,
    }
    _write(path, state)
    return state


def record_pending_answer(
    onboarding_dir: str | Path, participant_id: str, *, persona_answer: str, persona_request_id: str | None,
) -> OnboardingState:
    """C2: persistiert die SOEBEN empfangene Personaantwort SOFORT -- BEVOR
    `record_step()` (der abschliessende, sichtbare Dialogschritt) aufgerufen
    wird. Ein Wiederaufruf, der `pending_step` bereits mit BEIDEN Werten
    (`sl_reply` UND `persona_answer`) vorfindet, darf WEDER die SL-Frage
    NOCH die Personaantwort erneut anfordern, sondern uebernimmt direkt
    `record_step()` mit den bereits gesicherten Werten.

    Korrektur (P2-Community-Ergebnisuebergabe 2026-09-25,
    MAIN-DATENWEGENTSCHEIDUNG.md §3): dieselbe Ledger-Bindung wie bei
    `record_pending_reply` (s. dort) gilt hier fuer die Personaantwort --
    `domain.zeitriss.community_creation._persona_get_reply_factory` schreibt
    den empfangenen Antworttext bereits VOR diesem Aufruf durabel in den
    Requestledger-Datensatz (`request_ledger.finish_received(...,
    result_text=...)`). Ein `OSError` WAEHREND dieses lokalen
    Schreibvorgangs verliert die Antwort deshalb NICHT mehr: ein
    Folgeprozess findet sie ueber `request_ledger.find_durable_result()`
    wieder, BEVOR ein neuer Persona-Request reserviert/gesendet wird -- kein
    automatischer Zweitrequest fuer denselben bereits empfangenen Schritt."""
    onboarding_dir = Path(onboarding_dir)
    path = _path(onboarding_dir, participant_id)
    state = _load(path)
    if state is None or state.status != "in_progress":
        raise ValueError(f"kein offener Erschaffungsauftrag fuer {participant_id!r}")
    if state.pending_step is None or state.pending_step.get("sl_reply") is None:
        raise ValueError(
            f"kein ausstehender empfangener SL-Reply fuer {participant_id!r} -- "
            "record_pending_reply() muss zuerst aufgerufen werden."
        )
    state.pending_step["persona_answer"] = persona_answer
    state.pending_step["persona_request_id"] = persona_request_id
    _write(path, state)
    return state


def record_step(onboarding_dir: str | Path, participant_id: str, question: str, answer: str) -> OnboardingState:
    """Jeder Schritt wird SOFORT persistiert (Crash-Sicherheit) — ein Abbruch
    zwischen zwei Fragen verliert nur die noch nicht beantwortete Frage,
    nicht den bisherigen Fortschritt. Leert ein ggf. vorhandenes
    `pending_step` (C2) -- der Schritt ist jetzt final in `steps` uebernommen,
    das Scratch-Feld hat seinen Zweck erfuellt."""
    onboarding_dir = Path(onboarding_dir)
    path = _path(onboarding_dir, participant_id)
    state = _load(path)
    if state is None or state.status != "in_progress":
        raise ValueError(f"kein offener Erschaffungsauftrag fuer {participant_id!r}")
    state.steps.append({"question": question, "answer": answer})
    state.pending_step = None
    _write(path, state)
    return state


def complete_with_save(
    onboarding_dir: str | Path, participant_id: str, save_block: dict,
    harvest_validator: HarvestValidator, expected_chrononaut_id: str,
) -> OnboardingState:
    """Markiert die Erschaffung erst dann als `completed`, wenn ein
    gueltiger (v7/Ein-Figur/passende char_id, geprueft ueber die injizierte
    Domaenen-Policy) Save vorliegt — vorher KEIN Dummy-v7, kein fingierter
    Fortschritt (11 §3)."""
    if not harvest_validator.validate_block(save_block, expected_chrononaut_id):
        raise ValueError(
            f"Save-Block fuer {participant_id!r} ist ungueltig oder passt nicht zur erwarteten "
            f"Chrononaut-ID {expected_chrononaut_id!r} — Erschaffung bleibt unvollstaendig."
        )
    onboarding_dir = Path(onboarding_dir)
    path = _path(onboarding_dir, participant_id)
    state = _load(path)
    if state is None:
        raise ValueError(f"kein Erschaffungsauftrag fuer {participant_id!r} — start_or_resume() zuerst aufrufen")
    state.status = "completed"
    state.final_save = save_block
    state.pending_step = None
    _write(path, state)
    return state


def ensure_participant_persona_state(
    persona_state_store, states_dir: str | Path, participant_id: str,
    chrononaut_id: str, save_block: dict,
) -> dict:
    """D1/A2 (PLAN-CRITIC-ABSCHLUSS.md BLOCKER): gemeinsamer Import-/
    Figurenservice -- stellt sicher, dass fuer `participant_id` ein
    gueltiger Persona-State existiert, den `ZeitrissHarvestValidator.
    validate_identity` akzeptiert (`persona_key`==participant_id,
    `plays_char.character_id`==chrononaut_id).

    Existiert bereits ein State (z.B. aus einer vorherigen Spielrunde),
    werden NUR die Identitaetsfelder (`persona_key`/`plays_char`) an den
    importierten Save angeglichen -- `rounds_played`/`learnings`/... bleiben
    unangetastet (Import zaehlt NICHT als gespielte Runde).

    Existiert noch KEIN State (frischer externer Import ohne vorherige
    Persona-Historie), wird ein neuer State mit KLAR TECHNISCH MARKIERTEN
    Platzhaltern fuer `real_name`/`archetype`/`play_style`/`charwunsch`
    angelegt -- NIE erfundene Charakterzuege (Grenzen §5/A22)."""
    chars = save_block.get("characters")
    char0 = chars[0] if isinstance(chars, list) and chars and isinstance(chars[0], dict) else {}
    plays_char = {
        "save_file": f"{participant_id}.json",
        "character_id": chrononaut_id,
        "name": char0.get("name", "?"),
        "callsign": char0.get("callsign", "?"),
    }
    try:
        state = persona_state_store.load_state(participant_id, states_dir=states_dir)
        state["persona_key"] = participant_id
        state["plays_char"] = plays_char
    except FileNotFoundError:
        state = {
            "v": 2,
            "persona_key": participant_id,
            "real_name": participant_id,
            "archetype": (
                "TECHNISCHER PLATZHALTER -- extern importierter Save, kein "
                "erspielter Archetyp/keine erfundene Charaktereigenschaft."
            ),
            "play_style": (
                "TECHNISCHER PLATZHALTER -- extern importierter Save, kein "
                "erspielter Spielstil."
            ),
            "charwunsch": (
                "TECHNISCHER PLATZHALTER -- kein Erschaffungsdialog "
                "durchlaufen (externer Import)."
            ),
            "plays_char": plays_char,
            "rounds_played": 0,
        }
    persona_state_store.save_state(participant_id, state, states_dir=states_dir)
    return state


def abandon(onboarding_dir: str | Path, participant_id: str) -> OnboardingState:
    """Bewusster Neustart (11 §3: 'ein Neustart ist bewusst zu waehlen') —
    erzeugt KEIN unbemerktes Duplikat, sondern markiert den alten Auftrag
    explizit als abgebrochen, bevor ein neuer begonnen wird."""
    onboarding_dir = Path(onboarding_dir)
    path = _path(onboarding_dir, participant_id)
    state = _load(path)
    if state is None:
        raise ValueError(f"kein Erschaffungsauftrag fuer {participant_id!r}")
    state.status = "abandoned"
    _write(path, state)
    return state


def _attempt_path(onboarding_dir: Path, key: str) -> Path:
    safe = key.replace("/", "_")
    return onboarding_dir / f"attempt__{safe}.json"


def bind_attempt(onboarding_dir: str | Path, key: str, *, seed_generation: int) -> int:
    """Terminal-Bestand/Neustart-Auftrag 2026-10-02 (02_NACHARBEITSAUFTRAG.md
    §1/§2 r2): liefert die VOR dem ersten Request dauerhaft gebundene,
    kollisionsfreie Generation fuer EINEN bewusst neuen Vorgang unter `key`
    (ein Vorgang = eine menschliche Zusatzerschaffung ODER eine Persona-
    Frischstart-Einladungsgelegenheit, s. Aufrufer in `ui/tui.py`) --
    GETRENNT von wechselbaren Auditzeilen (`lobby_service.read_offer_log`,
    best-effort, `OSError` dort bewusst verschluckt) UND von der
    Kataloganzahl (die sich durch eine parallele Teilregistrierung
    verschieben kann).

    Existiert bereits ein NICHT abgeschlossener (`resolved=False`)
    Datensatz fuer `key`, wird DESSEN Generation unveraendert zurueckgegeben
    (Wiederaufnahme desselben offenen Vorgangs behaelt ihre Identitaet --
    02 'Zurueck/Abbruch/frische Session ist kein implizites force_new').
    Sonst wird eine NEUE Generation (groesser als jede fuer `key` jemals
    vergebene) angelegt und SOFORT durabel geschrieben, BEVOR der Aufrufer
    irgendeinen Modellaufruf taetigt. `seed_generation` bindet die ERSTE
    jemals fuer `key` vergebene Generation an die Kataloganzahl zum
    Zeitpunkt des allerersten Aufrufs (Rueckwaertskompatibilitaet mit
    Aufrufern, die Figuren unabhaengig von diesem Binder anlegen, z.B.
    `domain.zeitriss.community_creation.advance_additional_persona_
    creation`s eigene direkte `generation`-Uebergabe) -- jede SPAETERE
    Generation fuer denselben `key` ignoriert die Kataloganzahl vollstaendig
    und zaehlt nur noch von der zuletzt gebundenen Generation weiter.

    Ein gewoehnlicher Schreibfehler (`OSError`) ODER ein nicht einordenbarer
    vorhandener Datensatz propagiert UNGEFANGEN, IMMER als `ValueError`
    (entweder `json.JSONDecodeError` bei syntaktisch ungueltigem JSON, oder
    explizit geworfen, falls die oberste Ebene kein Dict ist oder kein
    `"generation"`-Schluessel vorhanden ist -- z.B. bei einem Teilschreib-
    Abbruch, der nur `"resolved"` aber noch nicht `"generation"` persistiert
    hat) -- kontrollierter Halt VOR jedem Modellaufruf (02 'Operativer
    Bind-Fehler/unklare Zuordnung: HOLD vor Modellcall, nicht ueber Zaehler/
    UUID ueberspringen'); der Aufrufer faengt `(OSError, ValueError)` ab und
    bricht sichtbar ab, OHNE eine Ersatzidentitaet zu raten (r2-Nacharbeit-
    Nachzug 2026-10-02, End-Critic-Befund 1: `KeyError`/`AttributeError`
    propagierten vorher bei vier von sechs Korruptionsformen UNGEFANGEN an
    `ui/tui.py`s `except (OSError, ValueError)` vorbei)."""
    onboarding_dir = Path(onboarding_dir)
    path = _attempt_path(onboarding_dir, key)
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or "generation" not in data:
            raise ValueError(
                f"nicht einordenbarer Vorgangs-Datensatz fuer key={key!r} unter {path}: {data!r}"
            )
        if not data.get("resolved", False):
            return int(data["generation"])
        next_generation = int(data["generation"]) + 1
    else:
        next_generation = int(seed_generation)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(
        json.dumps({"key": key, "generation": next_generation, "resolved": False}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    tmp.replace(path)
    return next_generation


def resolve_attempt(onboarding_dir: str | Path, key: str, generation: int) -> None:
    """Schliesst die Generation `generation` fuer `key` ab (eine tatsaechliche
    Entscheidung/ein tatsaechliches Ergebnis liegt jetzt vor -- Save
    erschaffen ODER Persona-Entscheidung erhalten, s. Aufrufer) -- der
    NAECHSTE `bind_attempt`-Aufruf fuer denselben `key` erhaelt dadurch eine
    NEUE Generation, statt denselben (jetzt erledigten) Vorgang weiter als
    offen zu behandeln. No-op, falls fuer `key` keine Generation gebunden
    ist oder die dort gebundene Generation nicht (mehr) `generation`
    entspricht (keine rueckwirkende Fremdaenderung, kein Ueberschreiben
    eines inzwischen bereits weitergezaehlten Datensatzes). Admission-Block/
    Transportfehler/HOLD-Faelle rufen dies bewusst NICHT auf (Vorgang bleibt
    offen, derselbe Versuch ist spaeter mit identischer Identitaet
    fortsetzbar). Ein nicht einordenbarer vorhandener Datensatz propagiert
    UNGEFANGEN als `ValueError` (r2-Nacharbeit-Nachzug 2026-10-02, End-Critic-
    Befund 1, analog `bind_attempt`)."""
    onboarding_dir = Path(onboarding_dir)
    path = _attempt_path(onboarding_dir, key)
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(
            f"nicht einordenbarer Vorgangs-Datensatz fuer key={key!r} unter {path}: {data!r}"
        )
    if int(data.get("generation", -1)) != generation:
        return
    data["resolved"] = True
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def _attempt_claim_path(onboarding_dir: Path, key: str) -> Path:
    safe = key.replace("/", "_")
    return onboarding_dir / f"attempt-claim__{safe}.json"


def record_attempt_claim(onboarding_dir: str | Path, key: str, *, generation: int, char_id: str) -> None:
    """Auftragsbindung-Nachzug (2026-10-02, 02_RESTNACHZUG_AUFTRAGSBINDUNG.md
    §2): bindet `char_id` DAUERHAFT an (`key`, `generation`) -- die
    eindeutige, nachpruefbare Zuordnung "diese Registrierung gehoert zu
    GENAU diesem offenen Erschaffungsauftrag", die blosse Inhalts-/
    Archivgleichheit, derselbe Teilnehmer oder ein aktiver Katalogzeiger
    NICHT ersetzen koennen (s. `attempt_claim_matches`). Aufrufer MUSS dies
    VOR dem ersten ueberschreibenden Abschlusswrite (Katalogregistrierung/
    Figursave/Current-Publikation) aufrufen -- fuer eine bereits vorhandene,
    UNVERAENDERTE Eigenclaim (derselbe `key`+`generation`+`char_id`, z.B.
    I/O-Reentry an Register/Figursave) ist dies ein reines Idempotenz-No-op
    (derselbe Inhalt wird einfach erneut geschrieben).

    GETRENNT von `bind_attempt`/`resolve_attempt`s eigener Ledgerdatei
    (`attempt__<key>.json`) -- eine EIGENE Datei (`attempt-claim__<key>.json`),
    damit ein `bind_attempt`-Aufruf, der bei bereits abgeschlossener
    (`resolved=True`) Generation eine NEUE Generation mintet (und dabei
    SEINE EIGENE Datei komplett neu schreibt), den hier dauerhaft
    protokollierten ALTEN Claim NICHT mit-ueberschreibt/loescht -- genau
    dieser Fortbestand ist die Grundlage dafuer, dass eine SPAETERE, neue
    Generation den ALTEN Claim noch als "gehoert NICHT zu mir" erkennen
    kann (s. `attempt_claim_matches`)."""
    onboarding_dir = Path(onboarding_dir)
    path = _attempt_claim_path(onboarding_dir, key)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(
        json.dumps({"key": key, "generation": generation, "char_id": char_id}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    tmp.replace(path)


def attempt_claim_matches(onboarding_dir: str | Path, key: str, *, generation: int, char_id: str) -> bool:
    """Auftragsbindung-Nachzug (s. `record_attempt_claim`-Docstring):
    liefert `True` NUR, wenn fuer `key` bereits ein Claim-Datensatz
    existiert, der EXAKT `generation` UND `char_id` entspricht -- der
    Beweis, dass `char_id` zu GENAU dem offenen Auftrag `generation`
    gehoert (eigener, noch nicht abgeschlossener ODER gerade in dieser
    Katalogpersistenz abzuschliessender Versuch). `False`, wenn KEIN Claim
    existiert ODER ein Claim mit ABWEICHENDER `generation` und/oder
    `char_id` vorliegt -- in BEIDEN Faellen ist NICHT belegt, dass die
    bestehende Registrierung von `char_id` zu GENAU diesem Aufruf gehoert
    (typischer Fall: eine FRUEHERE, bereits abgeschlossene Generation hat
    `char_id` beansprucht; die jetzige, neue Generation hat dafuer KEINE
    eigene Berechtigung, selbst wenn Teilnehmer/Inhalt identisch sind oder
    ein Archivsave fehlt). Ein nicht einordenbarer vorhandener Datensatz
    propagiert UNGEFANGEN als `ValueError` (analog `bind_attempt`/
    `resolve_attempt`) -- kontrollierter Halt statt stillem Ignorieren
    einer korrupten Bindungsdatei."""
    onboarding_dir = Path(onboarding_dir)
    path = _attempt_claim_path(onboarding_dir, key)
    if not path.exists():
        return False
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(
            f"nicht einordenbarer Auftragsbindungs-Claim fuer key={key!r} unter {path}: {data!r}"
        )
    return data.get("generation") == generation and data.get("char_id") == char_id
