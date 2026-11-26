#!/usr/bin/env python3
"""
tests/mmo_sim/test_arena_gast_wallet_intake_normalization_2026_11_26.py —
Arena-Gast Wallet-Intake-Normalisierung (Stage 3 Minimalfix, 2026-11-26).

Befund (Part B, quell-verifiziert, s. Report): beide Importcaller
(`_cmd_import` tui.py, `_decide_participant_save_intake` tui.py) teilen
`import_export.preview_import_tolerant` -- dessen EINZIGE Toleranzstufe
(`has_residual_structural_cap_overflow`) liefert fuer einen reinen
Wallet-Typfehler (`economy.wallets.<char_id>` als nackte Zahl statt
`{"balance": N}`) `False` (die Projektion macht den Kandidaten bereits
VOLLSTAENDIG gueltig -> kein Cap-Rest) -> harte Ablehnung, OBWOHL die
vorhandene, wertgleiche Projektion (`save_compatibility.evaluate_with_
wallet_projection`) den Kandidaten laengst akzeptiert. Selbst wenn toleriert
wuerde, schrieben beide Caller bisher unconditional den ROHEN Block
(`json.loads(raw)`), NIE den projizierten Kandidaten.

Fix (dieser Testdatei begleitend, s. Report fuer den vollen `git diff`):
  1. `import_export.ImportPreview` bekommt das additive Feld
     `canonical_block: dict | None = None`.
  2. `preview_import_tolerant` prueft VOR dem Cap-Ueberlauf-Gate
     `save_compatibility.evaluate_with_wallet_projection(obj, cid)` -- bei
     `accepted and used_projection` liefert sie den normalisierten
     Kandidaten ueber `canonical_block`, `tolerated` bleibt `False`.
  3. Beide Caller (`tui.py` `_cmd_import`/`_decide_participant_save_intake`)
     schreiben `preview.canonical_block if ... is not None else
     json.loads(raw...)` statt unconditional `json.loads(raw...)`.

STATIC-Fixture (Provenienz sha256 `05a51f2305a0b08b8e19c25843034c8781cab1ce
db635a4c1066250d1f890341`, eingebettetes Save-JSON `SAVE-TEST-CHR7731-
STATIC-HQ-01`, char_id `CHR-7731`, `economy.wallets.CHR-7731 == 100`): Die
Fixture liegt AUSSERHALB dieses Repo-Checkouts (nicht Teil von ZEITRISS-md)
-- der eingebettete Save-JSON-Block wird daher hier als literale Konstante
(`_STATIC_SAVE_BLOCK`, byte-identisch zum extrahierten JSON) gefuehrt statt
zur Testlaufzeit von dort gelesen zu werden (Portabilitaet: dieser Testpfad
muss auch unabhaengig von der urspruenglichen Testumgebung lauffaehig
bleiben).

RED-Beleg (`test_red_...`): rekonstruiert dynamisch die PRE-FIX-Fassung von
`preview_import_tolerant` durch Textsubtraktion der beiden additiven
Fix-Bloecke aus der AKTUELLEN (gepatchten) Quelldatei (kein git-Revert,
reiner String-Vergleich) und beweist, dass diese Fassung das STATIC-JSON
weiterhin mit `MalformedImportError` ablehnt -- deckungsgleich mit dem
empirischen Befund aus Part B (`B-import-repro-report.md`).

Pure Python + pytest (`test_*`-Funktionen), zusaetzlich lauffaehig als
eigenstaendiges Skript (`python3 <datei>`)."""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save  # noqa: E402

from mmo_sim.domain.zeitriss import import_export  # noqa: E402
from mmo_sim.domain.zeitriss import save_compatibility  # noqa: E402
from mmo_sim.ui.tui import TuiSession, _decide_participant_save_intake  # noqa: E402

_IMPORT_EXPORT_SRC_PATH = (
    _REPO_ROOT / "mmo_sim" / "domain" / "zeitriss" / "import_export.py"
)

