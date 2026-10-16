#!/usr/bin/env python3
"""tests/mmo_sim/fixtures/recovery_contract/budget_calc_fixture.py --
neutrale, oeffentliche Repo-Testfixture fuer `test_recovery_ops_r1.py::
test_budget_seed_30_independent_cases` (ZR-LIVEWEG-PR-KANDIDAT-20261016-R1,
01_AUFTRAG.md C). KEIN historischer Budgetreceipt/kein privates
Pruefpaket -- die Preis-/Kostenformeln sind oeffentlich dokumentierte
Provider-Listenpreise (reiner Mathecode, keine Spielstaende/Secrets/
personenbezogene Daten). Nur die Ablagebeschreibung/Herkunft ist gegenueber
dem privaten Referenzhelfer neu gefasst; `physical_cost_usd`/`BudgetBlocked`/
`main()`-Vertrag und alle Zahlenwerte bleiben unveraendert, damit die
bestehenden 30 unabhaengigen Faelle weiterhin exakt binden.
Counts include all input with disjoint cache read/write subsets PER attempt.
An actual live scenario still requires model/input/count/rate/fee bindings.

Hintergrund des zugrunde liegenden Kostenmodells:

Netzfrei, stdlib-only, keine Live-Requests. Rechnet logische Operationen und
physische Transportversuche GETRENNT:

  `request_ledger.begin()` (SRC/mmo_sim/core/request_ledger.py) committet die
  Reservierung EINMAL pro logischer Operation, VOR dem Transport. Der
  tatsaechliche Versand laeuft danach durch `OWUIChat._post`
  (SRC/internal/qa/harness/owui_client.py), die eine EIGENE Retry-Schleife IM
  selben Adapteraufruf besitzt: Default `max_retries=3` -> bis zu DREI
  physische POST-Versuche fuer EINE einzige logische Operation, nach
  Zeitueberschreitungen mit unklarem Ausgang. Der Ledger-Guard verhindert nur
  eine ZWEITE logische Reservierung fuer dieselbe Identitaet
  (`OpenReservationExistsError`) -- er macht die physischen Versuche
  INNERHALB einer Operation nicht kostenneutral. `mmo_sim/adapters/
  persona_api.py` hat demgegenueber KEINE interne Retry-Schleife (ein
  urlopen()-Aufruf pro `decide()`), ist also pro logischer Operation auf
  GENAU EINEN physischen Versuch begrenzt -- eine eigene, im Quellcode
  ueberprueft Tatsache, nicht angenommen.

  Worst-case = Summe je Rolle aus
    physische_Versuche * (ungecachter_Input * Inputpreis
                           + gecachter_Input * Cache-READ-Satz
                           + Output * Outputpreis
                           + ggf. Cache-Write-Zuschlag) / 1e6
    + belegte Zuschlaege.

  Cache-READ ist KEIN Gratis-Pfad (03_LIVEGRENZE_UND_KOSTEN.md: "Cachehit nur
  als optionale Szenarioersparnis, nicht garantierte Null-/Billigkosten"):
  gecachte Input-Tokens werden zum dokumentierten Cache-READ-Satz
  CACHE_READ_USD_PER_MTOK (0.30 USD/Mtok) bepreist, nie zu 0.

Fehlende Pflicht-Inputs ergeben IMMER ein explizites BudgetBlocked/BLOCKED,
nie eine erfundene Summe. 1.20 USD erscheint hier NUR als optionaler harter
Fruehstop-Deckel (Ergebnis FRUEHSTOP_EXPECTED_BELOW_SCENARIO), nicht als
behauptete Obergrenze fuer den vollen Szenarioumfang.
"""
from __future__ import annotations

import json
import sys
from decimal import Decimal, getcontext

getcontext().prec = 28

