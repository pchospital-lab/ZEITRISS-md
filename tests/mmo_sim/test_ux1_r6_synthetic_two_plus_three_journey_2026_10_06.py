#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_r6_synthetic_two_plus_three_journey_2026_10_06.py —
W25 (ZEITRISS Terminal UX-1, R6): die echte 2+3-Reise (ZWEI MENSCHEN + DREI
FREIWILLIGE KI) ECHT ueber den tatsaechlichen `scripts/mmo_sim.py`-Subprozess
-- nicht die in-Prozess-`TuiSession`-Methodenprobe
(`test_ux1_r5_round_journey_group_sizes_2026_10_06.py`), sondern derselbe
Fachvertrag ueber einen echten, eigenstaendigen Python-Subprozess.

Luecke, die dieser Test schliesst (s. BRIEF-W25.md): der Subprozess-Harness
(`e2e_real_subprocess_dialog.py`, `manual_offline_harness.py`) doppelte
bisher NUR die GM-/SL-Transportgrenze; die PERSONA-Transportgrenze
(`MMO_SIM_PERSONA_API_BASE_URL`) blieb unverdrahtet, eine echte KI-Einladung
ueber den Subprozess war daher nicht spielbar. `_ux1_r6_persona_loopback_
support.PersonaLoopbackServer` (NEU, testseitig) schliesst das inhalts-
gebunden (kein Antwort-Queue-Fake) -- derselbe Grundsatz wie der bereits
etablierte GM-Loopback (`_ux1_r5_synthetic_creation_support.
CreationCapableSmartGmServer`).

Deckt den vollen Fachvertrag EINES zusammenhaengenden Subprozesslaufs:
1. Frische Menschenerschaffung (Leader) bis zu einem gueltigen v7-Save
   UEBER DEN ECHTEN SL-Erschaffungsdialog ('n' im Hauptmenue) -- kein
   Save-Inject.
