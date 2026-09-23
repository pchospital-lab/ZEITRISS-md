#!/usr/bin/env python3
"""
lobby/rooms.py — QA-Fassaden-Shim (P2).

Die Lobby-/Tisch-/Completion-Autoritaet aus P1 (ehemals 1326 Zeilen in dieser
Datei) lebt jetzt neutral (domaenenfrei) unter `mmo_sim/core/store.py` —
Core-Extraktion, KEINE Kopie (PLAN.md §2). ZEITRISS-Domaenenregeln
(Fuenfer-Tischgrenze, v7-Save-Validierung — vormals `TABLE_MAX_SIZE=5` und
`_validate_harvest`-Hardcodes hier in dieser Datei, PLAN-CRITIC.md A1
BLOCKER) sind jetzt injizierte Policy-Objekte aus `mmo_sim/domain/zeitriss/
policy.py`.

Diese Datei bleibt am alten Ort und mit der alten oeffentlichen API, damit
`section.py`, `faithful_section.py` und `test_lobby_tables.py` (eingefrorene
P1-Regression) UNVERAENDERT weiterlaufen. Abweichungen von der alten Signatur
sind an den betroffenen Funktionen dokumentiert (alt->neu).

`import persona_state as ps` / `import saves as save_lib` bleiben ueber den-
selben Flat-Namespace-Mechanismus wie in P1 erreichbar (sys.path-Eintrag fuer
den harness-Ordner) — diese Dateien selbst BEWEGEN sich nicht, daher bricht
der `__file__`-relative Mechanismus hier nicht (im Gegensatz zum vormaligen
Laufzeit-Patch von `ps._SCHEMA_PATH`, der beim Verschieben DES CODES
gebrochen waere, s. PLAN-CRITIC.md A2).
"""
from __future__ import annotations

import sys
from pathlib import Path