# ── STATIC-Fixture (eingebettetes Save-JSON, literal, Provenienz s. oben) ──

_STATIC_SAVE_BLOCK: dict = {
    "v": 7, "zr": "4.2.6", "save_id": "SAVE-TEST-CHR7731-STATIC-HQ-01",
    "parent_save_id": None, "merge_id": None, "branch_id": "ANCHOR-test-static",
    "campaign": {
        "episode": 1, "mission": 0, "px": 0, "px_state": "stable", "heat": 0,
        "mode": "mixed", "epoch": None, "rift_seeds": [], "entry_choice_skipped": False,
        "episode_start": None, "episode_end": None,
    },
    "characters": [{
        "id": "CHR-7731", "name": "Yara Kessler", "callsign": "STATIC", "rank": "Rekrut",
        "lvl": 1, "xp": 0,
        "origin": {"epoch": "frühes 21. Jh.", "hominin": "Homo sapiens sapiens", "role": "freie Kurierin / Infiltratorin"},
        "attr": {"STR": 2, "GES": 5, "INT": 4, "CHA": 3, "TEMP": 2, "SYS": 2},
        "lp": 10, "lp_max": 10, "stress": 0, "has_psi": False, "sys_installed": 0,
        "talents": [{
            "name": "Lautlose Bewegung", "tier": "Basis",
            "effect": "+2 auf GES-Proben beim Schleichen, Anpirschen und lautlosem Vorgehen in Gebäuden. Routine-Schleichen ohne Zeitdruck gilt als automatischer Erfolg.",
        }],
        "equipment": [
            {"name": "Schallgedämpfte Walther PPS", "type": "weapon", "tier": 1},
            {"name": "Einbruchswerkzeug-Set", "type": "gadget", "tier": 0},
            {"name": "ITI-Felduniform (zeitlos)", "type": "armor", "tier": 0},
            {"name": "Comlink-Ohrstöpsel", "type": "gadget", "tier": 0},
        ],
        "implants": [],
        "history": {
            "background": "Fünf Jahre freie Kurierin durch Europa — keine Fragen, pünktliche Lieferung. Das ITI hat sie rekrutiert, weil sie dreimal unbemerkt durch gesicherte Gebäude spaziert ist. Erster Feldeinsatz: Theta-7-Extraktion, sauber abgeschlossen.",
            "milestones": ["Theta-7-Extraktion: Datenpaket gesichert, unentdeckt, kein Alarm."],
        },
        "carry": [
            {"name": "Schallgedämpfte Walther PPS", "type": "weapon", "tier": 1},
            {"name": "Einbruchswerkzeug-Set", "type": "gadget", "tier": 0},
            {"name": "ITI-Felduniform (zeitlos)", "type": "armor", "tier": 0},
            {"name": "Comlink-Ohrstöpsel", "type": "gadget", "tier": 0},
        ],
        "quarters_stash": [],
        "vehicles": {
            "epoch_vehicle": {"id": "VEH-7731", "name": "ITI-Standardtransporter", "type": "vehicle", "tier": 1, "upgrades": []},
            "availability": {"ready_every_missions": 4, "next_ready_in": 0},
            "legendary_temporal_ship": None,
        },
        "reputation": {
            "iti": 0, "faction": "nicht zugeordnet",
            "factions": {"ordo_mnemonika": 0, "chrono_symmetriker": 0, "kausalklingen": 0, "zerbrechliche_ewigkeit": 0},
        },
        "wallet": 100, "level_history": {},
    }],
    "economy": {"wallets": {"CHR-7731": 100}},
    "research": {"projects": []},
    "logs": {
        "trace": ["MS-TEST · Theta-7-Extraktion · Yara Kessler / STATIC · Ergebnis: Datenpaket gesichert, unentdeckt · Stress-Delta: 0 · Heat-Delta: 0"],
        "hud": [], "psi": [], "arena_psi": [], "market": [], "artifact_log": [],
        "notes": ["Testszene: Theta-7-Infiltration abgeschlossen. GES-Probe Schleichen: W6[3]+2+2=7 vs SG 6, Erfolg. Datenpaket an Duty-Desk übergeben."],
        "flags": {
            "runtime_version": "4.2.6", "chronopolis_unlocked": False, "imported_saves": [],
            "duplicate_branch_detected": False, "duplicate_character_detected": False, "continuity_conflicts": [],
        },
    },
    "summaries": {
        "summary_last_episode": "", "summary_last_rift": "",
        "summary_active_arcs": "Testlauf Theta-7 abgeschlossen. Yara Kessler bereit für ersten regulären Einsatz.",
    },
    "continuity": {
        "last_seen": {"mode": "hq", "episode": 1, "mission": 0, "location": "HQ — Quarzatrium"},
        "split": {"family_id": None, "thread_id": None, "expected_threads": [], "resolved_threads": [], "convergence_ready": False},
        "roster_echoes": [], "shared_echoes": [], "convergence_tags": [], "npc_roster": [], "active_npc_ids": [],
    },
    "arc": {"factions": {}, "questions": [], "hooks": []},
    "ui": {
        "gm_style": "verbose", "suggest_mode": False, "action_mode": "uncut", "intro_seen": True,
        "dice": {"debug_rolls": True}, "contrast": "standard", "badge_density": "standard",
        "output_pace": "normal", "voice_profile": "gm_second_person",
    },
    "arena": {
        "active": False, "phase": "idle", "queue_state": "idle", "mode": "single", "tier": 1,
        "previous_mode": None, "resume_token": None, "contract_id": None, "streak": 0,
        "pending_rewards": {"cu": 0, "xp": 0, "arena_rep": 0, "multiplier": 1, "risk": "none"},
        "banked_rewards": {"cu": 0, "xp": 0, "arena_rep": 0},
        "rewarded_runs_this_contract": 0, "first_wins": {}, "defeated_types": [],
        "last_reward_episode": None, "wins_player": 0, "wins_opponent": 0, "match_policy": "sim",
    },
}

