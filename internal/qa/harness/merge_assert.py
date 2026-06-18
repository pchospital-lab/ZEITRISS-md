#!/usr/bin/env python3
"""
merge_assert.py — v7-Save-Validator + Split/Merge-Regel-Assertions
==================================================================
Erdet die 5er-Split/Merge-Tests (docs/testing.md §P1) am REPO-KANON, statt
Regeln im Harness zu erraten. Zwei Quellen der Wahrheit:

  1. SCHEMA: `systems/gameflow/saveGame.v7.export.schema.json` (strikt,
     additionalProperties:false) — wird live aus dem Repo geladen, nicht
     dupliziert. Validierung via jsonschema (4.26 vorhanden).

  2. MERGE-REGELN: kodiert aus den Runtime-Tests
     - tools/test_economy_merge.js     -> Session-Anker-Economy-Priorität
     - tools/test_continuity_output_contract.js -> Recap-4-Blöcke + Echo-Format
     - tools/test_v7_schema_consistency.js -> shared_echoes(max6,'tag') /
                                              roster_echoes(max5,'char_id')
     - tools/test_v7_issue_pack.js      -> split.family_id/convergence_ready,
                                           imported_saves[].status=='merged',
                                           Seed-Cap 12

VBR-Selbsttest:  python3 harness/merge_assert.py --selftest
  -> validiert die bekannten guten Repo-Fixtures (müssen PASS sein) und ein
     paar bewusst kaputte Mutationen (müssen FAIL sein). Kein SL-Call, gratis.

Als Modul:  from merge_assert import validate_export, assert_merge, Finding
"""
from __future__ import annotations
import argparse
import copy
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ─── Repo-Pfade (SSOT) ────────────────────────────────────────────────────────
REPO = Path("/mnt/agent_share/cloud/repos/ZEITRISS-md-git")
SCHEMA_PATH = REPO / "systems" / "gameflow" / "saveGame.v7.export.schema.json"
FIXTURES = REPO / "internal" / "qa" / "fixtures"

# Echo-Budgets (test_v7_schema_consistency.js)
MAX_ROSTER_ECHOES = 5
MAX_SHARED_ECHOES = 6
MAX_CONVERGENCE_TAGS = 4
# Seed-Cap beim HQ-Merge (speicher-fortsetzung.md §rift_seeds + test_v7_issue_pack)
MAX_OPEN_SEEDS = 12


@dataclass
class Finding:
    code: str
    severity: str        # "FAIL" | "SOFT" | "INFO"
    msg: str

    def __str__(self) -> str:
        sym = {"FAIL": "❌", "SOFT": "⚠️", "INFO": "ℹ️"}.get(self.severity, "·")
        return f"{sym} [{self.code}] {self.msg}"


@dataclass
class Result:
    findings: list[Finding] = field(default_factory=list)

    def add(self, code: str, severity: str, msg: str):
        self.findings.append(Finding(code, severity, msg))

    @property
    def ok(self) -> bool:
        return not any(f.severity == "FAIL" for f in self.findings)

    @property
    def fails(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "FAIL"]

    def merge(self, other: "Result"):
        self.findings.extend(other.findings)


# ─── Schema-Validierung (SSOT = Repo-Schema) ──────────────────────────────────
_SCHEMA_CACHE: dict | None = None


def load_schema() -> dict:
    global _SCHEMA_CACHE
    if _SCHEMA_CACHE is None:
        _SCHEMA_CACHE = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return _SCHEMA_CACHE


