#!/usr/bin/env python3
"""
mmo_sim/domain/zeitriss/creation_service.py — Betreiber-Grant fuer eine
eng freigegebene Gast-Erschaffung (R2 F4, ZR-BETREIBER-GASTERSCHAFFUNG-
20261103-R2, GENERAL-REVIEW.md §F4).

R1-Luecke (General-Review): nur 2 abandoned-Guards wurden ergaenzt, aber
"freigegeben" blieb reiner Prompttext ohne Grant-Check -- eine ID-
Tischanfrage (`core.table_admission.py`) oder blosser Text IST KEINE
Autoritaet, einen Gast-GM-Aufruf zu erlauben. Dieses Modul liefert NUR die
fehlende Autoritaetsschicht: eine KONKRETE Erschaffungsanfrage, eine
durable Betreiberentscheidung, die GENAU EINEN Gast + GENAU EINEN
Erschaffungsvorgang (Generation) dauerhaft bindet, UND eine
Gueltigkeitspruefung, die VOR JEDEM GM-Aufruf/Save erneut gilt (fehlend/
abgelehnt/fremd/veraltet -> `CreationGrantError`, kein Bypass).

Reuse, kein zweiter Erschaffungsloop: `ui/tui.py`s Gast-Dialogbefehl ruft
nach einer erfolgreichen `ensure_valid_grant`-Pruefung unveraendert
`core.creation_service.run_admitted_creation_dialog` auf (derselbe GM-
Turn-/Admission-/Requestledger-/Korrekturmechanismus wie der Hostpfad).
Die aufrufende Session-Kapazitaetsrolle spielt fuer diese Autoritaet AN
KEINER Stelle eine Rolle -- die Freigabe kommt AUSSCHLIESSLICH aus dem
hier gefuehrten Grant-Record, niemals aus einer Rollen-/Kapazitaetsflagge
der aufrufenden Session.

Ablage: `run_dir/creation_grants/<safe_guest_id>.json`. Record-Form:
    {
      "guest_id", "operator_id", "status": "requested"|"approved"|"rejected",
      "generation": int | None, "created_ts", "updated_ts",
      "log": [ {ts, actor, action, target}, ... ],  # append-only Audit
    }

Restart-fest: `_load`/`_write` nutzen dasselbe atomare Tmp-Replace-Muster
wie `onboarding.py`/`catalog.py` (kein 0-Reset bei existierendem Record)."""
from __future__ import annotations

import json
import time
from pathlib import Path

from . import onboarding as onboarding_lib
from ...core.admission import read_table_decision, try_commit_table_decision


class CreationGrantError(RuntimeError):
    """Fehlende/abgelehnte/fremde/veraltete Freigabe (F4 §2) -- der
    Aufrufer (`ui/tui.py`) darf bei dieser Ausnahme WEDER einen GM-Aufruf
    taetigen NOCH `onboarding.complete_with_save` erreichen."""


def _grants_dir(run_dir: str | Path) -> Path:
    d = Path(run_dir) / "creation_grants"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _grant_path(run_dir: str | Path, guest_id: str) -> Path:
    safe = guest_id.replace("/", "_")
    return _grants_dir(run_dir) / f"{safe}.json"