# Cap-Ueberlauf-Fixtures (unveraendert aus dem bestehenden J4-Toleranzpfad-
# Test wiederverwendet, reiner Lesezugriff -- kein Handreinigen).
_J4_FIXTURE_DIR = _HERE / "fixtures" / "j4_tolerant_import"
_P01_PATH = _J4_FIXTURE_DIR / "p01_latch.json"


def _static_raw() -> str:
    return json.dumps(_STATIC_SAVE_BLOCK)


# ── Fixture-Vorbedingung: STATIC-JSON scheitert am harten preview_import ──

def test_static_fixture_fails_hard_preview_precondition():
    try:
        import_export.preview_import(_static_raw())
        assert False, "Vorbedingung verletzt: STATIC-JSON sollte am harten preview_import scheitern"
    except import_export.MalformedImportError as e:
        assert "economy/wallets/CHR-7731" in str(e) or "wallets" in str(e), str(e)


# ── RED: rekonstruierte PRE-FIX-Fassung lehnt STATIC-JSON weiterhin ab ─────

def _load_reconstructed_pre_fix_module():
    """Entfernt per exaktem String-Abgleich die beiden additiven Fix-
    Bloecke aus der AKTUELLEN Quelldatei und laedt das Ergebnis als
    eigenstaendiges Modul unter dem korrekten Package-Kontext
    (`mmo_sim.domain.zeitriss`) -- kein git-Revert, reine Textsubtraktion.
    Schlaegt LAUT fehl (statt stillschweigend zu uebernehmen), falls einer
    der beiden Bloecke nicht mehr exakt einmal vorkommt (z.B. nach einer
    spaeteren Umformulierung des Fixes)."""
    patched_src = _IMPORT_EXPORT_SRC_PATH.read_text(encoding="utf-8")

    field_block = (
        '    tolerated: bool = False\n'
        '    warnings: tuple[str, ...] = ()\n'
        '    # Stage 3 (Arena-Gast Wallet-Intake-Normalisierung, 2026-11-26): additives\n'
        '    # Feld, Default None haelt JEDEN bestehenden Aufrufer bytegleich. Wird NUR\n'
        '    # vom Normalisierungszweig unten gesetzt (wertgleicher, schema-gueltiger\n'
        '    # Kandidat) -- `tolerated` bleibt in diesem Fall False (kein Cap-Rest).\n'
        '    canonical_block: dict | None = None\n'
    )
    field_block_orig = (
        '    tolerated: bool = False\n'
        '    warnings: tuple[str, ...] = ()\n'
    )
    branch_block = (
        '\n'
        '    # Stage 3 (Arena-Gast Wallet-Intake-Normalisierung, 2026-11-26): VOR dem\n'
        '    # Cap-Ueberlauf-Gate pruefen, ob die wertgleiche Wallet-Projektion\n'
        '    # (`save_compatibility.evaluate_with_wallet_projection`) den Block\n'
        '    # vollstaendig gueltig macht. Der Owner-/Identity-Guard steckt IN dieser\n'
        '    # Funktion (`validate_save_block`) -- ein fremd/falsch gebundener\n'
        '    # Envelope scheitert dort und wird NICHT gerettet. Lazy-Import wie der\n'
        '    # bestehende `core.save_correction`-Import unten (kein Zyklus: `domain.\n'
        '    # zeitriss.save_compatibility` importiert nur `save_validation`).\n'
        '    from . import save_compatibility\n'
        '\n'
        '    projection_outcome = save_compatibility.evaluate_with_wallet_projection(obj, cid)\n'
        '    if projection_outcome.accepted and projection_outcome.used_projection:\n'
        '        proj_level = None\n'
        '        proj_chars = obj.get("characters")\n'
        '        if isinstance(proj_chars, list) and proj_chars and isinstance(proj_chars[0], dict):\n'
        '            proj_level = proj_chars[0].get("lvl", proj_chars[0].get("level"))\n'
        '        return ImportPreview(\n'
        '            char_id=cid, level=proj_level, n_characters=n, single_char_ok=True,\n'
        '            canonical_block=projection_outcome.canonical_block,\n'
        '        )\n'
        '\n'
    )
    assert patched_src.count(field_block) == 1, "Fix-Feldblock nicht exakt einmal gefunden -- RED-Rekonstruktion ungueltig"
    assert patched_src.count(branch_block) == 1, "Fix-Normalisierungszweig nicht exakt einmal gefunden -- RED-Rekonstruktion ungueltig"
    pre_fix_src = patched_src.replace(field_block, field_block_orig).replace(branch_block, "\n")
    assert "canonical_block" not in pre_fix_src, "Rekonstruktion unvollstaendig -- canonical_block noch vorhanden"
    assert "evaluate_with_wallet_projection" not in pre_fix_src, "Rekonstruktion unvollstaendig -- Normalisierungszweig noch vorhanden"

    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td) / "import_export_pre_fix_redcheck.py"
        tmp_path.write_text(pre_fix_src, encoding="utf-8")
        import importlib.util
        temp_mod_name = "mmo_sim.domain.zeitriss._import_export_pre_fix_redcheck"
        spec = importlib.util.spec_from_file_location(temp_mod_name, tmp_path, submodule_search_locations=[])
        mod = importlib.util.module_from_spec(spec)
        mod.__package__ = "mmo_sim.domain.zeitriss"
        sys.modules[temp_mod_name] = mod
        try:
            spec.loader.exec_module(mod)
        finally:
            del sys.modules[temp_mod_name]
        return mod