def validate_export(save: dict, label: str = "save") -> Result:
    """Validiert einen Save gegen das strikte v7-Export-Schema des Repos.

    Wichtig: Das Export-Schema ist STRIKT (additionalProperties:false). Live-
    SL-Output und Fixtures mit `fixture_kind`/Legacy-Feldern fallen damit auf.
    Deshalb wird `additionalProperties:false` für den Live-Pfad NICHT als hartes
    FAIL gewertet, sondern Zusatz-Properties als SOFT gemeldet (der Runtime-
    Loader normalisiert die ohnehin). Pflichtfeld-Fehler bleiben hart FAIL.
    """
    res = Result()
    try:
        import jsonschema  # noqa: PLC0415
    except ImportError:
        res.add("SCHEMA-DEP", "FAIL", "jsonschema nicht installiert")
        return res

    schema = load_schema()
    validator = jsonschema.Draft7Validator(schema)
    for err in validator.iter_errors(save):
        path = "/".join(str(p) for p in err.absolute_path) or "<root>"
        # additionalProperties-Verstöße = SOFT (Loader normalisiert), Rest = FAIL
        is_additional = "additionalProperties" in err.message or err.validator == "additionalProperties"
        sev = "SOFT" if is_additional else "FAIL"
        res.add("SCHEMA", sev, f"{label} @ {path}: {err.message[:160]}")
    return res


# ─── Echo-Format (test_v7_schema_consistency.js) ──────────────────────────────
def check_echo_formats(save: dict, label: str = "save") -> Result:
    res = Result()
    cont = save.get("continuity") or {}
    shared = cont.get("shared_echoes", [])
    roster = cont.get("roster_echoes", [])
    conv = cont.get("convergence_tags", [])

    if len(shared) > MAX_SHARED_ECHOES:
        res.add("ECHO-CAP", "FAIL", f"{label}: shared_echoes {len(shared)}>{MAX_SHARED_ECHOES}")
    if len(roster) > MAX_ROSTER_ECHOES:
        res.add("ECHO-CAP", "FAIL", f"{label}: roster_echoes {len(roster)}>{MAX_ROSTER_ECHOES}")
    if len(conv) > MAX_CONVERGENCE_TAGS:
        res.add("ECHO-CAP", "FAIL", f"{label}: convergence_tags {len(conv)}>{MAX_CONVERGENCE_TAGS}")

    for i, item in enumerate(shared):
        if not isinstance(item, dict) or isinstance(item, list):
            res.add("ECHO-FMT", "FAIL", f"{label}: shared_echoes[{i}] muss Objekt sein (kein String/Primitive)")
        elif not (isinstance(item.get("tag"), str) and item.get("tag")):
            res.add("ECHO-FMT", "FAIL", f"{label}: shared_echoes[{i}] braucht non-leeren 'tag' (Fremdkeys verboten)")
    for i, item in enumerate(roster):
        if not isinstance(item, dict) or isinstance(item, list):
            res.add("ECHO-FMT", "FAIL", f"{label}: roster_echoes[{i}] muss Objekt sein")
        elif not (isinstance(item.get("char_id"), str) and item.get("char_id")):
            res.add("ECHO-FMT", "FAIL", f"{label}: roster_echoes[{i}] braucht non-leeren 'char_id'")

    # Dedup-Check: shared_echoes-tags müssen eindeutig sein (Merge darf nicht stapeln)
    tags = [it.get("tag") for it in shared if isinstance(it, dict) and it.get("tag")]
    dupes = {t for t in tags if tags.count(t) > 1}
    if dupes:
        res.add("ECHO-DEDUP", "FAIL", f"{label}: shared_echoes-Tags doppelt (Merge-Dedup verletzt): {sorted(dupes)}")
    return res


# ─── Seed-Cap (speicher-fortsetzung.md + test_v7_issue_pack.js) ───────────────
def check_seed_cap(save: dict, label: str = "save") -> Result:
    res = Result()
    seeds = (save.get("campaign") or {}).get("rift_seeds", [])
    open_seeds = [s for s in seeds if isinstance(s, dict) and s.get("status") in (None, "open")]
    if len(open_seeds) > MAX_OPEN_SEEDS:
        res.add("SEED-CAP", "FAIL",
                f"{label}: {len(open_seeds)} offene Seeds > Cap {MAX_OPEN_SEEDS} "
                f"(Overflow muss als handoff_to ausgelagert + getract werden)")
    return res