def _load(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def guest_onboarding_key(guest_id: str, generation: int) -> str:
    """Generation 1 (die ERSTE, normale Gast-Erschaffung) nutzt BEWUSST
    dieselbe Teilnehmerkennung wie jede andere erste Erschaffung
    (`ui/tui.py:_cmd_new_or_switch_character`s Default `onboarding_key =
    self.participant_id`) -- NUR SO bleiben die bestehenden, an die PLAIN-
    Teilnehmerkennung gebundenen LeseWEGE (`TuiSession._resolve_member`,
    `_cmd_table_request_join`, `_cmd_export`) fuer die EIGENE Figur eines
    Gastes nutzbar ("fuer eine Tischanfrage verwenden koennen", F4 §5).

    EIN Betreiber-Re-Grant NACH einem Abbruch (Generation >= 2) bekommt
    dagegen einen EIGENEN, von der Teilnehmerkennung GETRENNTEN Schluessel
    (analog `ui/tui.py:_human_fresh_onboarding_key` auf der Hostseite) --
    ein abgebrochener Vorgang kann dadurch NIE durch ein spaeteres `start_
    or_resume` unter demselben Schluessel wiederbelebt werden (F4 §4).
    Katalog/Current/Persona-State bleiben in JEDEM Fall an der realen
    `guest_id` gebunden (s. `ui/tui.py:_finish_granted_guest_creation`),
    unabhaengig von diesem rein onboarding-internen Scratch-Schluessel."""
    if generation <= 1:
        return guest_id
    return f"{guest_id}__gast_erschaffung_gen{generation}"


def _attempt_is_abandoned(onboarding_dir: str | Path, onboarding_key: str) -> bool:
    """Gemeinsame Lesefunktion fuer `request_creation`/`ensure_valid_
    grant`: `True` NUR, wenn fuer `onboarding_key` bereits ein Record
    existiert UND dieser `status="abandoned"` ist -- reiner Lesevorgang
    (`onboarding.peek`), KEIN Seiteneffekt."""
    state = onboarding_lib.peek(onboarding_dir, onboarding_key)
    return state is not None and state.status == "abandoned"


def guest_attempt_claim_key(guest_id: str) -> str:
    """Schluessel fuer `onboarding.record_attempt_claim`/`attempt_claim_
    matches` (Auftragsbindung-Claim) -- EIGENER Namensraum, getrennt von
    `ui/tui.py:_human_fresh_attempt_key` (menschliche Host-Zusatzfigur),
    damit beide Flows niemals dieselbe Claim-Datei teilen."""
    return f"gast-erschaffung-claim::{guest_id}"


def request_creation(
    run_dir: str | Path, onboarding_dir: str | Path, *, operator_id: str, guest_id: str,
) -> dict:
    """Gast stellt eine KONKRETE Erschaffungsanfrage an EINEN benannten
    Betreiber (F4 §1) -- reine Anfrage, bindet NOCH KEINEN Grant (das macht
    AUSSCHLIESSLICH `decide_creation_request`). Idempotent: ein bereits
    offener (`status="requested"`) Record fuer DENSELBEN `operator_id`
    wird UNVERAENDERT zurueckgegeben. Ein bereits freigegebener
    (`status="approved"`) Record fuer DENSELBEN `operator_id` wird NUR
    dann unveraendert zurueckgegeben, wenn sein Erschaffungsvorgang NICHT
    bereits abgebrochen ist (s. `ensure_valid_grant`) -- eine wiederholte
    Anfrage darf einen NOCH gueltigen Grant nicht versehentlich
    ueberschreiben/entwerten, muss aber nach einem Abbruch einen NEUEN,
    offenen Antrag beginnen koennen (sonst waere der Gast nach einem
    Abbruch strukturell blockiert). Eine Anfrage an einen ANDEREN
    Betreiber ODER nach einer Ablehnung beginnt ebenfalls bewusst einen
    NEUEN, offenen Antrag (alte Entscheidung verliert ihre Bedeutung fuer
    diesen neuen Antrag)."""
    run_dir = Path(run_dir)
    path = _grant_path(run_dir, guest_id)
    record = _load(path)
    if record is not None and record.get("operator_id") == operator_id:
        status = record.get("status")
        if status == "requested":
            return record
        if status == "approved":
            generation = record.get("generation")
            still_open = generation is not None and not _attempt_is_abandoned(
                onboarding_dir, guest_onboarding_key(guest_id, generation),
            )
            if still_open:
                return record
    now = time.time()
    new_record = {
        "guest_id": guest_id, "operator_id": operator_id, "status": "requested",
        "generation": (record or {}).get("generation"),
        "created_ts": now, "updated_ts": now,
        "log": (record or {}).get("log", []) + [
            {"ts": now, "actor": guest_id, "action": "request_creation", "target": operator_id},
        ],
    }
    _write(path, new_record)
    return new_record


def decide_creation_request(run_dir: str | Path, *, operator_id: str, guest_id: str, approve: bool) -> dict:
    """Betreiber-ONLY-Entscheidung UEBER eine bestehende, offene
    (`status="requested"`) Anfrage -- KEIN offener Antrag -> `CreationGrant
    Error`. `operator_id` MUSS mit dem in der Anfrage genannten Betreiber
    uebereinstimmen (geprueft GEGEN den persistierten Record, NIE gegen
    einen Aufrufer-Glauben) -- ein fremder Betreiber kann eine fremde
    Anfrage nicht entscheiden (F4 §1/§2 "fremd").

    Bei `approve=True`: bindet GENAU EINE neue, fuer diesen Gast NIE zuvor
    vergebene Generation (fortlaufend ab der zuletzt vergebenen, 0 beim
    allerersten Mal) UND schreibt `status="approved"` + diese Generation in
    den Record -- das IST der durable Grant (F4 §1), nicht der blosse
    Record-Zustand allein. Bei `approve=False`: `status="rejected"`, KEINE
    Generation gebunden -- `ensure_valid_grant` lehnt danach strukturell ab."""
    run_dir = Path(run_dir)
    path = _grant_path(run_dir, guest_id)
    record = _load(path)
    if record is None or record.get("status") != "requested":
        raise CreationGrantError(
            f"keine offene Erschaffungsanfrage fuer guest_id={guest_id!r} -- request_creation() zuerst."
        )
    if record.get("operator_id") != operator_id:
        raise CreationGrantError(
            f"operator_id={operator_id!r} ist nicht der angefragte Betreiber "
            f"({record.get('operator_id')!r}) -- Entscheidung abgelehnt (fremd)."
        )
    now = time.time()
    if approve:
        prev_generation = record.get("generation") or 0
        record["status"] = "approved"
        record["generation"] = prev_generation + 1
    else:
        record["status"] = "rejected"
    record["updated_ts"] = now
    record.setdefault("log", []).append(
        {"ts": now, "actor": operator_id, "action": "approve" if approve else "reject", "target": guest_id}
    )
    _write(path, record)
    return record


def _creation_decision_id(operator_id: str, guest_id: str, generation: int) -> str:
    """R4 FIX3 (B2/G4, ZR-BETREIBER-GASTERSCHAFFUNG-20261103-R4): Schluessel
    des EINEN gemeinsamen atomaren Entscheid-Slots (`core.admission.
    try_commit_table_decision`/`read_table_decision`, bisher nur fuer
    Tisch-Stops/`complete_section` genutzt) fuer GENAU diese freigegebene
    Gast-Operation+Generation -- derselbe generische Mechanismus, nur
    gebunden an (Betreiber, Gast, Generation) statt an eine Store-
    `table_id`. Eindeutig, solange `operator_id`/`guest_id` sich nicht
    GENAU in der Trennzeichenfolge ueberlappen (dieselbe akzeptierte
    Kollisionsgrenze wie `_safe_table_component`s Zeichenersetzung)."""
    return f"creation-{operator_id}-{guest_id}-gen{generation}"


def ensure_valid_grant(
    run_dir: str | Path, onboarding_dir: str | Path, *, operator_id: str, guest_id: str,
) -> int:
    """Gueltigkeitspruefung VOR JEDEM GM-Aufruf/Save (F4 §2) -- liefert die
    autorisierte Generation ODER wirft `CreationGrantError`:
      - fehlend: kein Record vorhanden.
      - abgelehnt: `status != "approved"` (deckt `"rejected"` UND einen
        noch unentschiedenen `"requested"`-Zustand ab).
      - fremd: `record["operator_id"] != operator_id`.
      - veraltet: der Erschaffungsvorgang GENAU dieser gebundenen
        Generation (`guest_onboarding_key(guest_id, generation)`) ist
        bereits `onboarding.abandon`-markiert -- ein erneutes `start_or_
        resume` unter demselben Teilnehmernamen/derselben Generation darf
        diesen bewusst aufgegebenen Entwurf NICHT wiederbeleben (nutzt den
        bestehenden `onboarding.complete_with_save`-Abandoned-Guard bereits
        HIER, VOR jedem weiteren Schritt). Eine NEUE Betreiberfreigabe
        bindet eine NEUE Generation mit eigenem, unberuehrtem Schluessel.
      - gestoppt (R4 FIX3, B2/G4): ein Betreiber-Stop (`request_creation_
        stop`) hat den gemeinsamen Entscheid-Slot fuer GENAU diese
        Generation bereits gewonnen ('stopped', ODER ein beschaedigter/
        fremder Entscheid -- fail-closed wie `read_table_decision`) --
        dieser Entwurf ist terminal, weder ein weiterer Dialogschritt
        (`_cmd_gast_erschaffung_dialog`) noch eine Publikation
        (`_finish_granted_guest_creation`) ist danach noch moeglich. Ein
        bereits GEWONNENER Annahme-Entscheid ('accepted', s.
        `try_commit_creation_accept`) blockiert HIER NICHT -- die
        Fertigstellung einer bereits angenommenen Figur bleibt idempotent
        erreichbar (completed-Schutz, R3 G3/R4 FIX4)."""
    run_dir = Path(run_dir)
    record = _load(_grant_path(run_dir, guest_id))
    if record is None:
        raise CreationGrantError(f"keine Erschaffungsanfrage/-freigabe fuer guest_id={guest_id!r} vorhanden.")
    status = record.get("status")
    if status != "approved":
        raise CreationGrantError(
            f"Erschaffung fuer guest_id={guest_id!r} ist nicht freigegeben (status={status!r})."
        )
    if record.get("operator_id") != operator_id:
        raise CreationGrantError(
            f"Grant fuer guest_id={guest_id!r} ist an Betreiber {record.get('operator_id')!r} gebunden -- "
            f"{operator_id!r} ist fremd, kein Zugriff."
        )
    generation = record.get("generation")
    if generation is None:
        raise CreationGrantError(f"Grant fuer guest_id={guest_id!r} hat keine gebundene Generation.")
    if _attempt_is_abandoned(onboarding_dir, guest_onboarding_key(guest_id, generation)):
        raise CreationGrantError(
            f"Grant fuer guest_id={guest_id!r}/Generation {generation} ist veraltet (dieser "
            "Erschaffungsvorgang wurde abgebrochen) -- erneute Betreiberfreigabe erforderlich."
        )
    decision = read_table_decision(run_dir, _creation_decision_id(operator_id, guest_id, generation))
    if decision is not None and decision.get("decision") != "accepted":
        raise CreationGrantError(
            f"Grant fuer guest_id={guest_id!r}/Generation {generation} ist durch einen adressierten "
            "Betreiber-Stop beendet (terminal) -- kein weiterer Dialogschritt/Publikation moeglich."
        )
    return generation


def request_creation_stop(run_dir: str | Path, *, operator_id: str, guest_id: str) -> dict:
    """R4 FIX3 (B2/G4, ZR-BETREIBER-GASTERSCHAFFUNG-20261103-R4): adressierter
    Betreiberstop fuer GENAU die bereits gebundene Generation eines
    freigegebenen Gastes, waehrend der Erschaffungsrequest noch offen ist
    (vor der Annahme/Publikation). AUTORITAET: `operator_id` MUSS der im
    Grant-Record gebundene Betreiber sein, der Grant MUSS `status=
    "approved"` mit einer bereits gebundenen Generation tragen -- Ziel+
    Generation sind damit SCHON VOR diesem Aufruf durch die urspruengliche
    Freigabe (`decide_creation_request`) gebunden, nicht erst hier
    erfunden. Reuse des bestehenden Tisch-Stop-Entscheid-Mechanismus
    (`core.admission.try_commit_table_decision`, bisher nur fuer Store-
    `table_id`s genutzt) -- derselbe EINE atomare Entscheid-Slot, den auch
    `try_commit_creation_accept` (vor jeder Publikation) zu gewinnen
    versucht. Gewinnt der Stop ('stopped'), ist der Entwurf terminal (s.
    `ensure_valid_grant`). Hat die Annahme den Slot bereits gewonnen
    ('accepted'), bleibt der Stop wirkungslos fuer den bereits
    angenommenen Fortschritt (derselbe 'plan_committed'-Stil wie
    `table_admission.request_table_stop`) -- der Rueckgabewert nennt den
    tatsaechlich gefallenen Entscheid ehrlich."""
    run_dir = Path(run_dir)
    record = _load(_grant_path(run_dir, guest_id))
    if record is None or record.get("status") != "approved":
        raise CreationGrantError(
            f"kein freigegebener Erschaffungsvorgang fuer guest_id={guest_id!r} -- Stop nicht adressierbar."
        )
    if record.get("operator_id") != operator_id:
        raise CreationGrantError(
            f"operator_id={operator_id!r} ist nicht Betreiber dieser Freigabe "
            f"({record.get('operator_id')!r}) -- Stop abgelehnt (fremd)."
        )
    generation = record.get("generation")
    if generation is None:
        raise CreationGrantError(f"Grant fuer guest_id={guest_id!r} hat keine gebundene Generation.")
    decision_id = _creation_decision_id(operator_id, guest_id, generation)
    stop_won, decision = try_commit_table_decision(
        run_dir, decision_id, "stopped", operator_id=operator_id, guest_id=guest_id, generation=generation,
    )
    decided = "stopped" if stop_won else str(decision.get("decision", "unknown"))
    return {
        "decision": decided, "generation": generation, "guest_id": guest_id, "operator_id": operator_id,
    }


def try_commit_creation_accept(
    run_dir: str | Path, *, operator_id: str, guest_id: str, generation: int,
) -> tuple[bool, dict]:
    """R4 FIX3 (B2/G4): Gegenstueck zu `request_creation_stop` -- versucht
    denselben gemeinsamen Entscheid-Slot mit 'accepted' atomar zu
    gewinnen, GENAU VOR der ersten Katalog-/Current-Publikation in
    `ui/tui.py:_finish_granted_guest_creation`. `(won, decision)`: bei
    `won=True` (bzw. `decision["decision"]=="accepted"` bei einem eigenen
    frueheren idempotenten Gewinn) ist die Publikation zulaessig; gewinnt
    statt dessen ein bereits gesetzter Stop, liefert `decision["decision"]
    =="stopped"` -- der Aufrufer veroeffentlicht dann NICHT."""
    run_dir = Path(run_dir)
    decision_id = _creation_decision_id(operator_id, guest_id, generation)
    return try_commit_table_decision(
        run_dir, decision_id, "accepted", operator_id=operator_id, guest_id=guest_id, generation=generation,
    )


def creation_stop_committed(
    run_dir: str | Path, *, operator_id: str, guest_id: str, generation: int,
) -> bool:
    """R5 A (ZR-BETREIBER-GASTERSCHAFFUNG-20261105-R5, 01_NACHZUG.md §2,
    GUEST-OPERATOR.md §3): reine Lesepruefung, ob der gemeinsame Entscheid-
    Slot fuer GENAU diese laufende Operation+Generation bereits durch einen
    adressierten Betreiber-Stop (bzw. einen fail-closed nicht als 'accepted'
    lesbaren Entscheid) terminal geworden ist -- derselbe Slot und dieselbe
    fail-closed-Lesart wie der Stop-Zweig in `ensure_valid_grant` (keine
    zweite Autoritaet). Gebunden an die ERWARTETE `generation` des gerade
    laufenden Dialogs, NICHT an den aktuellen Grant-Record -- ein neuer Grant
    einer ANDEREN Generation darf diesen alten laufenden Versuch nicht
    freigeben (01_NACHZUG.md §2). Ein bereits GEWONNENER eigener Annahme-
    Entscheid ('accepted') gilt NICHT als Stop (idempotenter completed-Schutz).
    `True` bedeutet: der laufende Erschaffungsweg ist terminal -- `core.
    creation_service.run_admitted_creation_dialog` darf dann KEINEN weiteren
    GM-/Korrektur-Request mehr senden."""
    decision = read_table_decision(
        Path(run_dir), _creation_decision_id(operator_id, guest_id, generation),
    )
    return decision is not None and decision.get("decision") != "accepted"


def grant_status(run_dir: str | Path, guest_id: str) -> dict | None:
    """Reine Lesefunktion (Status-Anzeige/Tests) -- liefert den
    persistierten Grant-Record unveraendert, `None` wenn (noch) keine
    Anfrage fuer `guest_id` existiert."""
    return _load(_grant_path(Path(run_dir), guest_id))


def list_requested_for_operator(run_dir: str | Path, operator_id: str) -> list[dict]:
    """R4 U2 (01_NACHZUG.md U2 Punkt 2/3, PLAYER-UX-REVIEW.md F2): read-only
    Uebersicht aller `status="requested"`-Erschaffungsanfragen, die GENAU AN
    `operator_id` gerichtet sind -- die lokale Antwort auf "der zustaendige
    Betreiber sieht die Anfrage und kann sie nummeriert entscheiden", ohne
    vorher eine `guest_id` kennen zu muessen. Scannt dieselbe Ablage wie
    `request_creation`/`decide_creation_request` (kein neuer Store), analog
    `core.table_admission.list_open_tables`. Liefert deterministisch nach
    `guest_id` sortiert, leer bei fehlendem/leerem `creation_grants`-
    Verzeichnis oder ohne passende offene Anfrage."""
    d = Path(run_dir) / "creation_grants"
    if not d.is_dir():
        return []
    out: list[dict] = []
    for path in sorted(d.glob("*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if record.get("status") == "requested" and record.get("operator_id") == operator_id:
            out.append(record)
    out.sort(key=lambda r: r.get("guest_id", ""))
    return out