def test_red_pre_fix_reconstruction_rejects_static_wallet_type_error():
    pre_fix_mod = _load_reconstructed_pre_fix_module()
    try:
        pre_fix_mod.preview_import_tolerant(_static_raw())
        assert False, "RED-Vorbedingung verletzt: pre-fix sollte STATIC-JSON ablehnen"
    except pre_fix_mod.MalformedImportError as e:
        assert "economy/wallets/CHR-7731" in str(e) or "wallets" in str(e), str(e)


def test_red_pre_fix_raw_write_candidate_stays_schema_invalid_number():
    """Write-Crux (pre-fix): ohne jede Preview-Gate-Passage wuerde
    `json.loads(raw)` den rohen, schema-ungueltigen Zahlenwert liefern --
    GENAU der Zustand, den beide Caller vor dem Fix unconditional
    geschrieben haetten."""
    written_would_be = json.loads(_static_raw())
    wallet_val = written_would_be["economy"]["wallets"]["CHR-7731"]
    assert wallet_val == 100
    assert not isinstance(wallet_val, dict), "pre-fix Write-Kandidat war eine nackte Zahl, kein {'balance': ...}-Objekt"


# ── GRÜN: preview_import_tolerant liefert canonical_block, tolerated=False ─

def test_green_preview_import_tolerant_normalizes_static_wallet():
    preview = import_export.preview_import_tolerant(_static_raw())
    assert preview.tolerated is False, "Wallet-Normalisierung ist ein voll gueltiger Kandidat, KEIN Cap-Toleranzrest"
    assert preview.char_id == "CHR-7731"
    assert preview.single_char_ok is True
    assert preview.canonical_block is not None
    assert preview.canonical_block["economy"]["wallets"]["CHR-7731"] == {"balance": 100}
    # Wertgleich: der Betrag selbst bleibt unangetastet, nur die Form aendert sich.
    assert preview.canonical_block["characters"][0]["id"] == "CHR-7731"