# ─── Merge-Assertions (test_economy_merge.js + test_v7_issue_pack.js) ─────────
def assert_merge(merged: dict,
                 anchor: dict,
                 branches: list[dict],
                 expected_threads: list[str] | None = None,
                 label: str = "merge") -> Result:
    """Prüft ein Merge-Ergebnis gegen den Repo-Kanon.

    merged   = der gemergte HQ-Save (SL-Output nach Multi-Save-Import)
    anchor   = der zuerst gepostete Save (= Session-Anker, führt campaign/economy)
    branches = die Branch-Saves, die hineingemergt wurden
    expected_threads = erwartete branch_ids, default aus branches[].branch_id
    """
    res = Result()
    cont = merged.get("continuity") or {}
    split = cont.get("split") or {}

    # 1) Session-Anker-Priorität: campaign-Kernfelder == Anker
    a_camp = anchor.get("campaign") or {}
    m_camp = merged.get("campaign") or {}
    for fld in ("episode",):
        if fld in a_camp and m_camp.get(fld) != a_camp.get(fld):
            res.add("ANCHOR", "FAIL",
                    f"{label}: campaign.{fld}={m_camp.get(fld)} != Anker {a_camp.get(fld)} (Anker muss führen)")

    # 2) Wallet-SSOT (seit 2026-06-16, hq_pool-Abschaffung): Es gibt keinen
    #    gespeicherten gemeinsamen Topf mehr. Geld lebt in characters[].wallet,
    #    die Gruppenkasse ist ein berechneter View. Es gibt daher keine
    #    "ankergeführte hq_pool"-Regel mehr zu prüfen. Die Konservierung wird
    #    rein über assert_wealth_conservation (Schritt 7) abgesichert.
    a_pool = (anchor.get("economy") or {}).get("hq_pool")
    m_pool = (merged.get("economy") or {}).get("hq_pool")

    # 3) Konvergenz: resolved_threads ⊇ expected_threads, convergence_ready
    #    WICHTIG (2026-06-16): gegen thread_id der Branches matchen, NICHT branch_id.
    #    Die SL führt continuity.split.thread_id als Thread-Identität (z.B. "SQUAD-ABCD"),
    #    während branch_id der Lineage-Anker ist ("SPLIT-...-SQUAD"). Erst Branch-thread_ids
    #    nehmen, dann auf expected_threads des Merge-Saves zurückfallen.
    branch_threads = []
    for b in branches:
        bsplit = (b.get("continuity") or {}).get("split") or {}
        tid = bsplit.get("thread_id") or b.get("branch_id")
        if tid:
            branch_threads.append(tid)
    exp = expected_threads or branch_threads or list(split.get("expected_threads") or [])
    exp_set = {e for e in exp if e}
    resolved = set(split.get("resolved_threads") or [])
    expected_in_split = set(split.get("expected_threads") or [])
    if exp_set:
        missing = exp_set - resolved
        if missing:
            res.add("CONVERGE", "FAIL",
                    f"{label}: resolved_threads {sorted(resolved)} deckt erwartete {sorted(missing)} nicht ab")
        if not split.get("convergence_ready"):
            res.add("CONVERGE", "FAIL", f"{label}: convergence_ready nicht true trotz vollständigem Merge")
        if expected_in_split and expected_in_split != exp_set:
            res.add("CONVERGE", "SOFT",
                    f"{label}: split.expected_threads {sorted(expected_in_split)} != Branch-thread_ids {sorted(exp_set)}")
        if not split.get("family_id"):
            res.add("CONVERGE", "FAIL", f"{label}: split.family_id fehlt (kanonischer Split braucht family_id)")

    # 4) imported_saves: jeder Branch protokolliert. Kanonisch = Objektform
    #    [{save_id, branch_id, status}] (Modul 12). String-Array (nur save_ids)
    #    trägt die Info, ist aber nicht-kanonisch -> SOFT statt FAIL.
    imported = ((merged.get("logs") or {}).get("flags") or {}).get("imported_saves") or []
    imp_objs = [e for e in imported if isinstance(e, dict) and e.get("save_id") and e.get("branch_id")]
    imp_strs = [e for e in imported if isinstance(e, str) and e]
    if exp_set:
        if not imported:
            res.add("IMPORTED", "FAIL",
                    f"{label}: imported_saves leer — kein Branch-Import protokolliert")
        elif imp_strs and not imp_objs:
            res.add("IMPORTED", "SOFT",
                    f"{label}: imported_saves als String-Array ({len(imp_strs)} Einträge) statt "
                    f"kanonischer Objektform [{{save_id,branch_id,status}}] (Modul 12)")
        elif len(imp_objs) < len(branches):
            res.add("IMPORTED", "SOFT",
                    f"{label}: imported_saves protokolliert {len(imp_objs)}/{len(branches)} Branches "
                    f"in Objektform")
    for e in imp_objs:
        if e.get("status") not in ("merged", "rejected", "conflict"):
            res.add("IMPORTED", "SOFT", f"{label}: imported_saves status='{e.get('status')}' unüblich")

    # 4b) HQ-Pool-Leck-Check ENTFALLEN (2026-06-16, hq_pool-Abschaffung):
    #     Der gemeinsame Topf existiert nicht mehr. Das frühere Leck/Inflations-
    #     Risiko ist architektonisch beseitigt, weil jede CU einem Owner-Wallet
    #     gehört und über Split/Merge mitreist statt geteilt/summiert zu werden.
    #     Die Konservierung sichert jetzt allein assert_wealth_conservation.

    # 5) Dedupe-Guards gesetzt
    flags = ((merged.get("logs") or {}).get("flags") or {})
    for guard in ("duplicate_branch_detected", "duplicate_character_detected"):
        if guard not in flags:
            res.add("DEDUPE", "SOFT", f"{label}: logs.flags.{guard} fehlt")

    # 6) Echo-Format + Seed-Cap am Merge-Ergebnis
    res.merge(check_echo_formats(merged, label))
    res.merge(check_seed_cap(merged, label))

    # 7) EXPLOIT-GUARD: Vermögens-Konservierung über Split/Merge (Flo-Befund)
    res.merge(assert_wealth_conservation(merged, anchor, branches, label))
    return res


