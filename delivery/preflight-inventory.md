# Preflight-Inventar — Populationsbackup/-Restore (ZR-POPULATION-BACKUP-RESTORE)

Dieses Inventar beschreibt die **tatsaechlich wirksamen** Resolver, Datenrollen,
Pfade und Ein-/Ausschlussentscheidungen des populationsweiten Backups
(`mmo_sim/core/population_backup.py`). Es ist bewusst **nichtgeheim**: es nennt
nur Rollen, relative Layouts und Policy, keine realen Credentials oder privaten
Spielinhalte. Nachzug F6 (CODE-REVIEW C6): das bisher nur in Codekommentaren
referenzierte Inventar wird hiermit als echte Quelle mitgeliefert.

## Wirksame Resolver (Quelle: Produktcode, Commit-Basis `b8908318`)

Der Backup-Hook bekommt die sechs Rollen **immer explizit** als
`PopulationRoots` (kein angenommener gemeinsamer Elternordner). Es gibt zwei
tatsaechliche Produktionscaller:

### 1. TUI (`ui/tui.py:TuiSession`)
`TuiSession._population_backup_roots()`:

| Rolle | Resolver | Default-Pfad (CLI `--data-dir`, `scripts/mmo_sim.py:109`) |
| --- | --- | --- |
| onboarding | `self.onboarding_dir` | `<data_dir>/onboarding` |
| catalog | `self.catalog_dir` | `<data_dir>/catalog` |
| run | `self.run_dir` | `<data_dir>/run` |
| states | `self.states_dir` | `<data_dir>/states` |
| registry | `self._local_round_registry_dir()` = `onboarding_dir.parent/registry` | `<data_dir>/registry` |
| prefs | `self.onboarding_dir.parent` (nur Glob, s.u.) | `<data_dir>` |

Backup-Ziel: `_population_backup_root_dir()` = `<data_dir>/population_backups`
(Geschwister des Datenroots, **nie** innerhalb einer Rolle — `_assert_no_overlap`).
CLI-Default `--data-dir` = `<repo>/internal/mmo_sim_data` (`scripts/mmo_sim.py:109`).

### 2. Lobby/Lab (`core/lobby_flow.py:play_bound_table`)
Dieselben sechs Rollen aus der laufenden `session` (`lobby_flow.py:248-257`):
`registry_dir = session.onboarding_dir.parent/registry`,
`prefs_root = session.onboarding_dir.parent`,
Backup-Ziel `session.onboarding_dir.parent/population_backups`.

## Getrennt konfigurierter Fall (nicht-gemeinsamer Elternordner)

`PopulationRoots` ist bewusst sechsfach-explizit (`@dataclass(frozen=True)`),
damit ein Betrieb die Rollen auch auf **verschiedene** Elternordner/Volumes
legen kann, z. B. `states` auf schnellem lokalem Speicher, `catalog`/`registry`
auf einem gemeinsamen Netzlaufwerk. Dieselben Produktresolver
(`collect_population_files`, `generate_population_backup`, `restore_population`)
arbeiten unveraendert, weil sie ausschliesslich ueber `roots.as_dict()` iterieren
und nie `parent` raten. `_assert_no_overlap` prueft jede Rolle einzeln gegen das
`backup_root`. Der Restore legt alle sechs Rollen wieder relativ zu **einem**
neuen `target_root` an (`ROLE_TARGET_SUBDIR`), damit das Ergebnis direkt als
neues `--data-dir` nutzbar ist — das Backup bewahrt die Rollen-Trennung, der
Restore vereinheitlicht sie bewusst in einem privaten Root.

Der Regressionstest `test_f6_separate_root_config_*` deckt genau diesen Fall
mit sechs getrennt konfigurierten Wurzeln ab.

## Scan-Policy je Rolle

- `onboarding`, `catalog`, `run`, `states`, `registry`: **rekursiv** (`os.walk`).
- `prefs`: **nicht** rekursiv, nur Glob `ui_prefs*.json` + `last_participant.json`
  direkt in `prefs_root` (das im Default-Layout mit dem gemeinsamen Elternordner
  der anderen fuenf identisch ist — ein rekursiver Walk wuerde sie doppelt
  einsammeln).

## Ein-/Ausschlussentscheidungen

**Eingeschlossen** (whole_population): alle regulaeren Dateien der sechs Rollen
nach der obigen Scan-Policy. Jede Datei wird genau einmal gelesen/gehasht;
Manifest und Kopie nutzen denselben Scan.

**Ausgeschlossen, auditierbar im Manifest unter `excluded`:**

| Klasse | Muster (`population_backup.py`) | Begruendung |
| --- | --- | --- |
| OS-/Transient | `lab.lock.json`, `*.tmp`, `*.tmp-*`, `__pycache__`, `.DS_Store` (`_EXCLUDED_NAME_PATTERNS`) | PID-OS-Lock/transiente Writes, keine fachliche Bindung |
| Auth/Secret/Env (F6) | `_AUTH_EXCLUDED_PATTERNS`: `.env*`, `auth*.json`, `*_auth.json`, `api_key*`/`apikey*`/`*api-key*`, `*credentials*` (inkl. blanke `credentials`, `aws_credentials`), `token*`/`*_token.json`/`*.token`, `secret*`/`*.secret`, `*.pem`/`*.key`/`*.keyfile`/`*.p12`/`*.pfx`/`*.keystore`, `id_rsa*`/`id_ed25519`, `session_auth*`, `provider_auth*`/`*provider_token*`/`*access_token*`/`*refresh_token*`, `oauth*.json`, `service*account*.json`, `kubeconfig*`, `.netrc`/`.npmrc`/`.pgpass`/`.pypirc`/`.htpasswd` | Provider-/Shell-/Cloud-Credentials gehoeren **nie** in eine Population; nur dateinamenbasiert, Inhalt wird nie gelesen. (Generische `config.json` wird bewusst NICHT pauschal ausgeschlossen, um legitime Nicht-Secret-Konfiguration nicht zu verlieren.) |
| Symlink/Spezialdatei | `_is_safe_regular_file` via `os.lstat` | Link-/Pfadausbruch, FIFO/Device/Socket |

**Policy:** Der Auth-Ausschluss ist eine **wirksame Grenze** (die Datei wird
nicht gehasht/kopiert/restauriert), nicht bloss eine Manifestnotiz „liegt
ausserhalb". Notwendige nichtgeheime Konfiguration bleibt enthalten. Keine
rekursiven Sicherungen der Sicherungen (`population_backups/` liegt ausserhalb
der sechs Rollen; `_assert_no_overlap` lehnt Fehlkonfiguration hart ab).

## Ueberschneidungen

- `prefs_root` == gemeinsamer Elternordner der fuenf rekursiven Rollen im
  Default-Layout → aufgeloest durch die Glob-statt-Walk-Policy fuer `prefs`.
- Backup-Ziel unterhalb `prefs_root` (z. B. `<data_dir>/population_backups`) ist
  **kein** Rekursionsrisiko (prefs scannt nicht rekursiv); nur Gleichheit/Umschluss
  wird abgelehnt.

## Datengrenze (Auftrags-Sicherheitsauflage)

Credentials werden ausschliesslich ueber die normale getrennte native
Konfiguration bereitgestellt und **niemals aus einem Backup importiert**. Der
Restore gewinnt keine Ausfuehrungsautoritaet aus OS-PIDs (`lab.lock.json`
ausgeschlossen). Reale Secrets sind weder Testmaterial noch Beleg; Tests
verwenden ausschliesslich einen klar erkennbaren Fake-Sentinel.