# ── GRÜN: beide Caller schreiben den normalisierten Block ──────────────────

def test_green_decide_participant_save_intake_writes_normalized_block():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        outcome = _decide_participant_save_intake(
            catalog_dir=d / "catalog", onboarding_dir=d / "onboarding", run_dir=None,
            participant_id="guest-static-test", raw_save_text=_static_raw(),
        )
    assert outcome.action == "register_new"
    assert outcome.char_id == "CHR-7731"
    assert outcome.tolerated is False
    assert outcome.block is not None
    assert outcome.block["economy"]["wallets"]["CHR-7731"] == {"balance": 100}


def _scripted_input(lines: list[str]):
    it = iter(lines)

    def _fn(prompt: str = "") -> str:
        try:
            return next(it)
        except StopIteration:
            raise EOFError()
    return _fn


def test_green_cmd_import_writes_normalized_block_via_normal_write():
    from mmo_sim.domain.zeitriss import catalog

    single_line_raw = json.dumps(_STATIC_SAVE_BLOCK)
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_scripted_input(["i", single_line_raw, "ENDE", "j", "x"]),
            print_fn=printed.append,
        )
        rc = session.run()
        assert rc == 0, printed
        # Kein tolerierter Best-Effort-Zweig: die Wallet-Normalisierung ist
        # ein voll gueltiger Kandidat, zeigt daher NIE die Toleranzwarnung.
        assert not any("TOLERIERTER FREMDIMPORT" in p for p in printed), printed
        stored = catalog.load_figure_save(d / "catalog", "p1", "CHR-7731")
        assert stored is not None
        assert stored["economy"]["wallets"]["CHR-7731"] == {"balance": 100}


# ── Wertgleichheit: abweichender Betrag normalisiert, NICHT angeglichen ────

def test_amount_200_normalizes_to_balance_200_not_coerced_to_other_value():
    block = copy.deepcopy(_STATIC_SAVE_BLOCK)
    block["economy"]["wallets"]["CHR-7731"] = 200
    preview = import_export.preview_import_tolerant(json.dumps(block))
    assert preview.tolerated is False
    assert preview.canonical_block["economy"]["wallets"]["CHR-7731"] == {"balance": 200}


# ── Guard (a): Owner-/Identity-Guard IN evaluate_with_wallet_projection ────