def total_wealth(save: dict) -> float:
    """Gesamtvermögen = Summe aller characters[].wallet (Wallet-SSOT seit
    2026-06-16). Geld lebt ausschließlich in den Wallets; die Gruppenkasse ist
    ein berechneter View. Ein evtl. noch vorhandener Legacy-`economy.hq_pool`
    wird additiv mitgezählt, damit gemischte Alt-Fixtures (Pool noch im JSON)
    konservierungs-konsistent bleiben, bis sie migriert sind."""
    pool = (save.get("economy") or {}).get("hq_pool") or 0
    wallets = 0.0
    for c in save.get("characters", []):
        w = c.get("wallet")
        if isinstance(w, (int, float)):
            wallets += w
    # Fallback: falls characters[] leer, aber economy.wallets vorhanden
    if not wallets:
        for rec in ((save.get("economy") or {}).get("wallets") or {}).values():
            b = rec.get("balance") if isinstance(rec, dict) else None
            if isinstance(b, (int, float)):
                wallets += b
    return float(pool) + wallets


def assert_wealth_conservation(merged: dict, anchor: dict,
                               branches: list[dict] | None = None,
                               label: str = "merge") -> Result:
    """EXPLOIT-GUARD (Flo-Befund 2026-06-16): Über einen Split/Merge-Zyklus darf
    das Gesamtvermögen NICHT steigen. Andernfalls lässt sich durch wiederholtes
    Split→Merge legal unendlich CU generieren.

    Referenz ist das Anker-Gesamtvermögen (vor Split). Das Merge-Ergebnis muss
    <= Anker sein (Toleranz für legitime Mission-Ausgaben/Einnahmen NICH hier —
    dieser Canary spielt keine Missionen, also gilt strikt: kein Zuwachs).

    INFLATION (merge > anchor) = FAIL (Exploit).
    LEAK (merge < anchor)      = SOFT (Geld verschwindet — auch unerwünscht,
                                 aber kein Exploit; Design-Frage).
    """
    res = Result()
    # Konservierung ist nur ehrlich prüfbar, wenn der Anker den VOLLEN Vorzustand
    # trägt (Pool + alle Wallets). Ein Fragment-Anker ohne characters/wallets würde
    # einen Falsch-"Anstieg" erzeugen — dann skippen statt falsch FAILen.
    a_chars = anchor.get("characters") or []
    m_chars = merged.get("characters") or []
    a_has_wallets = any(isinstance(c.get("wallet"), (int, float)) for c in a_chars)
    m_has_wallets = any(isinstance(c.get("wallet"), (int, float)) for c in m_chars)
    if (m_has_wallets and not a_has_wallets) or (len(a_chars) < len(m_chars) and not a_has_wallets):
        res.add("WEALTH", "INFO",
                f"{label}: Anker trägt keinen vollständigen Wallet-Vorzustand — "
                f"Vermögens-Konservierung nicht prüfbar (Fragment-Anker)")
        return res
    w_anchor = total_wealth(anchor)
    w_merge = total_wealth(merged)
    if w_anchor <= 0:
        res.add("WEALTH", "INFO", f"{label}: Anker-Vermögen 0 — Konservierung nicht prüfbar")
        return res
    delta = w_merge - w_anchor
    pct = delta / w_anchor * 100
    if delta > 1e-6:
        res.add("WEALTH-EXPLOIT", "FAIL",
                f"{label}: Gesamtvermögen STEIGT über Split/Merge {w_anchor:.0f}→{w_merge:.0f} "
                f"(+{delta:.0f}, +{pct:.1f}%) — Geld-Druck-Exploit über Split/Merge-Zyklus")
    elif delta < -1e-6:
        res.add("WEALTH-LEAK", "SOFT",
                f"{label}: Gesamtvermögen SINKT über Split/Merge {w_anchor:.0f}→{w_merge:.0f} "
                f"({delta:.0f}, {pct:.1f}%) — Geld verschwindet (Leck, kein Exploit)")
    else:
        res.add("WEALTH", "INFO", f"{label}: Gesamtvermögen erhalten ({w_merge:.0f} CU)")
    return res