_HARNESS_DIR = Path(__file__).resolve().parents[1]
_AGENT_MP_DIR = _HARNESS_DIR / "agent_mp"
_REPO_ROOT = _HARNESS_DIR.parents[2]  # internal/qa/harness -> internal/qa -> internal -> repo root
for _p in (str(_HARNESS_DIR), str(_AGENT_MP_DIR), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import persona_state as ps  # noqa: E402
import saves as save_lib  # noqa: E402

import mmo_sim.core.store as core_store  # noqa: E402
from mmo_sim.domain.zeitriss.policy import (  # noqa: E402
    ZeitrissHarvestValidator,
    ZeitrissTableSizePolicy,
)

# ── Rueckwaerts-kompatible Konstanten (nicht mehr vom Kern selbst benutzt) ──────
TABLE_MIN_SIZE = 1
TABLE_MAX_SIZE = 5

_ZEITRISS_TABLE_POLICY = ZeitrissTableSizePolicy(min_size=TABLE_MIN_SIZE, max_size=TABLE_MAX_SIZE)
_ZEITRISS_HARVEST_VALIDATOR = ZeitrissHarvestValidator()

# ── Exceptions/Dataclasses: direkter Re-Export ──────────────────────────────────
GroupDerivation = core_store.GroupDerivation
ChrononautLockedError = core_store.ChrononautLockedError
TableSizeError = core_store.TableSizeError
LeaderOnlySendError = core_store.LeaderOnlySendError
VisibilityError = core_store.VisibilityError
TableClosedError = core_store.TableClosedError
TablePendingError = core_store.TablePendingError
CompletionResult = core_store.CompletionResult

derive_group_and_leader = core_store.derive_group_and_leader

# Private Helfer, von test_lobby_tables.py direkt referenziert.
_completion_final_path = core_store._completion_final_path
_completion_plan_path = core_store._completion_plan_path
_completion_guard_path = core_store._completion_guard_path
_open_completion_order_for_table = core_store._open_completion_order_for_table
_member_bound_by_open_order = core_store._member_bound_by_open_order
_table_has_final = core_store._table_has_final
_run_id = core_store._run_id
_safe_component = core_store._safe_component
_read_locks = core_store._read_locks
_write_locks = core_store._write_locks
_locks_path = core_store._locks_path


class Lobby(core_store.Lobby):
    """Alt->neu: `Lobby(run_dir)` bleibt 1-Parameter-Konstruktor — die
    ZEITRISS-Tischgroessen-Policy wird HIER (QA-Fassade), nicht im Kern,
    fest verdrahtet."""

    def __init__(self, run_dir):
        super().__init__(run_dir, _ZEITRISS_TABLE_POLICY)


class Table(core_store.Table):
    """Alt->neu: `join_more(persona_key, chrononaut_id)` bleibt 2-Parameter —
    die Policy wird hier automatisch nachgereicht (Kern-Signatur verlangt sie
    explizit, A1)."""

    def join_more(self, persona_key: str, chrononaut_id: str) -> bool:  # type: ignore[override]
        return super().join_more(persona_key, chrononaut_id, _ZEITRISS_TABLE_POLICY)


def create_table_from_offer_log(lobby, table_id, offer_log_events, chrononaut_ids):
    table, derivation = core_store.create_table_from_offer_log(
        lobby, table_id, offer_log_events, chrononaut_ids,
    )
    if table is not None:
        # Sicher: `Table`-Subklasse fuegt keine neuen Dataclass-Felder hinzu,
        # identisches Instanz-Layout (kein __slots__) -> reine Method-Set-
        # Erweiterung (join_more-Override) durch Klassenwechsel.
        table.__class__ = Table
    return table, derivation


def submit_to_sl(
    table, actor_persona_key, sl_stub, turn_idx, text,
    origin_persona_key=None, origin_source=None, save_payload=None,
):
    return core_store.submit_to_sl(
        table, actor_persona_key, sl_stub, turn_idx, text,
        origin_persona_key=origin_persona_key, origin_source=origin_source,
        save_payload=save_payload,
    )


def post_table_message(table, persona_key, text):
    return core_store.post_table_message(table, persona_key, text)


def persona_view(table, persona_key):
    return core_store.persona_view(table, persona_key)


def operator_view(table):
    return core_store.operator_view(table)


def load_current_save(run_dir, persona_key, states_dir=None):
    return core_store.load_current_save(run_dir, persona_key, ps, states_dir=states_dir)


def complete_section(lobby, table, section_id, harvested_saves, states_dir, today="2026-09-21"):
    """Alt->neu (A5): der neue Kern (`mmo_sim.core.store.complete_section`) hat
    KEIN Default fuer `today` mehr — ein stehengelassenes Testdatum darf bei
    neuen Aufrufern nie implizit greifen. Dieser Default existiert
    AUSSCHLIESSLICH hier, an der QA-Fassaden-Grenze, damit die eingefrorene
    P1-Testsuite (die `complete_section` immer ohne `today` aufruft und
    "2026-09-21" fuer deterministische Vergleiche erwartet) unveraendert
    bestehen bleibt. Jeder NEUE Produktionsaufrufer (mmo_sim/core/runtime.py)
    ruft den Kern direkt mit explizitem realen Datum auf.

    End-Critic-Nacharbeit (BLOCKER, WEGKARTE §6): der Kern trennt die Ernte
    (Phase 1, `_resume_and_harvest`) jetzt von Lock-Release/`__final`/
    `status=closed` (Phase 2, `finalize_section_after_reflection`) -- Phase 2
    laeuft NUR, wenn der Aufrufer sie explizit ausloest (in der Produktion
    `core/runtime.py:SectionRuntime.finalize()`, ERST nach erfolgreicher
    Pflicht-KI-Reflexion). P1/diese Fassade kennt keine Pflicht-Reflexion und
    erwartet weiterhin das alte ATOMARE Verhalten (Ernte+Finalisierung in
    einem Aufruf) -- darum zieht diese Fassade Phase 2 hier sofort nach, wenn
    Phase 1 erfolgreich war. `finalize_section_after_reflection` ist selbst
    idempotent (No-Op bei bereits existierendem `__final`-Marker), daher ist
    das auch beim Doppel-Abschluss-Pfad sicher."""
    result = core_store.complete_section(
        lobby, table, section_id, harvested_saves, states_dir, today,
        _ZEITRISS_HARVEST_VALIDATOR, ps,
    )
    if result.success:
        core_store.finalize_section_after_reflection(lobby, table, section_id)
    return result


def return_to_lobby(lobby, table):
    return core_store.return_to_lobby(lobby, table)
