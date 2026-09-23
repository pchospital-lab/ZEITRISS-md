# ZEITRISS MMO-Sim — Bedien-/Betriebsdoku (P2, Bauabnahme)

> Status dieses Dokuments: P2-Bauabnahme, NICHT liveabgenommen. Siehe
> `WORKER-REPORT.md` im Ergebnispaket für die vollständige Funktionsmatrix
> (IMPLEMENTIERT/OFFLINE_GEPRÜFT/LIVE_GEPRÜFT/OFFEN).

## Architektur

```
mmo_sim/
  core/       neutraler Kern (Store, Persona-State-Engine, Controller, Runtime,
              Scheduler, Identity, Events, Completion-Marker) — kennt KEINE
              ZEITRISS-Regel (kein "v7", kein "5").
  adapters/   echte Produktionspfade: persona_api (LiteLLM/OpenRouter),
              persona_claude_code (lokale CLI, isoliert), gm_owui (nutzt
              agent_mp/sl_client), fakes (Prozess-/HTTP-Grenze für Tests).
  domain/zeitriss/  ZEITRISS-Domänenregeln als injizierte Policy-Objekte
              (policy.py), Save-Extraktion (saves.py, aus agent_mp/ verschoben),
              Onboarding, Import/Export, Katalog, Community-Bootstrap, Prelude.
  registry/   neutraler Teilnehmer-/Anwendungsdatensatz-Hook (11 §9).
  ui/tui.py   Terminaloberfläche (kein Browser fürs Spielen).
  lab/runner.py  headless Lab-Betrieb (Singleton, Budget, Stop/Status).
  reports/report.py  lokale Event-Reports + Issue-Entwürfe (kein Modellcall).
```

Die QA-Fassaden (`internal/qa/harness/lobby/rooms.py`, `agent_mp/saves.py`,
`persona_state.py`) sind Re-Export-Shims auf die extrahierte Implementierung
— sie enthalten selbst keine Logik mehr, nur Alt→Neu-Kompatibilitätsschicht
(Konstruktorsignaturen, Default-Datum für die eingefrorene P1-Testsuite).

## Starten (Terminal, kein Browser)

```bash
python3 scripts/mmo_sim.py --participant <teilnehmer-id> --data-dir internal/mmo_sim_data
```

Oder über den generischen Launcher: `python3 scripts/launcher.py` → Menüpunkt
`[M] ZEITRISS MMO-Sim`.

## Tests

```bash
# Neue mmo_sim-Regressionen (Gesamtrunner):
python3 tests/mmo_sim/run_all.py

# Eingefrorene P1-Regression (muss weiterhin grün sein):
python3 internal/qa/harness/lobby/test_lobby_tables.py

# Offizieller P1-Regressionsrunner (aus dem Auftragspaket, --repo-root auf
# diesen Worktree, --output-dir AUSSERHALB des Repos):
python3 <auftragspaket>/reference/p1-regressions/run_checks.py \
  --repo-root <dieser-worktree> --output-dir <externes-verzeichnis>
```

## Provider-Profile (03_PROVIDER_UND_BETRIEB.md)

| Profil | Spieler-Personas | KI-SL |
|---|---|---|
| Hybrid | `persona_claude_code` (lokale CLI, isoliert) | `gm_owui` |
| API | `persona_api` (LiteLLM/OpenRouter) | `gm_owui` |
| Offline-Prüfung | `adapters/fakes.FakeCLIProcess`/`FakeHTTPServer` | dito |

Kein stiller Fallback: 401/403 → `ProviderAuthError`, 429/Quota →
`ProviderQuotaError`, CLI/Isolation fehlt → `ProviderUnavailableError`. Alle
drei Fehlerklassen führen zu Pause/Fehlerstatus, nie zu einem automatischen
Providerwechsel.