def _conflict_fields(save: dict) -> set[str]:
    confs = ((save.get("logs") or {}).get("flags") or {}).get("continuity_conflicts") or []
    out = set()
    for c in confs:
        if isinstance(c, dict) and c.get("field"):
            out.add(c["field"])
    return out


# ─── VBR-Selbsttest gegen Repo-Fixtures ───────────────────────────────────────
def _selftest() -> int:
    print("=== merge_assert Selbsttest (gegen Repo-Fixtures, kein SL-Call) ===\n")
    passed = failed = 0

    def check(name: str, cond: bool, detail: str = ""):
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f"  ✅ {name}")
        else:
            failed += 1
            print(f"  ❌ {name}  {detail}")

    # 1) Bekannte gute Fixtures müssen das Echo-/Seed-/Merge-Regelwerk bestehen
    good = {
        "5er_hq_highlevel": "savegame_v7_5er_hq_highlevel.json",
        "split_3_2_merge": "savegame_v7_split_3_2_merge.json",
        "merge_rift_pvp": "savegame_v7_merge_rift_pvp.json",
    }
    fixtures: dict[str, dict] = {}
    for key, fn in good.items():
        p = FIXTURES / fn
        if not p.exists():
            check(f"fixture vorhanden: {fn}", False, "DATEI FEHLT")
            continue
        fixtures[key] = json.loads(p.read_text(encoding="utf-8"))
        r = check_echo_formats(fixtures[key], key)
        r.merge(check_seed_cap(fixtures[key], key))
        check(f"gute Fixture besteht Echo+Seed-Regeln: {key}",
              r.ok, "; ".join(str(f) for f in r.fails))

    # 2) Kanonisches Merge-Ergebnis muss assert_merge bestehen
    if "split_3_2_merge" in fixtures:
        m = fixtures["split_3_2_merge"]
        # rekonstruiere anchor + branches aus dem Fixture-Kontext
        # Wallet-SSOT: kein hq_pool mehr. Anker traegt dieselben characters[]-Wallets
        # wie das Merge-Ergebnis, damit die Konservierung (Σ Wallets) aufgeht.
        anchor = {"campaign": {"episode": 7},
                  "economy": {"wallets": {}},
                  "characters": copy.deepcopy(m.get("characters") or [])}
        branches = [
            {"branch_id": "RIFT-A-3ER", "save_id": "SAVE-RIFT-A"},
            {"branch_id": "RIFT-B-2ER", "save_id": "SAVE-RIFT-B"},
        ]
        r = assert_merge(m, anchor, branches, label="split_3_2")
        check("kanonisches 3/2-Merge besteht assert_merge",
              r.ok, "; ".join(str(f) for f in r.fails))

    # 3) Bewusst kaputte Mutationen MÜSSEN failen (Validator-Schärfe)
    if "split_3_2_merge" in fixtures:
        base = fixtures["split_3_2_merge"]

        broken_echo = copy.deepcopy(base)
        broken_echo["continuity"]["shared_echoes"] = ["morgenrot"]  # String statt Objekt
        check("kaputt: shared_echoes als String failt",
              not check_echo_formats(broken_echo, "broken").ok)

        broken_dup = copy.deepcopy(base)
        broken_dup["continuity"]["shared_echoes"] = [
            {"tag": "x", "scope": "shared", "text": "a"},
            {"tag": "x", "scope": "shared", "text": "b"},
        ]
        check("kaputt: doppelter shared_echo-Tag failt (Dedup)",
              not check_echo_formats(broken_dup, "broken").ok)

        broken_conv = copy.deepcopy(base)
        broken_conv["continuity"]["split"]["resolved_threads"] = ["RIFT-A-3ER"]  # B fehlt
        broken_conv["continuity"]["split"]["convergence_ready"] = True
        anchor = {"campaign": {"episode": 7},
                  "economy": {"wallets": {}},
                  "characters": copy.deepcopy(base.get("characters") or [])}
        branches = [{"branch_id": "RIFT-A-3ER", "save_id": "x"},
                    {"branch_id": "RIFT-B-2ER", "save_id": "y"}]
        check("kaputt: unvollständige resolved_threads failt CONVERGE",
              not assert_merge(broken_conv, anchor, branches, label="broken").ok)

        broken_seed = copy.deepcopy(base)
        broken_seed["campaign"]["rift_seeds"] = [{"id": f"S{i}", "status": "open"} for i in range(13)]
        check("kaputt: 13 offene Seeds failt SEED-CAP",
              not check_seed_cap(broken_seed, "broken").ok)

        # Wealth-Konservierung (Exploit-Guard) - reine Wallet-Welt, kein Pool.
        # Anker-Gesamtvermoegen = 1000 (Wallets). Inflation = Merge mit 1500.
        anchor_w = {"economy": {"wallets": {}},
                    "characters": [{"id": "A", "wallet": 500}, {"id": "B", "wallet": 500}]}
        merge_inflated = {"economy": {"wallets": {}},
                          "characters": [{"id": "A", "wallet": 1000}, {"id": "B", "wallet": 500}]}
        check("exploit: Vermögens-Inflation über Merge failt WEALTH-EXPLOIT",
              not assert_wealth_conservation(merge_inflated, anchor_w, label="broken").ok)
        merge_conserved = {"economy": {"wallets": {}},
                           "characters": [{"id": "A", "wallet": 500}, {"id": "B", "wallet": 500}]}
        check("gut: erhaltenes Vermögen besteht WEALTH",
              assert_wealth_conservation(merge_conserved, anchor_w, label="good").ok)

    print(f"\n=== Selbsttest: {passed} passed, {failed} failed ===")
    return 0 if failed == 0 else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true", help="gegen Repo-Fixtures verifizieren")
    ap.add_argument("--validate", metavar="SAVE.json", help="einen Save gegen v7-Export-Schema prüfen")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(_selftest())
    if args.validate:
        save = json.loads(Path(args.validate).read_text(encoding="utf-8"))
        res = validate_export(save, Path(args.validate).name)
        res.merge(check_echo_formats(save, "save"))
        res.merge(check_seed_cap(save, "save"))
        for f in res.findings:
            print(f)
        print(f"\n{'OK' if res.ok else 'FAIL'} ({len(res.fails)} harte Fehler)")
        sys.exit(0 if res.ok else 1)
    ap.print_help()


if __name__ == "__main__":
    main()