# ---- Preise: review/evidence/public-price.json (General, OpenRouter
# anthropic/claude-sonnet-4.6, 2026-10-15) + native-evidence/price_native.json
# (Mains OBSERVED_NATIVE_BILLED_RATE aus la1-data usage.cost_details) ----
INPUT_USD_PER_MTOK = Decimal("3")
OUTPUT_USD_PER_MTOK = Decimal("15")
CACHE_READ_USD_PER_MTOK = Decimal("0.30")
CACHE_WRITE_5MIN_USD_PER_MTOK = Decimal("3.75")
CACHE_WRITE_1H_USD_PER_MTOK = Decimal("6.00")
MTOK = Decimal(1_000_000)

# ROUTES.json (aus Mains nativen route_*.json, exakt uebernommen):
GM_OUTPUT_LIMIT_TOKENS = 16384
PERSONA_OUTPUT_LIMIT_TOKENS = 400

# SRC-Default fuer OWUIChat.max_retries (internal/qa/harness/owui_client.py
# __init__ default max_retries=3); genutzt von mmo_sim/adapters/gm_owui.py
# ueber agent_mp/sl_client.SLSession, s. FLOW-PROOF.json.
GM_DEFAULT_PHYSICAL_RETRIES_PER_LOGICAL_OP = 3
# persona_api.py hat KEINE interne Retry-Schleife (ein urlopen() je decide()).
PERSONA_PHYSICAL_ATTEMPTS_PER_LOGICAL_OP = 1


class BudgetBlocked(Exception):
    """Explizites Signal fuer fehlende Pflicht-Inputs. Niemals abgefangen,
    um stattdessen eine erfundene Summe zu liefern -- der Aufrufer muss
    dieses Signal als BLOCKED_MISSING_BOUND weiterreichen."""

    def __init__(self, missing: str):
        self.missing = missing
        super().__init__(f"BLOCKED_MISSING_BOUND: {missing}")


def _count(value, name, *, positive=False):
    if type(value) is not int or value < (1 if positive else 0):
        raise BudgetBlocked(name + " must be a finite non-negative integer (positive for attempts)")
    return value


def _money(value, name, *, positive=False):
    if isinstance(value, bool) or value is None:
        raise BudgetBlocked(name + " missing/invalid")
    try:
        result = Decimal(str(value))
    except Exception as exc:
        raise BudgetBlocked(name + " invalid decimal") from exc
    if not result.is_finite() or result < 0 or (positive and result == 0):
        raise BudgetBlocked(name + " must be finite and non-negative (positive for next attempt)")
    return result


def physical_cost_usd(
    *, physical_attempts, output_tokens, input_tokens,
    cache_write_tokens=0, cache_write_kind=None, cached_input_tokens=0,
):
    """Explicit SCENARIO, not a live budget guard or native rate proof.

    All token counts are PER PHYSICAL ATTEMPT. input_tokens is the TOTAL
    inclusive input, not Anthropic's uncached-only usage.input_tokens field.
    Cache-read and cache-write tokens are disjoint subsets of that total.
    A write uses the FULL write rate instead of base-input + full-write rate.
    The WHOLE per-attempt cost, including writes, is multiplied by attempts.
    Known-cache scenarios are not conservative no-cache upper bounds.
    Missing/negative/fractional/bool/nonfinite/impossible inputs block.
    """
    n = _count(physical_attempts, "physical_attempts", positive=True)
    out = _count(output_tokens, "output_tokens")
    total_input = _count(input_tokens, "input_tokens")
    reads = _count(cached_input_tokens, "cached_input_tokens")
    writes = _count(cache_write_tokens, "cache_write_tokens")
    if reads + writes > total_input:
        raise BudgetBlocked("cache read/write subsets exceed inclusive input_tokens")
    if cache_write_kind not in (None, "5min", "1h") or (writes and cache_write_kind is None):
        raise BudgetBlocked("cache_write_kind must be 5min or 1h when writes are present")
    uncached = total_input - reads - writes
    write_rate = (CACHE_WRITE_5MIN_USD_PER_MTOK if cache_write_kind == "5min"
                  else CACHE_WRITE_1H_USD_PER_MTOK)
    per_read = Decimal(reads) * CACHE_READ_USD_PER_MTOK / MTOK
    per_write = Decimal(writes) * write_rate / MTOK
    per_attempt = ((Decimal(uncached) * INPUT_USD_PER_MTOK
                   + Decimal(out) * OUTPUT_USD_PER_MTOK) / MTOK + per_read + per_write)
    return {
        "physical_attempts": n,
        "per_attempt_usd": str(per_attempt),
        "cache_read_cost_usd": str(Decimal(n) * per_read),
        "cache_write_cost_usd": str(Decimal(n) * per_write),
        "total_usd": str(Decimal(n) * per_attempt),
        "classification": "EXPLICIT_SCENARIO_NOT_LIVE_AUTHORITY",
        "input_semantics": "per_attempt_inclusive_total_disjoint_cache_subsets",
    }


