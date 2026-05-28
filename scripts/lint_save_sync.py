#!/usr/bin/env python3
"""Save-Sync-Handover lint: anchors, macros, in-fiction beats, doc cross-refs."""
from __future__ import annotations

from pathlib import Path

from scripts.lib_repo import repo_root, read_text
from scripts.lib_lint import ok


def main() -> int:
    root = repo_root(Path(__file__))

    # Load toolkit (same compose as lint_chronopolis)
    tk = ""
    try:
        tk += read_text(root / "systems" / "toolkit-gpt-spielleiter.md") + "\n"
    except FileNotFoundError:
        pass
    try:
        tk += read_text(root / "internal" / "runtime" / "toolkit-runtime-makros.md")
    except FileNotFoundError:
        pass

    all_ok = True

    # 1) LINT-Anchor-Coverage: jedes neue Macro hat seinen Anchor im Toolkit
    for tag in [
        r"LINT:SAVE_SYNC_HANDOVER",
        r"LINT:SAVE_SYNC_PRE_BRIEFING",
        r"LINT:SAVE_SYNC_PRE_RIFT",
        r"LINT:SAVE_SYNC_PRE_CHRONO_GATE",
        r"LINT:SAVE_SYNC_PRE_ARENA",
        r"LINT:SAVE_SYNC_POST_DEBRIEF",
        r"LINT:SAVE_SYNC_POST_CHRONO",
        r"LINT:SAVE_SYNC_POST_ARENA",
        r"LINT:HQ_HUB_ROUTER",
    ]:
        all_ok &= ok(tag, f"{tag} present", tk)

    # 2) Macros existieren mit erwarteten Signaturen
    all_ok &= ok(
        r"macro\s+save_sync_offer\(transition_type\)",
        "save_sync_offer(transition_type) macro present",
        tk,
    )
    all_ok &= ok(
        r"macro\s+save_sync_pre_briefing\(\)",
        "save_sync_pre_briefing() macro present",
        tk,
    )
    all_ok &= ok(
        r"macro\s+save_sync_pre_rift\(\)",
        "save_sync_pre_rift() macro present",
        tk,
    )
    all_ok &= ok(
        r"macro\s+save_sync_pre_chrono_gate\(\)",
        "save_sync_pre_chrono_gate() macro present",
        tk,
    )
    all_ok &= ok(
        r"macro\s+save_sync_pre_arena\(\)",
        "save_sync_pre_arena() macro present",
        tk,
    )
    all_ok &= ok(
        r"macro\s+save_sync_post_debrief\(\)",
        "save_sync_post_debrief() macro present",
        tk,
    )
    all_ok &= ok(
        r"macro\s+save_sync_post_chrono\(\)",
        "save_sync_post_chrono() macro present",
        tk,
    )
    all_ok &= ok(
        r"macro\s+save_sync_post_arena\(\)",
        "save_sync_post_arena() macro present",
        tk,
    )
    all_ok &= ok(
        r"macro\s+hq_hub_router_show\(\)",
        "hq_hub_router_show() macro present",
        tk,
    )

    # 3) Save-Angebot-Strings im Sync-Offer-Macro
    all_ok &= ok(
        r"Kodex:\s+HQ-Stand stabil\.\s+Deepsave m\u00f6glich\.",
        "Sync-offer Kodex 'HQ-Stand stabil' string present",
        tk,
    )
    all_ok &= ok(
        r"Kodex:\s+Sync vor \u00dcbergang empfohlen [\u2014-] !save f\u00fcr Stand sichern\.",
        "Sync-offer Kodex 'Sync vor Übergang' string present",
        tk,
    )

    # 4) In-Fiction-Beats vorhanden (Lore-Anker pro Übergangstyp)
    all_ok &= ok(
        r"Sprungvorbereitung",
        "Pre-briefing in-fiction beat ('Sprungvorbereitung') present",
        tk,
    )
    all_ok &= ok(
        r"Rift-Koordinate aktiviert",
        "Pre-rift in-fiction beat ('Rift-Koordinate aktiviert') present",
        tk,
    )
    all_ok &= ok(
        r"Schleuse verriegelt",
        "Pre-chronopolis in-fiction beat ('Schleuse verriegelt') present",
        tk,
    )
    all_ok &= ok(
        r"Match-Lock",
        "Pre-arena in-fiction beat ('Match-Lock') present",
        tk,
    )
    all_ok &= ok(
        r"Nullzeit-Andocken",
        "Post-debrief in-fiction beat ('Nullzeit-Andocken') present",
        tk,
    )
    all_ok &= ok(
        r"Schleuse entriegelt",
        "Post-chronopolis in-fiction beat ('Schleuse entriegelt') present",
        tk,
    )
    all_ok &= ok(
        r"Match-Recap eingeh\u00e4ngt",
        "Post-arena in-fiction beat ('Match-Recap eingehängt') present",
        tk,
    )

    # 5) HQ-Hub-Router enthält die Standard-Optionen
    all_ok &= ok(
        r"Briefing anfordern",
        "HQ-Hub-Router contains 'Briefing anfordern'",
        tk,
    )
    all_ok &= ok(
        r"HQ erkunden",
        "HQ-Hub-Router contains 'HQ erkunden'",
        tk,
    )
    all_ok &= ok(
        r"Auto-HQ",
        "HQ-Hub-Router contains 'Auto-HQ'",
        tk,
    )
    all_ok &= ok(
        r"Chronopolis-Schleuse",
        "HQ-Hub-Router contains 'Chronopolis-Schleuse'",
        tk,
    )
    all_ok &= ok(
        r"Rift-Board",
        "HQ-Hub-Router contains 'Rift-Board'",
        tk,
    )
    all_ok &= ok(
        r"Arena-Router",
        "HQ-Hub-Router contains 'Arena-Router'",
        tk,
    )

    # 6) Modul 12 (speicher-fortsetzung.md) hat den neuen § Save-Sync-Handover
    sv = root / "systems" / "gameflow" / "speicher-fortsetzung.md"
    if sv.exists():
        sv_text = read_text(sv)
        all_ok &= ok(
            r"##\s+Save-Sync-Handover an Abschnitts\u00fcberg\u00e4ngen\s*\{#save-sync-handover\}",
            "Modul 12 has §Save-Sync-Handover with explicit anchor",
            sv_text,
        )
        all_ok &= ok(
            r"Acht verbindliche Sync-Punkte",
            "Modul 12 lists 'Acht verbindliche Sync-Punkte'",
            sv_text,
        )
        all_ok &= ok(
            r"Im selben Chat ist nach Save kein \u00dcbergang mehr m\u00f6glich",
            "Modul 12 enforces 'no transition after save in same chat'",
            sv_text,
        )
        # Fast-Lane entfernt (refactor/remove-fast-lane, 2026-05-28):
        # Anker zeigt jetzt auf die Legacy-Notiz statt auf die aktive Ausnahme.
        all_ok &= ok(
            r"Bis v4\.2\.5 gab es eine \*\*Fast-Lane\*\*-Ausnahme",
            "Modul 12 trails the Fast-Lane removal note",
            sv_text,
        )
    else:
        print("[FAIL] Modul 12 (speicher-fortsetzung.md) not found")
        all_ok = False

    # 7) SL-Referenz: Save-Taktung listet 8 Sync-Punkte + Cross-Link auf
    #    Modul 12 §Save-Sync-Handover
    slr = root / "core" / "sl-referenz.md"
    if slr.exists():
        slr_text = read_text(slr)
        all_ok &= ok(
            r"Acht verbindliche Sync-Punkte",
            "SL-Referenz lists 'Acht verbindliche Sync-Punkte'",
            slr_text,
        )
        all_ok &= ok(
            r"#save-sync-handover",
            "SL-Referenz cross-links to #save-sync-handover anchor",
            slr_text,
        )
    else:
        print("[FAIL] SL-Referenz not found")
        all_ok = False

    # 8) Masterprompt: Save-Sync-Handover-Klausel mit Übergangstypen + Verbot
    mp = root / "meta" / "masterprompt_v6.md"
    if mp.exists():
        mp_text = read_text(mp)
        all_ok &= ok(
            r"Save-Sync-Handover an Abschnitts\u00fcberg\u00e4ngen \(verbindlich\)",
            "Masterprompt has §Save-Sync-Handover clause",
            mp_text,
        )
        # Verweis auf SSOT statt Volltext-Duplikat — schlanker Masterprompt-Block
        all_ok &= ok(
            r"SSOT.*speicher-fortsetzung\.md.*Save-Sync-Handover",
            "Masterprompt cross-refs Modul 12 SSOT",
            mp_text,
        )
        all_ok &= ok(
            r"Im selben Chat ist nach\s+`?!?save`?\s+kein \u00dcbergang mehr m\u00f6glich",
            "Masterprompt enforces 'no transition after save in same chat'",
            mp_text,
        )
        all_ok &= ok(
            r"HQ-Hub-Router ist Pflicht",
            "Masterprompt requires 'HQ-Hub-Router ist Pflicht'",
            mp_text,
        )
        all_ok &= ok(
            r"Squad-Man\u00f6ver innerhalb einer Mission sind KEIN Split",
            "Masterprompt enforces 'Squad-Manöver = kein Split'",
            mp_text,
        )
    else:
        print("[FAIL] Masterprompt not found")
        all_ok = False

    # 9) Spielerhandbuch hat Sync-Beat-Faustregel
    sh = root / "core" / "spieler-handbuch.md"
    if sh.exists():
        sh_text = read_text(sh)
        all_ok &= ok(
            r"Sync-Beat",
            "Spielerhandbuch Faustregel mentions 'Sync-Beat'",
            sh_text,
        )
        all_ok &= ok(
            r"HQ-Hub-Router",
            "Spielerhandbuch Faustregel mentions 'HQ-Hub-Router'",
            sh_text,
        )
    else:
        print("[FAIL] Spielerhandbuch not found")
        all_ok = False

    # 10) Tester-Briefing hat Acht-Sync-Punkte-Tabelle
    tb = root / "docs" / "qa" / "tester-playtest-briefing.md"
    if tb.exists():
        tb_text = read_text(tb)
        all_ok &= ok(
            r"Acht Sync-Punkte",
            "Tester-Briefing has 'Acht Sync-Punkte' table",
            tb_text,
        )
        all_ok &= ok(
            r"Sync-Station",
            "Tester-Briefing references 'Sync-Station' beat",
            tb_text,
        )
        all_ok &= ok(
            r"Rift-Koordinate aktiviert",
            "Tester-Briefing references 'Rift-Koordinate aktiviert' beat",
            tb_text,
        )
    else:
        print("[FAIL] Tester-Briefing not found")
        all_ok = False

    # 11) LINT-Anchor-Leak-Check (LINT: darf nicht in HUD oder Backticks landen)
    for i, line in enumerate(tk.splitlines(), 1):
        if "LINT:SAVE_SYNC" in line and ("`" in line or "hud_tag(" in line):
            print(f"[FAIL] SAVE_SYNC LINT anchor leaked in output (line {i})")
            all_ok = False
            break

    print("\nSummary:", "OK" if all_ok else "FAIL")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