2. Namensbasierte Einladung DREIER bekannter synthetischer KI
   (sniper/tech/medic -- Bestandsfixtures, `_fixture_note` = "SIMULIERT/
   FIXTURE", s. `internal/qa/harness/lobby/fixtures/saves/`), die ECHT
   ueber den Entscheidungsvertrag (`decision_contract`) via HTTP zusagen
   (Persona-Loopback: deterministisch "accept").
3. Eine ZWEITE Menschenperson ("Zweit", ebenfalls Bestandsfixtur-Figur,
   NICHT die hier zu belegende frische Erschaffung) tritt bei -> 2
   Menschen + 3 KI = 5 Mitglieder.
4. Reale GM-Beitraege: mehrere echte, unterscheidbare Spielzuege (Leader
   UND Zweit) erreichen den GM-Loopback nachweisbar.
5. '/pause' beendet Prozess 1 kontrolliert -- bewusst VOR dem Abschluss,
   um zu belegen, dass die /pause-Wrappertext NICHT mit der echten
   Abschlussnotiz verwechselt wird (Auftragsklarstellung).
6. Prozess 2 (ECHTER SEPARATER Subprozess, DIESELBE Datenroot, dieselbe
   `--participant`-ID): Fortsetzen OHNE neue Figur-/Community-/
   Requestidentitaet (keine erneute Registrierung, kein zweiter
   Erschaffungsdialog) -- real bis zum Abschnittsabschluss (echter
   `COMPLETION_MARKER`) UND der echten lokalen Abschlussnotiz
   (`reflections.jsonl`, `kind=human_note`) fuer BEIDE Menschen.

Ein ZWEITER, bewusst ISOLIERTER Test deckt den Ablehnungspfad (KI lehnt
ECHT ab): NICHT in dieselbe Runde gemischt, weil ein einziges "reject"
unter den zustimmungspflichtigen Gaesten die GESAMTE angefragte Runde
kontrolliert abbricht (`ui/tui.py:_cmd_local_round`, "nicht alle
angefragten Teilnehmer haben zugesagt" -- empirisch bestaetigt, s.
ADAPTER-NOTES.md) -- ein Mix haette die 2+3-Pflichtkonstellation selbst
zerstoert.

Reflexions-/Notizreihenfolge zwischen Leader und Zweit ist beim echten
Produkt NICHT deterministisch (beide IDs sind zur Laufzeit zufaellige
Registry-Hex-IDs, `core/runtime.py:_collect_reflections` iteriert
`table.members` in SORTIERTER Reihenfolge -- welche der beiden IDs
lexikografisch kleiner ist, haengt vom Zufall ab). Die Antworten auf beide
Notiz-Prompts sind deshalb bewusst SYMMETRISCH gestaltet (zwei feste,
unterscheidbare Texte) und die Zuordnung wird NACH dem Lauf ueber
`reflections.jsonl` (Schluessel = tatsaechliche `persona_key`) geprueft,
NIE ueber die Eingabereihenfolge selbst.

Pure Python, nur `assert`, echter Exitcode, synthetische Daten/Temp-Dirs,
ECHTE eigenstaendige Subprozesse (kein In-Prozess-`TuiSession`-Aufruf)."""
from __future__ import annotations

import json
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.domain.zeitriss.policy import COMPLETION_MARKER  # noqa: E402

from _ux1_r5_synthetic_creation_support import CreationCapableSmartGmServer  # noqa: E402
from _ux1_r6_persona_loopback_support import PersonaLoopbackServer  # noqa: E402
import _a24_local_support as sup  # noqa: E402

_LEADER_CREATION_ANSWER = "Standardausruestung Leader (W25-R6-Subprozessreise)."
_LEADER_MOVE_1 = "Leader-Zug-1-W25 (Anker, 2+3-Subprozessreise)."
_ZWEIT_MOVE_1 = "Zweit-Zug-1-W25 (echter Beitrag der zweiten Person)."
_LEADER_MOVE_2 = "Leader-Zug-2-W25 (zweiter echter Beitrag vor /pause)."
_LEADER_RESUME_MOVE = "Leader-Zug-3-W25 (Resume-Anker, echter separater Prozess)."
_NOTE_A = "Notiz-W25-A: Runde war in Ordnung (lokal, nicht fuer die SL)."
_NOTE_B = "Notiz-W25-B: alles plangemaess verlaufen (lokal, nicht fuer die SL)."
_AI_KEYS = ("sniper", "tech", "medic")


def _setup_common(root: Path) -> dict:
    registry_dir = root / "registry"
    onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
    states_dir, run_dir = root / "states", root / "run"
    write_test_profile(run_dir)
    return {
        "registry_dir": registry_dir, "onboarding_dir": onboarding_dir, "catalog_dir": catalog_dir,
        "states_dir": states_dir, "run_dir": run_dir,
    }


def test_two_plus_three_real_subprocess_restart_to_real_completion_note():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        d = _setup_common(root)
        registry_dir, onboarding_dir, catalog_dir = d["registry_dir"], d["onboarding_dir"], d["catalog_dir"]
        states_dir, run_dir = d["states_dir"], d["run_dir"]

        # Leader: KEINE vorab abgeschlossene Figur -- die frische
        # Erschaffung (Fachpunkt 1) laeuft ECHT im Subprozess selbst ('n').
        leader = sup.register_human(registry_dir, "LeaderW25")
        leader_id = leader.participant_id
        # Zweit: Bestandsfixtur-Figur (NICHT die hier zu belegende frische
        # Erschaffung -- die ist exklusiv dem Leader vorbehalten, s.
        # Moduldocstring Fachpunkt 1).
        zweit = sup.register_human(registry_dir, "ZweitW25")
        zweit_id = zweit.participant_id
        sup.onboard_human_figure(
            registry_dir, zweit_id, onboarding_dir, states_dir, run_dir,
            "CHR-W25-ZWEIT", "Zweit", "ZWEITOPS",
        )
        # Drei bekannte synthetische KI -- ECHTE Bestandsfixtures
        # (`internal/qa/harness/lobby/fixtures/saves/*.json`, je mit
        # `_fixture_note` == "SIMULIERT/FIXTURE" markiert), ueber denselben
        # Produktweg (`onboarding` + `core.store.publish_current_save`)
        # tischbereit gemacht wie jeder andere Bestandstest.
        for pk in _AI_KEYS:
            save = sup.make_ready(onboarding_dir, states_dir, run_dir, pk)
            assert save  # nur zur Lesbarkeit: echte Fixture wurde tatsaechlich geladen

        guest_tokens = [zweit_id] + [f"persona:{pk}" for pk in _AI_KEYS]
        table_id = sup.compute_table_id(leader_id, [zweit_id, *_AI_KEYS])
        section_id = f"{table_id}-section"

        # ---------------------------------------------------------------
        # Prozess 1: Erschaffung + Einladung (3x accept) + Zweitbeitritt +
        # mehrere echte Spielzuege + kontrolliertes '/pause' (KEIN Abschluss).
        # ---------------------------------------------------------------
        with CreationCapableSmartGmServer(table_id=table_id, section_id=section_id, complete_after=999) as gm1, \
             PersonaLoopbackServer() as persona1:
            env1 = {
                "OPENWEBUI_URL": gm1.base_url, "OPENWEBUI_API_KEY": "SYNTHETIC_W25_KEY",
                "MMO_SIM_PERSONA_API_BASE_URL": persona1.base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTHETIC_W25_KEY", "MMO_SIM_PERSONA_API_MODEL": "synthetic-w25",
            }
            stdin1 = (
                "n\n" + _LEADER_CREATION_ANSWER + "\n"
                + "l " + " ".join(guest_tokens) + "\n"
                + "j\n"
                + _LEADER_MOVE_1 + "\n"
                + _ZWEIT_MOVE_1 + "\n"
                + _LEADER_MOVE_2 + "\n"
                + "/pause\n"
            )
            p1 = sup.run_process(root, leader_id, stdin1, env1, timeout=40)
            assert p1.returncode == 0, f"Prozess 1 fehlgeschlagen: rc={p1.returncode}\n{p1.stderr}"
            out1 = p1.stdout

            # -- Fachpunkt 1: frische, ECHTE Erschaffung bis v7-Save.
            assert "Erschaffung abgeschlossen:" in out1, out1[-1500:]
            assert "Erschaffung bereits abgeschlossen" not in out1, out1[-500:]
            assert "Neu registriert:" not in out1, (
                f"Prozess 1 darf keine zusaetzliche Registrierung ausloesen (Zweit ist "
                f"Bestandsfixtur, ueber Testsetup registriert, nicht ueber 'neu:'): {out1[-500:]}"
            )

            # -- Fachpunkt 2: echte, HTTP-zugestellte accept-Entscheidung
            # ALLER drei benannten KI ueber den Persona-Loopback.
            assert "Gruppe eingeladen" in out1, out1[-1500:]
            for pk in _AI_KEYS:
                assert pk in out1.split("Gruppe eingeladen", 1)[1][:400], out1
            decisions = {c["participant_id"]: c["decision"] for c in persona1.decision_calls}
            for pk in _AI_KEYS:
                assert decisions.get(pk) == "accept", f"'{pk}': echte accept-Entscheidung ueber HTTP erwartet: {decisions}"

            # -- Fachpunkt 3: 2 Menschen + 3 KI == 5 Mitglieder, echt ueber
            # den Produktweg gebunden.
            table1 = core_store.Table.load(run_dir, table_id)
            assert table1.status == "active", table1.status
            assert set(table1.members) == {leader_id, zweit_id, "sniper", "tech", "medic"}, table1.members

            # -- Fachpunkt 4: mehrere echte, unterscheidbare Spielzuege
            # (Leader UND Zweit) sind wirklich beim GM angekommen (nicht
            # nur in eine Tischabsprache verschwunden -- der Leaderanker
            # UND Zweits ERSTER Beitrag laufen ueber den Erstimportweg
            # tatsaechlich bis zur SL durch, s. `_HumanDriver._purpose_label`).
            gm_texts = [
                (m.get("content") or "") for c in gm1.calls for m in (c.get("messages") or [])[-1:]
            ]
            for text in (_LEADER_MOVE_1, _ZWEIT_MOVE_1):
                assert any(text in t for t in gm_texts), f"Zugzeile nicht beim GM angekommen: {text!r}"
            # Mindestens ein echter Spielzug je der drei KI (automatischer
            # Beitrag ueber den Persona-Loopback, kein Autoplayer-Text von
            # T/Main erfunden).
            ai_play_texts = [t for t in gm_texts if "[PersonaLoopback] Synthetischer Spielzug" in t]
            assert len(ai_play_texts) >= len(_AI_KEYS), (
                f"erwartet mindestens {len(_AI_KEYS)} echte KI-Spielzuege beim GM, beobachtet={len(ai_play_texts)}: {gm_texts}"
            )

            # -- Fachpunkt 5: '/pause' ist NICHT der echte Abschluss --
            # die Wrappertext-Meldung erscheint, kein COMPLETION_MARKER,
            # kein "Abschnitt abgeschlossen:".
            assert "Kontrolliert pausiert (/pause)" in out1, out1[-800:]
            assert "Abschnitt abgeschlossen:" not in out1, (
                f"Prozess 1 darf NICHT bereits real abschliessen (sonst vermischt der Test "
                f"/pause mit echtem Abschluss): {out1[-800:]}"
            )
            assert COMPLETION_MARKER not in out1, out1[-800:]

        # ---------------------------------------------------------------
        # Prozess 2: ECHTER separater Subprozess, DIESELBE Datenroot,
        # DIESELBE --participant-ID -- Fortsetzen ohne neue Figur-/
        # Community-/Requestidentitaet, bis zum ECHTEN Abschluss samt
        # ECHTER lokaler Notiz fuer BEIDE Menschen.
        # ---------------------------------------------------------------
        with CreationCapableSmartGmServer(table_id=table_id, section_id=section_id, complete_after=1) as gm2, \
             PersonaLoopbackServer() as persona2:
            env2 = {
                "OPENWEBUI_URL": gm2.base_url, "OPENWEBUI_API_KEY": "SYNTHETIC_W25_KEY_P2",
                "MMO_SIM_PERSONA_API_BASE_URL": persona2.base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTHETIC_W25_KEY_P2", "MMO_SIM_PERSONA_API_MODEL": "synthetic-w25-p2",
            }
            stdin2 = (
                "l " + " ".join(guest_tokens) + "\n"
                + "j\n"
                + _LEADER_RESUME_MOVE + "\n"
                + _NOTE_A + "\n"
                + _NOTE_B + "\n"
            )
            p2 = sup.run_process(root, leader_id, stdin2, env2, timeout=40)
            assert p2.returncode == 0, f"Prozess 2 fehlgeschlagen: rc={p2.returncode}\n{p2.stderr}"
            out2 = p2.stdout

            # -- Restart-Kontinuitaet: KEINE neue Figur/Registrierung,
            # derselbe, zuvor unterbrochene Abschnitt wird fortgesetzt
            # (sichtbar an der 'unterbrochen'-Markierung im Hauptmenue,
            # VOR jeder eigenen Eingabe -- also nicht durch die obigen
            # Spielzuege selbst erzeugt).
            assert "Neu registriert:" not in out2, out2[-500:]
            assert "Erschaffungsdialog gestartet" not in out2, (
                f"Prozess 2 darf KEINEN zweiten Erschaffungsdialog ausloesen: {out2[-500:]}"
            )
            assert f"{table_id} unterbrochen" in out2, (
                f"Prozess 2 muss den zuvor pausierten Abschnitt real erkennen: {out2[-1000:]}"
            )

            # -- Fachpunkt 6a: echter Abschnittsabschluss (COMPLETION_MARKER
            # UND die menschenlesbare Bestaetigung), NICHT durch /pause.
            assert COMPLETION_MARKER in out2, out2[-1500:]
            assert "Abschnitt abgeschlossen:" in out2, out2[-1500:]
            table2 = core_store.Table.load(run_dir, table_id)
            assert table2.status == "closed", table2.status
            assert set(table2.members) == {leader_id, zweit_id, "sniper", "tech", "medic"}, (
                f"Mitgliedschaft darf sich beim Abschluss NICHT aendern (keine neue Identitaet): {table2.members}"
            )

            # -- Fachpunkt 6b: ECHTE lokale Abschlussnotiz fuer BEIDE
            # Menschen (NICHT die /pause-Wrappertext, NIE im sl_log/in
            # table_messages -- Reihenfolge Leader/Zweit ist beim echten
            # Produkt zufallsabhaengig, s. Moduldocstring, daher Pruefung
            # ueber `reflections.jsonl`s tatsaechliche persona_key-Bindung,
            # nicht ueber Eingabereihenfolge).
            # G02/UX14 (s. R5-Vorbild `test_local_reflection_note_is_fourth_
            # recipient_purpose_not_leaked`): die Beschriftung steht VOR
            # dem jeweiligen Prompt, nicht notwendig auf einer eigenen
            # Zeile (der vorherige Prompt endet ohne Zeilenumbruch) --
            # Teilstringzaehlung statt exakter Zeilenpruefung.
            note_label = (
                "Empfaenger: eigene lokale Notiz (NICHT an Spielleitung/Tisch, freiwillig, "
                "leer = keine Notiz, keine Vertraulichkeitszusage bei geteiltem Bildschirm)."
            )
            assert out2.count(note_label) == 2, (
                f"je EINE lokale-Notiz-Beschriftung fuer Leader UND Zweit erwartet: {out2[-2000:]}"
            )
            reflections = sup.read_jsonl(run_dir / "reflections.jsonl")
            human_notes = {
                r["persona_key"]: r.get("text") for r in reflections
                if r.get("kind") == "human_note" and r.get("section_id") == section_id
            }
            assert set(human_notes) == {leader_id, zweit_id}, (
                f"beide Menschen muessen je eine echte lokale Notiz abgegeben haben: {human_notes}"
            )
            assert set(human_notes.values()) == {_NOTE_A, _NOTE_B}, (
                f"die abgegebenen Notiztexte muessen genau den beiden echten Antworten entsprechen "
                f"(nicht der /pause-Wrappertext, nicht leer): {human_notes}"
            )
            for text in human_notes.values():
                assert "Kontrolliert pausiert" not in text, human_notes

            # Die drei KI haben ihre VORGESEHENE Pflichtreflexion ebenfalls
            # ECHT ueber den Persona-Loopback abgegeben (sonst waere der
            # Abschnitt oben gar nicht `closed`, s. `core/runtime.py:
            # _collect_reflections`-Vertrag "Rueckgabewert True nur, wenn
            # ALLE KI-Pflichtreflexionen erfolgreich waren").
            ai_reflections = {
                r["persona_key"] for r in reflections
                if r.get("kind") == "ai_required_reflection" and r.get("section_id") == section_id
            }
            assert ai_reflections == set(_AI_KEYS), ai_reflections

            table_data = json.loads((run_dir / "tables" / f"{table_id}.json").read_text(encoding="utf-8"))
            sl_text = " ".join(e.get("content", "") for e in table_data.get("sl_log", []))
            for text in human_notes.values():
                assert text not in sl_text, "lokale Notiz darf NIE an die SL gehen"


def test_named_ai_invite_real_rejection_does_not_form_table():
    """Isolierter Ablehnungspfad (s. Moduldocstring 'warum getrennt'):
    eine ECHT ueber HTTP zugestellte reject-Entscheidung einer benannten
    KI blockiert die GESAMTE angefragte Runde -- kein Tisch, kein stiller
    Restgruppen-/Soloweiterlauf."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        d = _setup_common(root)
        registry_dir, onboarding_dir, catalog_dir = d["registry_dir"], d["onboarding_dir"], d["catalog_dir"]
        states_dir, run_dir = d["states_dir"], d["run_dir"]

        leader = sup.register_human(registry_dir, "LeaderReject")
        leader_id = leader.participant_id
        sup.onboard_human_figure(
            registry_dir, leader_id, onboarding_dir, states_dir, run_dir,
            "CHR-W25-REJLEAD", "RejLead", "REJLEADOPS",
        )
        sup.make_ready(onboarding_dir, states_dir, run_dir, "cqb")
        table_id = sup.compute_table_id(leader_id, ["cqb"])
        section_id = f"{table_id}-section"

        with CreationCapableSmartGmServer(table_id=table_id, section_id=section_id, complete_after=999) as gm, \
             PersonaLoopbackServer({"cqb": "reject"}) as persona:
            env = {
                "OPENWEBUI_URL": gm.base_url, "OPENWEBUI_API_KEY": "SYNTHETIC_W25_REJ_KEY",
                "MMO_SIM_PERSONA_API_BASE_URL": persona.base_url,
                "MMO_SIM_PERSONA_API_KEY": "SYNTHETIC_W25_REJ_KEY", "MMO_SIM_PERSONA_API_MODEL": "synthetic-w25-rej",
            }
            p = sup.run_process(root, leader_id, "l persona:cqb\n", env, timeout=30)
            assert p.returncode == 0, f"Prozess fehlgeschlagen: rc={p.returncode}\n{p.stderr}"
            out = p.stdout
            assert "Einladung an 'cqb' nicht angenommen (Entscheidung: reject)." in out, out[-800:]
            assert "nicht alle angefragten Teilnehmer haben zugesagt" in out, out[-800:]
            assert persona.decision_calls == [
                {"offer_id": sup.invitation_offer_id(leader_id, ["cqb"]), "participant_id": "cqb", "decision": "reject"}
            ], persona.decision_calls
            table_file = run_dir / "tables" / f"{table_id}.json"
            assert not table_file.exists(), "eine echt abgelehnte Einladung darf keinen Tisch anlegen"


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