def test_guard_owner_identity_mismatch_not_rescued_by_projection():
    """Direkter Nachweis des in `save_compatibility.evaluate_with_wallet_
    projection` eingebauten Owner-/Identity-Guards (`validate_save_block`):
    ein fremd erwarteter char_id wird NICHT durch die Wallet-Projektion
    gerettet, obwohl der Wallet-Fehler selbst normalisierbar waere."""
    outcome = save_compatibility.evaluate_with_wallet_projection(_STATIC_SAVE_BLOCK, "CHR-FREMD-0000")
    assert outcome.accepted is False
    assert outcome.used_projection is False
    assert outcome.canonical_block is None


# ── Guard (b): echter nicht-Wallet-Strukturfehler bleibt hart abgelehnt ────

def test_guard_non_wallet_structural_failure_stays_hard_rejected():
    broken = copy.deepcopy(_STATIC_SAVE_BLOCK)
    del broken["characters"][0]["id"]
    raw_broken = json.dumps(broken)
    try:
        import_export.preview_import(raw_broken)
        assert False, "Vorbedingung verletzt: sollte am harten preview_import scheitern"
    except import_export.MalformedImportError as original:
        original_msg = str(original)
    try:
        import_export.preview_import_tolerant(raw_broken)
        assert False, "fehlender char_id-Block muss hart abgelehnt bleiben (Owner-Guard)"
    except import_export.MalformedImportError as e:
        assert str(e) == original_msg, "Toleranzpfad darf bei Hartablehnung KEINE neue/geloskerte Meldung erzeugen"


# ── Guard (c): bestehender Cap-Ueberlauf-Toleranzfall bleibt unveraendert ──

def test_guard_existing_cap_overflow_case_stays_tolerated_true_raw_block():
    raw = _P01_PATH.read_text(encoding="utf-8")
    preview = import_export.preview_import_tolerant(raw)
    assert preview.tolerated is True
    assert preview.canonical_block is None
    assert any("maxItems" in w for w in preview.warnings)


def test_mixed_wallet_and_cap_overflow_falls_through_to_cap_overflow_branch():
    """Mischfall (Wallet-Fehler + Cap-Rest): `evaluate_with_wallet_
    projection` normalisiert den Wallet-Teil, aber der verbleibende
    Cap-Ueberlauf bleibt -- `accepted=False` -> faellt korrekt in den
    bestehenden Cap-Ueberlauf-Zweig (`tolerated=True`, Roh-Block, NICHT
    `tolerated=False` mit nur teilweise normalisiertem Kandidaten)."""
    d = json.loads(_P01_PATH.read_text(encoding="utf-8"))
    mixed = copy.deepcopy(d)
    char_id = mixed["characters"][0]["id"]
    mixed["economy"]["wallets"][char_id] = 400  # auf nackte Zahl zuruecksetzen
    raw_mixed = json.dumps(mixed)

    outcome = save_compatibility.evaluate_with_wallet_projection(mixed, char_id)
    assert outcome.accepted is False, "Vorbedingung: Cap-Rest darf die Projektion NICHT vollstaendig gueltig machen"

    preview = import_export.preview_import_tolerant(raw_mixed)
    assert preview.tolerated is True
    assert preview.canonical_block is None
    assert any("wallets" in w for w in preview.warnings)
    assert any("maxItems" in w for w in preview.warnings)


# ── Erfolgspfad bleibt additiv bytegleich (canonical_block=None, s. J4) ────

def test_healthy_block_via_tolerant_path_canonical_block_stays_none():
    block = full_v7_save("chrono-arena-gast-healthy", level=3)
    raw = import_export.export_save_text(block)

    plain = import_export.preview_import(raw)
    tolerant = import_export.preview_import_tolerant(raw)

    assert tolerant.tolerated is False
    assert tolerant.canonical_block is None
    assert tolerant.char_id == plain.char_id
    assert tolerant.level == plain.level
    assert tolerant.n_characters == plain.n_characters
    assert tolerant.single_char_ok == plain.single_char_ok


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"OK   {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
        except Exception:
            failed += 1
            print(f"ERROR {t.__name__}:")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} Tests bestanden.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