def gm_output_only_worst_case(physical_attempts, output_tokens=GM_OUTPUT_LIMIT_TOKENS):
    """Explizite General-Vorgabe: physische GM-Versuche x Output x 15 USD/MToken,
    NUR Output, OHNE Input (Input ist fuer kuenftige Laeufe nicht nativ gebunden,
    s. BUDGET-MODEL.json assumptions). Mit physical_attempts=12 ergibt das exakt
    2.94912 USD."""
    _count(physical_attempts, "physical_attempts", positive=True)
    _count(output_tokens, "output_tokens")
    return Decimal(physical_attempts) * Decimal(output_tokens) * OUTPUT_USD_PER_MTOK / MTOK


def p3_local_reserve_heuristic():
    """Lokale, NICHT-provider-gebundene Reserve-Heuristik aus
    PKG/review/reproduction/probe_live_offer.py (General) costs():
    (8592/4)*3/1e6 + 16384*15/1e6. Reproduziert P3s historischen Offenposten
    0.252204 USD (PROTECTED.json) -- bleibt separat sichtbar, wird NIE in
    total_usd eines Live-Szenarios addiert (keine Doppelbuchung)."""
    return (Decimal(8592) / Decimal(4)) * INPUT_USD_PER_MTOK / MTOK + Decimal(GM_OUTPUT_LIMIT_TOKENS) * OUTPUT_USD_PER_MTOK / MTOK