**Betriebswarnung `persona_claude_code` ohne `extra_isolation_flags`
(End-Critic W1):** Ohne konfigurierte `extra_isolation_flags` prüft
`check_isolation()` NUR Binary-Erreichbarkeit + Arbeitsbereich; die von
03 §5 geforderte Tool-/MCP-/Hook-/Settings-Isolation bleibt unverifiziert.
Einzige verbleibende Schutzschicht ist dann der Billing-Var-Check (03 §4,
prüft nur 3 benannte Variablen). `decide()` gibt in diesem Fall genau eine
Log-Warnung pro `check_isolation()`-Aufruf aus (`persona_claude_code.py`,
`_LOG.warning`). **Für echten Spielbetrieb (nicht nur den in
`review_p2_integration.py` geprüften Kontext-/JSON-Vertrag) sind reale,
verifizierte `extra_isolation_flags` Pflicht** — der Default-Fall ohne
Flags ist nur für die Offline-/Vertragsprüfung freigegeben.

**Admission-Gate: „vor jedem Request", nicht atomar damit (End-Critic
W2):** `read_admission_block()` liest `lab.stop`/`lab.status.json` frisch
von der Platte vor jedem GM-Request, es gibt aber keinen Lock zwischen
diesem Read und dem darauffolgenden vollen Turn. Ein exakt in diesem
Fenster gesetzter Stop lässt den bereits begonnenen Turn noch zu Ende
laufen (max. 1 Turn „Overshoot"), bevor der Gate beim nächsten Request
sicher greift. Für den aktuellen Offline-/Einzelbenutzer-Betrieb
vertretbar, aber nicht als vollständig race-frei/atomar missverstehen.

## P2-Restintegration (2026-09-23, siehe WORKER-REPORT-REST.md für Details)

- `l lead:persona:<id> [<weitere-token>]` macht eine eingeladene Persona
  zum Leader statt des aufrufenden Menschen (A24, echte Zusage vor
  Tischaufnahme; der aufrufende Mensch wird selbst zum Gast).
- Nach Import eines Saves mit `level >= 2` bietet das Terminal die
  Direktspielen-/KI-Vorlauf-Wahl (11 §7, A23) — der Vorlauf konfiguriert
  einen echten `LabRunner`/Budget, bleibt aber ohne separates Live-Go
  Konfiguration/Mockausführung (01 §M4).
- `[n]`/`[i]` registrieren die betroffene Figur jetzt im Teilnehmer-Katalog
  (`domain/zeitriss/catalog.py`) — Resume-Karte/Mehrfiguren-Übersicht
  zeigen echte Einträge (A21, Teilausbau: der zugrunde liegende Save-Store
  bleibt weiterhin EIN aktueller Stand pro Teilnehmer, siehe Restrisiken
  im WORKER-REPORT-REST.md).
- `reports/report.py:extract_provenance_excerpts` liefert unveränderte
  Textausschnitte zu Ausrüstung/Boss/Kampf/Drift-Erwähnungen aus echten
  `sl_turn`-Events (A13, reine Stichwortsuche, keine Modellbewertung).

## Bekannte Lücken (siehe WORKER-REPORT.md für Details)

- Kein echter Modellaufruf in diesem Bauauftrag (Auftragsgrenze) — alle
  Adapter sind an der Prozess-/HTTP-Grenze offline geprüft, nicht live.
- `scripts/launcher.py` weicht ab diesem Block bewusst von der
  repoübergreifenden Bytegleichheit ab (A4, siehe unten).
- Vollständige A01–A28-Testabdeckung mit allen Negativ-/Resume-Pfaden ist
  NICHT vollständig — reduzierter, aber real ausgeführter Kernsatz (siehe
  WORKER-REPORT.md Funktionsmatrix).
- Lokale Mehrmenschen-Runde (11 §8) ist auf Katalog-/Leader-Ebene geprüft,
  die volle TUI-Fokuswechsel-Bedienung ist nicht vollständig ausgebaut.

## A4 — `scripts/launcher.py`-Drift (bewusst, dokumentiert)

`scripts/launcher.py` ist repoübergreifend als byte-identisch gedacht
(`launcher-sync.sh`-Gate über 5 Bausätze). Dieser Block fügt einen optionalen
Projekt-Hook-Import (`mmo_sim_launcher_hook`, analog zum bestehenden
`rite_module`-Muster) und einen Menüpunkt `[M]` hinzu. Das erzeugt bewusst und
erwartungsgemäß Drift gegenüber den anderen 4 Bausätzen (ARXION, Privacy
Odyssey, Unfallhelfer, agent0) — KEIN Fehlalarm des Drift-Checks, KEINE
automatische Angleichung der anderen Repos in diesem Block (Auftragsgrenze).