def native_observed_persona_call_reproduction():
    """Reproduziert native-evidence/price_native.json 1:1 aus den Rohtokenzahlen
    (observed, nicht Worst-case): prompt_tokens=7303, completion_tokens=362.
    Kein eigener Providerkontakt -- reine Nachrechnung einer bereits
    exportierten, nativ abgerechneten usage.cost_details-Zeile."""
    prompt_tokens, completion_tokens = 7303, 362
    cost = Decimal(prompt_tokens) * INPUT_USD_PER_MTOK / MTOK + Decimal(completion_tokens) * OUTPUT_USD_PER_MTOK / MTOK
    return {"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens, "reproduced_cost_usd": str(cost), "native_reported_cost_usd": "0.027339"}


def pre_io_reserve_check(remaining_budget_usd, next_physical_attempt_worst_case_usd):
    """Vor JEDEM physischen I/O: ausreichende Reserve muss VORHER bestehen.
    Ein PHYSISCHER Deckel (USD), kein logischer Requestzaehler."""
    remaining = _money(remaining_budget_usd, "remaining_budget_usd")
    needed = _money(next_physical_attempt_worst_case_usd, "next_physical_attempt_worst_case_usd", positive=True)
    return remaining >= needed


def simulate_hard_cap_early_stop(cap_usd, per_physical_attempt_worst_case_usd, max_physical_attempts):
    """Simuliert einen harten physischen Ausgabendeckel: vor jedem Versuch wird
    geprueft, ob die Restreserve den worst-case Preis des NAECHSTEN Versuchs
    noch deckt. Liefert, wie viele der bis zu `max_physical_attempts`
    tatsaechlich stattfinden koennten, bevor der Deckel einen weiteren
    Versuch verhindert (Fruehstop), KEIN garantierter Abschluss."""
    cap = _money(cap_usd, "cap_usd")
    per_attempt = _money(per_physical_attempt_worst_case_usd, "per_physical_attempt_worst_case_usd", positive=True)
    _count(max_physical_attempts, "max_physical_attempts")
    spent = Decimal(0)
    attempts_funded = 0
    for _ in range(max_physical_attempts):
        if not pre_io_reserve_check(cap - spent, per_attempt):
            break
        spent += per_attempt
        attempts_funded += 1
    return {
        "cap_usd": str(cap),
        "per_physical_attempt_worst_case_usd": str(per_attempt),
        "max_physical_attempts_offered": max_physical_attempts,
        "attempts_actually_funded": attempts_funded,
        "spent_usd": str(spent),
        "early_stop_triggered": attempts_funded < max_physical_attempts,
        "expected_outcome": "FRUEHSTOP_EXPECTED_BELOW_SCENARIO" if attempts_funded < max_physical_attempts else "CAP_COVERS_FULL_SCENARIO",
        "is_claimed_upper_bound_for_full_scenario": False,
    }


def run_positive_cases():
    cases = {}

    gm_worst_case_output_only = gm_output_only_worst_case(physical_attempts=12)
    assert gm_worst_case_output_only == Decimal("2.94912"), gm_worst_case_output_only
    cases["gm_twelve_physical_attempts_output_only_worst_case"] = {
        "physical_attempts": 12,
        "output_tokens": GM_OUTPUT_LIMIT_TOKENS,
        "price_usd_per_mtok_output": str(OUTPUT_USD_PER_MTOK),
        "result_usd": str(gm_worst_case_output_only),
        "note": "4 logische GM-Operationen x bis zu 3 physische Versuche (OWUIChat._post Default) = 12 physische Versuche; NUR Output, Input separat gebunden (s. assumptions).",
    }

    p3_reserve = p3_local_reserve_heuristic()
    assert p3_reserve == Decimal("0.252204"), p3_reserve
    cases["p3_local_reserve_heuristic"] = {
        "result_usd": str(p3_reserve),
        "native_reported_reserved_usd": "0.252204",
        "note": "Getrennt sichtbar, kein Providerkostenanker, nie Teil eines Szenario-total_usd.",
    }

    native_repro = native_observed_persona_call_reproduction()
    assert native_repro["reproduced_cost_usd"] == native_repro["native_reported_cost_usd"]
    cases["native_observed_single_call_reproduction"] = native_repro

    one_attempt_persona = physical_cost_usd(physical_attempts=1, output_tokens=PERSONA_OUTPUT_LIMIT_TOKENS, input_tokens=7303)
    cases["persona_single_physical_attempt_known_native_input"] = one_attempt_persona

    cache_case = physical_cost_usd(
        physical_attempts=1, output_tokens=GM_OUTPUT_LIMIT_TOKENS, input_tokens=20000,
        cache_write_tokens=20000, cache_write_kind="5min", cached_input_tokens=0,
    )
    cases["optional_cache_write_scenario_not_guaranteed"] = cache_case

    cache_read_case = physical_cost_usd(
        physical_attempts=1, output_tokens=0, input_tokens=100000, cached_input_tokens=100000,
    )
    assert cache_read_case["total_usd"] == str(Decimal("0.03")), cache_read_case
    cases["cache_read_priced_not_free"] = {
        **cache_read_case,
        "note": "Rework-Fix: cached_input_tokens=100000 bei input_tokens=100000 (voll gecacht, 0 ungecachter Rest) -> 100000*0.30/1e6=0.03 USD, NICHT 0. Cache-READ ist Kosten, keine Gratis-Ersparnis (03_LIVEGRENZE_UND_KOSTEN.md).",
    }

    early_stop = simulate_hard_cap_early_stop(cap_usd="1.20", per_physical_attempt_worst_case_usd=str(Decimal(GM_OUTPUT_LIMIT_TOKENS) * OUTPUT_USD_PER_MTOK / MTOK), max_physical_attempts=12)
    assert early_stop["expected_outcome"] == "FRUEHSTOP_EXPECTED_BELOW_SCENARIO"
    assert early_stop["attempts_actually_funded"] < 12
    cases["hard_cap_1_20_is_early_stop_not_upper_bound"] = early_stop

    return cases


def run_negative_cases():
    cases = {}

    try:
        physical_cost_usd(physical_attempts=None, output_tokens=16384, input_tokens=100)
        raise AssertionError("missing physical_attempts must BLOCK")
    except BudgetBlocked as e:
        cases["missing_physical_attempts_blocks"] = {"status": "BLOCKED_MISSING_BOUND", "missing": e.missing}

    try:
        physical_cost_usd(physical_attempts=3, output_tokens=None, input_tokens=100)
        raise AssertionError("missing output_tokens must BLOCK")
    except BudgetBlocked as e:
        cases["missing_output_tokens_blocks"] = {"status": "BLOCKED_MISSING_BOUND", "missing": e.missing}

    try:
        physical_cost_usd(physical_attempts=0, output_tokens=16384, input_tokens=100)
        raise AssertionError("physical_attempts<=0 must BLOCK")
    except BudgetBlocked as e:
        cases["zero_physical_attempts_blocks"] = {"status": "BLOCKED_MISSING_BOUND", "missing": e.missing}

    try:
        physical_cost_usd(physical_attempts=1, output_tokens=16384, input_tokens=100, cache_write_tokens=500, cache_write_kind=None)
        raise AssertionError("cache_write_tokens without kind must BLOCK")
    except BudgetBlocked as e:
        cases["cache_write_without_kind_blocks"] = {"status": "BLOCKED_MISSING_BOUND", "missing": e.missing}

    # Persona-Rolle in diesem Auftrag: physische Versuchszahl pro logischer Op ist
    # quellgebunden (1, keine interne Retry-Schleife) -- die ANZAHL logischer
    # Persona-Operationen ist aber durch kein Dokument/keine native Evidenz
    # dieses Auftrags gebunden -> BLOCKED, keine erfundene Op-Zahl.
    try:
        physical_cost_usd(physical_attempts=None, output_tokens=PERSONA_OUTPUT_LIMIT_TOKENS, input_tokens=None)
        raise AssertionError("unbound persona logical-op-count scenario must BLOCK")
    except BudgetBlocked as e:
        cases["persona_role_total_scenario_blocked_unbound_op_count"] = {
            "status": "BLOCKED_MISSING_BOUND",
            "missing": e.missing,
            "note": "physical_attempts_per_logical_op fuer persona_api ist quellgebunden 1 (keine interne Retry-Schleife in persona_api.py); die ANZAHL logischer Persona-Operationen fuer dieses Szenario ist jedoch nicht nativ/auftragsgebunden -> kein Gesamt-total fuer diese Rolle erfunden.",
        }

    return cases


def main():
    report = {
        "schema": "general-budget-seed/1",
        "provenance": "tests/mmo_sim/fixtures/recovery_contract/budget_calc_fixture.py -- neutral public repo test fixture",
        "prices": {
            "input_usd_per_mtok": str(INPUT_USD_PER_MTOK),
            "output_usd_per_mtok": str(OUTPUT_USD_PER_MTOK),
            "cache_read_usd_per_mtok": str(CACHE_READ_USD_PER_MTOK),
            "cache_write_5min_usd_per_mtok": str(CACHE_WRITE_5MIN_USD_PER_MTOK),
            "cache_write_1h_usd_per_mtok": str(CACHE_WRITE_1H_USD_PER_MTOK),
            "source": "price_snapshot.json; fixed dated scenario prices, no model alias or provider invoice proof",
        },
        "routes": {
            "gm_output_limit_tokens": GM_OUTPUT_LIMIT_TOKENS,
            "persona_output_limit_tokens": PERSONA_OUTPUT_LIMIT_TOKENS,
            "gm_default_physical_retries_per_logical_op": GM_DEFAULT_PHYSICAL_RETRIES_PER_LOGICAL_OP,
            "persona_physical_attempts_per_logical_op": PERSONA_PHYSICAL_ATTEMPTS_PER_LOGICAL_OP,
        },
        "positive_cases": run_positive_cases(),
        "negative_cases": run_negative_cases(),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
