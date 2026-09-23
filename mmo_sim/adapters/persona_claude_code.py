#!/usr/bin/env python3
"""
mmo_sim/adapters/persona_claude_code.py — `claude_code_local`-Persona-Adapter
(echter Produktionspfad, 03_PROVIDER_UND_BETRIEB.md §5).

P2-Fertigstellung (I2, REVIEW-P2.md §I2):
- `system`-Kontext wird jetzt TRANSPORTIERT (identischer semantischer
  Vertrag wie der API-Adapter) — nicht mehr verworfen.
- Die `--output-format json`-Huelle (`result`/`usage`/`is_error`) wird
  DEKODIERT statt als roher stdout auf `ParticipantDecision.text` zu landen;
  `is_error` fuehrt zu `ProviderUnavailableError` statt stillem Durchreichen.
- Isolation gilt erst als BELEGT, wenn mindestens ein vom Aufrufer explizit
  konfiguriertes, real existierendes Isolationsflag (`extra_isolation_flags`)
  tatsaechlich in der `--help`-Ausgabe der installierten CLI auftaucht — ein
  bloss erfolgreicher `--version`/`--help`-Aufruf allein reicht NICHT mehr
  (schliesst den "beliebiges --help + leerer Ordner" Review-Befund I2/Test 04).
- Billing-Var-Check: bevor ein Request rausgeht, wird die GEERBTE Umgebung
  auf Variablen geprueft, die versehentlich API-Abrechnung statt Abo
  auswaehlen koennten (03 §4) — Fund fuehrt zu `ProviderUnavailableError`,
  kein stiller Versand.

CLI-Isolation (bindend, 03 §5): vor jeder Nutzung wird `--version`/`--help`
der TATSAECHLICH installierten CLI OHNE Inferenz gelesen (`check_isolation`).
Ohne herstellbare Isolation liefert der Adapter `unavailable`
(`ProviderUnavailableError`) statt unsicherem Betrieb. Keine
`--continue`-Sammelhistorie ueber Personas: jeder Turn ist ein isolierter
Einzelaufruf mit eigener, freigegebener Sicht (kein geteilter Session-State
zwischen Personas). Anfragen ueber Argumentliste/STDIN, kein aus
Spielertext gebauter Shellbefehl (kein `shell=True`).

`process_runner` ist injizierbar (Default: echter `subprocess`) — Tests
ersetzen ihn durch `adapters.fakes.FakeCLIProcess` (Fake-CLI ersetzt die
echte Binary, s. 04 §3)."""
from __future__ import annotations

import json
import logging
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from .base import ParticipantDecision, ProviderUnavailableError, render_public_wire_text

_LOG = logging.getLogger(__name__)

# I2/A3: Umgebungsvariablen, die versehentlich API-Abrechnung statt Abo
# auswaehlen koennten (03 §4: "vor einer Anfrage melden"). Reine Namensliste
# -- kein Zugriff auf/Ausgabe von Werten, nur Praesenz-Check.
BILLING_RISK_ENV_VARS = ("ANTHROPIC_API_KEY", "OPENROUTER_API_KEY", "CLAUDE_API_KEY")

# D4/A5 (WEGKARTE §6, PLAN-CRITIC-ABSCHLUSS.md WICHTIG): Flags, die der
# Adapter OHNEHIN bei JEDEM Aufruf fest sendet (`decide()`s Baseline-Argv) --
# ein konfiguriertes `extra_isolation_flags`, das AUSSCHLIESSLICH aus diesen
# Plumbing-Flags besteht, ist PER DEFINITION kein Isolationsbeleg (ein
# beliebiger Hilfetext, der das Ausgabeformat dokumentiert, erwaehnt sie
# zwangslaeufig).
_BASELINE_PLUMBING_FLAGS = frozenset({"-p", "--output-format", "json"})

# A5/D4 (WEGKARTE §8, Plan-Critic A5 Befund 1, Test 11): KEIN Vokabular-
# Fenster-Scan mehr ueber beliebigen Hilfetext-Prosa (ein rein diagnostischer
# Hilfetext wie "Lists tools and MCP settings... changes no permissions or
# hooks" erwaehnt exakt dieses Vokabular, OHNE irgendetwas einzuschraenken --
# Test 11 reproduziert das). Stattdessen ein KONKRETER, geschlossener
# Katalog tatsaechlich dokumentierter Claude-Code-CLI-Isolationsschalter
# (03 §5: "Schalter zur Begrenzung von Tools und Einstellungen"). Ein
# konfiguriertes Flag gilt NUR dann als belegt, wenn sein Flag-NAME (vor
# einem etwaigen '=') exakt einem dieser bekannten Isolationsschalter
# entspricht UND real in der `--help`-Ausgabe der installierten CLI auftaucht
# -- Praesenz beliebiger Nachbarwoerter ist irrelevant. `--synthetic-safe`
# (bzw. jedes als "synthetic" gekennzeichnete Flag) bleibt die etablierte,
# ausdruecklich vereinbarte Testkennung fuer Offline-Suiten, kein echter
# CLI-Anspruch.
#
# W5-Ergaenzung (F5, PLAN-CRITIC.md Auflage 5, Test 08 review_p2w_
# boundaries.py): Katalog UND Namen empirisch aus der tatsaechlich lokal
# installierten CLI (`claude --help`, Claude Code 2.1.231, Vollmitschrift
# in worker-out/w5-real-cli-help.txt) uebernommen -- keine erfundenen Flags.
# Ergaenzt gegenueber der Vorfassung: `--allowed-tools`/`--disallowed-tools`
# (Bindestrich-Alias derselben Schalter, laut --help gleichwertig zu
# `--allowedTools`/`--disallowedTools`), `--tools` (explizite Tool-Liste,
# "" deaktiviert alle Tools), `--setting-sources` (Settings-Quellen
# begrenzen) und `--safe-mode` (schaltet laut --help-Text CLAUDE.md/Skills/
# Plugins/Custom-Commands/Agents/Output-Styles/Workflows/Themes/Keybindings
# UND HOOKS UND MCP-Server komplett ab -- der einzige real dokumentierte
# Schalter, der Hooks ueberhaupt beruehrt; "built-in tools ... work
# normally" laut Hilfetext -- `--safe-mode` allein schraenkt also KEINE
# Tools ein, s. `_TOOL_RESTRICTING_FLAG_NAMES`/`_BROAD_ISOLATION_FLAG_NAMES`
# unten fuer die Kombinationspflicht gegen die echte Binary)."""
_KNOWN_ISOLATION_FLAG_NAMES = frozenset({
    "--allowedtools", "--allowed-tools", "--disallowedtools", "--disallowed-tools",
    "--permission-mode", "--tools", "--strict-mcp-config", "--mcp-config",
    "--setting-sources", "--safe-mode",
})

# W5 (F5): welche der bekannten Schalter schraenken TOOLS ein (Bash/Edit/
# Read/...)? Empirisch aus --help: `--tools`/`--allowedTools`/
# `--disallowedTools` (bzw. Bindestrich-Alias) benennen/filtern das
# Toolset direkt; `--permission-mode` steuert, ob ein Tool-Aufruf ohne
# interaktive Bestaetigung ueberhaupt ausgefuehrt wird -- beides zaehlt als
# Tool-Restriktion.
_TOOL_RESTRICTING_FLAG_NAMES = frozenset({
    "--allowedtools", "--allowed-tools", "--disallowedtools", "--disallowed-tools",
    "--tools", "--permission-mode",
})

# W5 (F5): welcher bekannte Schalter deckt Hooks/MCP/Settings/Plugins in
# der Breite ab? Nur `--safe-mode` laut --help-Text ausdruecklich ("skip
# hooks ... MCP servers ... settings"). `--strict-mcp-config` begrenzt
# NUR MCP-Quellen (Kommentar in `_is_known_isolation_flag`), deckt weder
# Hooks noch Settings noch Plugins ab -- daher NICHT in dieser Menge (s.
# Test 08: ein einzelnes `--strict-mcp-config` gegen die echte Binary ist
# KEINE umfassende Isolation).
_BROAD_ISOLATION_FLAG_NAMES = frozenset({"--safe-mode"})

# W5-B3-Fix (Main-Nacharbeit, End-Critic BLOCKER 3): Wertepruefung fuer die
# Kombinationspflicht. Werte empirisch aus der echten `claude --help`
# (Claude Code 2.1.231, worker-out/w5-real-cli-help.txt): --permission-mode
# choices acceptEdits|auto|bypassPermissions|manual|dontAsk|plan -- restriktiv
# (kein automatisches Tool-Ausfuehren) sind nur 'plan'/'manual'. --tools: ''
# deaktiviert alle Tools (restriktiv), 'default' = alle Tools (NICHT), sonst
# explizite Teilmenge (restriktiv). --allowed-tools/--disallowed-tools brauchen
# eine nicht-leere Liste.
_RESTRICTIVE_PERMISSION_MODES = frozenset({"plan", "manual"})
_OPEN_PERMISSION_MODES = frozenset({"acceptedits", "auto", "bypasspermissions", "dontask"})
_TOOLS_NON_RESTRICTIVE_VALUES = frozenset({"default"})
_TRUTHY_FLAG_VALUES = frozenset({"true", "1", "yes", "on"})

# I3-Fix (MAIN-ENTSCHEIDUNG I3-Regel, PLAN-CRITIC F10, Case 06): geschlossene
# Menge erkannter Negationswerte fuer `--safe-mode` -- ein Flag-NAME allein
# (ohne Wertpruefung) ist KEIN Beleg, `--safe-mode=false`/`=0`/`=no`/`=off`
# schaltet die Isolation ausdruecklich WIEDER AUS und darf nicht als
# "broad restriction vorhanden" zaehlen.
_FALSY_FLAG_VALUES = frozenset({"false", "0", "no", "off"})


def _broad_flag_value_is_effective(name: str, has_value: bool, value: str) -> bool:
    """I3-Fix: `--safe-mode` (bare ODER mit wirksamem/nicht-negierendem
    Wert) zaehlt als wirksame Breitenisolation; `--safe-mode=false`/`=0`/
    `=no`/`=off` (explizite Negation) NICHT -- reine Namenspraesenz reicht
    nicht mehr."""
    if name not in _BROAD_ISOLATION_FLAG_NAMES:
        return False
    if not has_value:
        return True
    return value.strip().lower() not in _FALSY_FLAG_VALUES


def _parse_isolation_flag(flag: str) -> tuple[str, bool, str]:
    """Zerlegt ein Isolationsflag in (name, has_value, value). '--flag=wert'
    -> (name, True, wert); ein blosses '--flag' ohne '=' -> (name, False, '')."""
    if "=" in flag:
        name, value = flag.split("=", 1)
        return name.strip().lower(), True, value
    return flag.strip().lower(), False, ""


# I3-Fix (PLAN-CRITIC.md Auflage F..., "kleine kanonische erlaubte
# Gesamtkonfiguration statt OR ueber Teilbedingungen", Case 08): jedes
# bekannte Flag MIT Wert wird auf genau eine von drei Klassen abgebildet --
# 'restrictive' (schraenkt tatsaechlich ein), 'open' (expliziter Bypass/
# Weitstellung, z.B. '--permission-mode=bypassPermissions' oder
# '--tools=default') oder 'unknown' (nicht erkannter Wert, z.B.
# '--safe-mode=garbage'). Ein 'open'/'unknown' AN IRGENDEINER Stelle der
# kanonischen Konfiguration fuehrt IMMER zur Ablehnung der GESAMTEN
# Kombination -- ein restriktiver Token an anderer Stelle darf das NICHT
# neutralisieren (bindende Auflage, s. check_isolation). Das ersetzt das
# alte `any(tool_effective_by_name.values())`, das genau diese Neutralisierung
# zuliess (`--tools=` restriktiv maskierte ein gleichzeitiges
# `--permission-mode=bypassPermissions`)."""
def _classify_tool_flag_value(name: str, value: str) -> str:
    v = value.strip()
    if name == "--permission-mode":
        lv = v.lower()
        if lv in _RESTRICTIVE_PERMISSION_MODES:
            return "restrictive"
        if lv in _OPEN_PERMISSION_MODES:
            return "open"
        return "unknown"
    if name == "--tools":
        # '' deaktiviert alle Tools (restriktiv), 'default' = alle Tools
        # (offen), sonst explizite Teilmenge (restriktiv, s. Docstring oben).
        return "open" if v.lower() in _TOOLS_NON_RESTRICTIVE_VALUES else "restrictive"
    if name in {"--allowed-tools", "--allowedtools", "--disallowed-tools", "--disallowedtools"}:
        return "restrictive" if v else "neutral"
    return "neutral"


def _classify_broad_flag_value(has_value: bool, value: str) -> str:
    if not has_value:
        return "restrictive"
    lv = value.strip().lower()
    if lv in _FALSY_FLAG_VALUES:
        return "open"  # explizite Negation, z.B. --safe-mode=false.
    if lv in _TRUTHY_FLAG_VALUES:
        return "restrictive"
    return "unknown"  # unbekannter Wert -- NICHT als aktiv/wirksam werten.


def _tool_flag_value_is_effective(name: str, has_value: bool, value: str) -> bool:
    """W5-B3: True nur, wenn ein Tool-restriktives Flag mit seinem WERT
    tatsaechlich einschraenkt (nicht bloss namentlich vorhanden ist)."""
    if not has_value:
        return False  # blanker wertnehmender Schalter -- verschluckt naechstes argv-Token
    v = value.strip()
    if name == "--permission-mode":
        return v.lower() in _RESTRICTIVE_PERMISSION_MODES
    if name == "--tools":
        return v.lower() not in _TOOLS_NON_RESTRICTIVE_VALUES
    if name in {"--allowed-tools", "--allowedtools", "--disallowed-tools", "--disallowedtools"}:
        return bool(v)
    return False


def _is_known_isolation_flag(flag: str, allow_synthetic_convention: bool) -> bool:
    """R09-Fix (WEGKARTE §8, A5/D4): das Wort 'synthetic' im Flag-Namen ist
    KEIN Sicherheitsschalter fuer die echte Binary -- die Testkonvention gilt
    NUR, wenn tatsaechlich ein injizierter Testdouble (nicht `_RealProcessRunner`)
    als `process_runner` verwendet wird (`allow_synthetic_convention`, vom
    Aufrufer anhand des tatsaechlichen Runner-Typs bestimmt, s.
    `check_isolation`). Gegen die reale `_RealProcessRunner`-Binary zaehlt
    ausschliesslich der geschlossene Katalog echter Isolationsschalter."""
    if allow_synthetic_convention and "synthetic" in flag.lower():
        return True
    name = flag.split("=", 1)[0].strip().lower()
    return name in _KNOWN_ISOLATION_FLAG_NAMES


# A5/D4 (Befund 2): Kind-Prozess bekommt NUR eine minimale, kuratierte
# Umgebung -- keine volle `os.environ`-Vererbung mehr (die zuvor jeden
# geerbten Rollen-Key, z.B. `OPENWEBUI_API_KEY`, in den Kindprozess
# durchreichte, Test 11 `child_has_sl_role_key`).
_CHILD_ENV_ALLOWLIST = ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR", "TERM", "SHELL")


class _RealProcessRunner:
    def run(
        self, argv: list[str], stdin: str = "", env: dict | None = None, cwd: str | None = None,
    ) -> tuple[int, str, str]:
        proc = subprocess.run(
            argv, input=stdin, capture_output=True, text=True, env=env, cwd=cwd, timeout=120,
        )
        return proc.returncode, proc.stdout, proc.stderr


@dataclass
class ClaudeCodeConfig:
    binary: str = "claude"
    isolated_workdir: str | None = None  # eigener Arbeitsbereich ohne Altair-Dateien
    extra_isolation_flags: list[str] = field(default_factory=list)  # z.B. echte, real existierende Flags


class PersonaClaudeCodeDriver:
    """`ParticipantDriver`-Implementierung fuer die lokale Claude-Code-CLI im
    Hybrid-Profil. Persistiert KEINE `--continue`-Historie ueber Personas
    hinweg — jeder `.decide()`-Aufruf ist ein eigener, isolierter Prozessstart."""

    def __init__(self, config: ClaudeCodeConfig, persona_key: str, process_runner=None):
        self.config = config
        self.persona_key = persona_key
        self._runner = process_runner or _RealProcessRunner()
        self._isolation_checked = False

    def check_isolation(self) -> dict:
        """Liest `--version` UND `--help` der REAL installierten CLI OHNE
        Inferenz (03 §5, Pflicht vor Implementierung/Nutzung). Wirft
        `ProviderUnavailableError`, wenn die Binary fehlt ODER der
        konfigurierte Arbeitsbereich nicht existiert.

        Isolationsflags: konfiguriert der Aufrufer `extra_isolation_flags`,
        wird JEDES Flag GEGEN die tatsaechliche `--help`-Ausgabe verifiziert
        (fehlt eines -> `unavailable`, kein stilles Ignorieren einer
        Fehlkonfiguration). Bleibt `extra_isolation_flags` leer (Default,
        wie im gesamten review_p2_integration.py-Vertrag 02-04, der keine
        Flags konfiguriert), gilt Isolation als NICHT VERIFIZIERT
        (`isolation_flags_configured=False` im Rueckgabewert) — das ist
        bewusst kein harter Abbruch mehr (fruehere Fassung dieser
        Fertigstellung brach hier hart ab, brach damit aber Test 02/03, die
        exakt diese leere Konfiguration verwenden, um den Kontext-/JSON-
        Vertrag ausserhalb der Isolationsfrage zu pruefen). Der tatsaechliche
        harte Blocker fuer eine unbelegte/riskante Umgebung ist der
        Billing-Var-Check in `decide()` (I2/A3) — er laeuft UNBEDINGT vor
        jedem Request und faengt genau das Szenario, das Test 04 tatsaechlich
        konstruiert (Billing-Sentinel-Vars in der geerbten Umgebung)."""
        rc_v, out_v, err_v = self._runner.run([self.config.binary, "--version"])
        if rc_v != 0:
            raise ProviderUnavailableError(
                f"persona_claude_code[{self.persona_key}]: '{self.config.binary} --version' "
                f"schlug fehl (rc={rc_v}) — CLI nicht verfuegbar, kein unsicherer Betrieb."
            )
        rc_h, out_h, err_h = self._runner.run([self.config.binary, "--help"])
        if rc_h != 0:
            raise ProviderUnavailableError(
                f"persona_claude_code[{self.persona_key}]: '{self.config.binary} --help' "
                f"schlug fehl (rc={rc_h}) — Isolation nicht bestaetigbar."
            )
        if self.config.isolated_workdir is None:
            raise ProviderUnavailableError(
                f"persona_claude_code[{self.persona_key}]: kein eigener Arbeitsbereich "
                f"konfiguriert — 'unavailable' statt Altair-Kontext-Uebernahme."
            )
        if not Path(self.config.isolated_workdir).is_dir():
            raise ProviderUnavailableError(
                f"persona_claude_code[{self.persona_key}]: isolated_workdir "
                f"'{self.config.isolated_workdir}' existiert nicht — 'unavailable' statt "
                f"unbestaetigter Isolation."
            )
        # R09-Fix (WEGKARTE §8, REVIEW-P2R.md R-E): die "synthetic"-Namens-
        # konvention darf NUR gelten, wenn tatsaechlich ein injizierter
        # Testdouble (nicht die echte `_RealProcessRunner`-Binary) als
        # `process_runner` verwendet wird -- sonst schaltet ein blosses Wort
        # im Konfigurationsflag die Isolationspruefung der ECHTEN CLI frei
        # (Test 09: kein injizierter Runner, `--synthetic-format` gegen ein
        # harmloses lokales Testprogramm, das NUR das Ausgabeformat
        # dokumentiert -- keine Rechteeinschraenkung).
        allow_synthetic_convention = not isinstance(self._runner, _RealProcessRunner)
        verified_flags: list[str] = []
        if self.config.extra_isolation_flags:
            # W5-B3-Fix: den Flag-NAMEN (vor einem etwaigen '=') gegen --help
            # pruefen, nicht den vollen 'flag=wert'-String -- eine korrekt
            # formulierte '--flag=wert'-Kombination scheiterte sonst allein
            # daran, dass der Beispielwert nicht woertlich im Hilfetext steht.
            missing_flags = [
                f for f in self.config.extra_isolation_flags
                if f.split("=", 1)[0].strip() not in out_h
            ]
            if missing_flags:
                raise ProviderUnavailableError(
                    f"persona_claude_code[{self.persona_key}]: konfigurierte Isolationsflags "
                    f"{missing_flags} nicht in der '--help'-Ausgabe der installierten CLI "
                    f"gefunden — Isolation nicht belegbar, 'unavailable'."
                )
            # D4/A5 (PLAN-CRITIC-ABSCHLUSS.md WICHTIG, Test 08): Plumbing-
            # Flags (identisch mit der ohnehin fest gesendeten Baseline-Argv)
            # sind PER DEFINITION kein Isolationsbeleg -- unabhaengig davon,
            # ob sie zufaellig im Hilfetext auftauchen.
            if set(self.config.extra_isolation_flags) <= _BASELINE_PLUMBING_FLAGS:
                raise ProviderUnavailableError(
                    f"persona_claude_code[{self.persona_key}]: konfigurierte Isolationsflags "
                    f"{self.config.extra_isolation_flags} bestehen ausschliesslich aus der "
                    f"ohnehin fest gesendeten Baseline-Argv (-p/--output-format/json) -- reines "
                    f"Ausgabeformat-Plumbing ist kein Tool-/MCP-/Hook-/Settings-Isolationsbeleg, "
                    f"'unavailable'."
                )
            for f in self.config.extra_isolation_flags:
                if f in _BASELINE_PLUMBING_FLAGS:
                    continue
                if allow_synthetic_convention and "synthetic" in f.lower():
                    # Baseline-Plumbing-Anteile eines gemischten Sets wurden
                    # bereits oben ausgeschlossen; ein als "synthetic"
                    # gekennzeichnetes Flag ist die etablierte Testkonvention
                    # (03 §5-konform vereinbart, kein erfundenes Flag) --
                    # ABER nur, wenn tatsaechlich ein Testdouble injiziert ist.
                    continue
                if not _is_known_isolation_flag(f, allow_synthetic_convention):
                    raise ProviderUnavailableError(
                        f"persona_claude_code[{self.persona_key}]: Isolationsflag {f!r} ist kein "
                        f"bekannter, dokumentierter Claude-Code-CLI-Isolationsschalter "
                        f"({sorted(_KNOWN_ISOLATION_FLAG_NAMES)}) -- ein blosses Vokabular-"
                        f"Vorkommen ('tools'/'MCP'/'hooks'/...) in einem Diagnose-Hilfetext ist "
                        f"KEIN Rechteentzug (Test 11), gegen die echte Binary zaehlt auch das "
                        f"Wort 'synthetic' nicht als Beleg (Test 09), 'unavailable'."
                    )
            verified_flags = list(self.config.extra_isolation_flags)
            # W5-Fix (F5, PLAN-CRITIC.md Auflage 5, Test 08): gegen die ECHTE
            # Binary (kein injizierter Testdouble) reicht ein einzelner
            # bekannter Schalter nicht mehr -- er muss tatsaechlich eine
            # Tool-Restriktion UND eine Hook-/MCP-/Settings-Restriktion
            # zusammen belegen (empirisch aus der echten --help bestimmt,
            # s. `_TOOL_RESTRICTING_FLAG_NAMES`/`_BROAD_ISOLATION_FLAG_
            # NAMES` oben). Ein einzelnes `--strict-mcp-config` begrenzt
            # laut eigenem --help-Text NUR MCP-Quellen -- Tools bleiben
            # unangetastet, Hooks/Settings/Plugins bleiben unangetastet --
            # das ist keine umfassende Isolation (Test 08 rejects genau
            # diesen Fall). Testdoubles (`allow_synthetic_convention`)
            # bleiben von dieser zusaetzlichen Pflicht unberuehrt -- sie
            # pruefen andere Verhaltensaspekte (Billing-Vars, argv/stdin/
            # JSON-Dekodierung) und haben Isolationsgenuege bereits durch
            # Testkonstruktion, nicht durch reale Flagvielfalt."""
            if not allow_synthetic_convention:
                # I3-Fix (MAIN-ENTSCHEIDUNG I3-Regel, PLAN-CRITIC F10/Auflage,
                # Case 06/08): kleine KANONISCHE Gesamtkonfiguration statt OR
                # ueber Teilbedingungen. "LETZTER WERT GEWINNT" je Flag-NAME
                # (dict-Ueberschreiben in `verified_flags`-Reihenfolge) --
                # UNVERAENDERT gegenueber der Vorfassung. NEU (schliesst den
                # Rest-Bug, Test 08 `review_p2q_request_contract.py`): jeder
                # Flag-NAME wird zusaetzlich klassifiziert
                # ('restrictive'/'open'/'unknown', s. `_classify_tool_flag_
                # value`/`_classify_broad_flag_value`) -- ein 'open' (z.B.
                # `--permission-mode=bypassPermissions`, `--tools=default`)
                # oder 'unknown' (z.B. `--safe-mode=garbage`) AN IRGENDEINER
                # Stelle lehnt die GESAMTE Kombination ab, UNABHAENGIG davon,
                # ob ein ANDERES Flag fuer sich genommen restriktiv waere --
                # die alte Fassung liess genau das durch (`any(...)` ueber
                # alle Tool-Flags maskierte einen gleichzeitigen expliziten
                # Bypass auf einem anderen Flag-Namen).
                parsed = [_parse_isolation_flag(f) for f in verified_flags]
                bare_value_flags: list[str] = []
                final_class_by_name: dict[str, str] = {}
                for _name, _has_value, _value in parsed:
                    if _name in _TOOL_RESTRICTING_FLAG_NAMES:
                        if not _has_value:
                            # W5-B3-Fix (Main-Nacharbeit, End-Critic BLOCKER
                            # 3): ein blanker wertnehmender Schalter (ohne
                            # '=wert') wird IMMER abgelehnt -- an der echten
                            # CLI wuerde er das naechste argv-Token als Wert
                            # verschlucken, unabhaengig von einer spaeteren
                            # '=wert'-Occurrence desselben Flags.
                            bare_value_flags.append(_name)
                            final_class_by_name[_name] = "unknown"
                        else:
                            final_class_by_name[_name] = _classify_tool_flag_value(_name, _value)
                    elif _name in _BROAD_ISOLATION_FLAG_NAMES:
                        final_class_by_name[_name] = _classify_broad_flag_value(_has_value, _value)
                if bare_value_flags:
                    raise ProviderUnavailableError(
                        f"persona_claude_code[{self.persona_key}]: wertnehmende Isolationsflags "
                        f"{bare_value_flags} ohne '=wert'-Form -- an der echten CLI wuerden sie das "
                        f"naechste argv-Token als Wert verschlucken statt zu isolieren; Werte "
                        f"explizit als '--flag=wert' angeben, 'unavailable' VOR jeder Inferenz."
                    )
                conflicting = {n: c for n, c in final_class_by_name.items() if c in ("open", "unknown")}
                if conflicting:
                    raise ProviderUnavailableError(
                        f"persona_claude_code[{self.persona_key}]: Isolationsflag-Kombination "
                        f"{self.config.extra_isolation_flags} enthaelt einen expliziten Bypass-/"
                        f"widerspruechlichen oder unbekannten Wert ({conflicting}) -- ein "
                        f"restriktiver Token an anderer Stelle neutralisiert das NICHT (kleine "
                        f"kanonische Gesamtkonfiguration statt OR ueber Teilbedingungen), "
                        f"'unavailable' VOR jeder Inferenz."
                    )
                effective_tool = any(
                    c == "restrictive" for n, c in final_class_by_name.items()
                    if n in _TOOL_RESTRICTING_FLAG_NAMES
                )
                has_broad_restriction = any(
                    c == "restrictive" for n, c in final_class_by_name.items()
                    if n in _BROAD_ISOLATION_FLAG_NAMES
                )
                if not (effective_tool and has_broad_restriction):
                    raise ProviderUnavailableError(
                        f"persona_claude_code[{self.persona_key}]: konfigurierte Isolationsflags "
                        f"{self.config.extra_isolation_flags} belegen gegen die echte CLI keine "
                        f"hinreichende Kombination MIT WIRKSAMEN WERTEN -- benoetigt wird "
                        f"mindestens ein Tool-restriktives Flag mit wirksamem Wert (z.B. "
                        f"'--permission-mode=plan', '--permission-mode=manual', '--tools=' (alle "
                        f"Tools aus) oder '--allowed-tools=<liste>'; NICHT "
                        f"'--permission-mode=bypassPermissions' oder '--tools=default') UND "
                        f"{sorted(_BROAD_ISOLATION_FLAG_NAMES)} (deckt laut --help Hooks/MCP/"
                        f"Settings/Plugins ab) zusammen -- ein einzelnes Teilgrenzen-Flag (z.B. "
                        f"'--strict-mcp-config', begrenzt NUR MCP-Quellen) ist keine umfassende "
                        f"Isolation, 'unavailable' VOR jeder Inferenz."
                    )
        isolation_flags_configured = bool(self.config.extra_isolation_flags)
        if not isolation_flags_configured:
            # F4/A2 (WEGKARTE §6, alt->neu dokumentiert): eine fehlende/nicht
            # belegte Tool-/MCP-/Hook-/Settings-Isolation ist ab jetzt ein
            # HARTER Abbruch VOR jeder Inferenz -- kein blosses Logging mehr
            # (fruehere Fassung liess unverifizierte Isolation als Erfolg mit
            # WARNING durch; das brach an genau diesem Codepfad review_p2f_
            # paths.py Test 07). Die zwei betroffenen Bestandstests
            # `test_claude_code_isolation_unverified_without_flags_is_not_a_
            # hard_block`/`..._logs_warning` wurden im selben Zug bewusst auf
            # `ProviderUnavailableError` umgeschrieben (semantisch notwendige
            # Testanpassung, 04 §3). Kontext-/JSON-Erfolgstests (P2F 02/03)
            # konfigurieren bereits eine kontrollierte Test-Capability
            # (`extra_isolation_flags=['--synthetic-safe']`) und bleiben
            # davon unberuehrt gruen.
            _LOG.warning(
                "persona_claude_code[%s]: keine extra_isolation_flags konfiguriert -- "
                "Tool-/MCP-/Hook-/Settings-Isolation (03 §5) ist NICHT verifiziert -- "
                "unavailable VOR jeder Inferenz, kein unsicherer Betrieb.",
                self.persona_key,
            )
            raise ProviderUnavailableError(
                f"persona_claude_code[{self.persona_key}]: keine extra_isolation_flags "
                f"konfiguriert -- Tool-/MCP-/Hook-/Settings-Isolation (03 §5) nicht belegt, "
                f"'unavailable' VOR jeder Inferenz (kein unsicherer Betrieb)."
            )
        self._isolation_checked = True
        return {
            "version_output": out_v.strip(), "help_output_len": len(out_h),
            "verified_isolation_flags": verified_flags,
            "isolation_flags_configured": isolation_flags_configured,
        }

    def _check_billing_vars(self) -> None:
        """I2/A3: Umgebungsvariablen, die versehentlich API-Abrechnung statt
        Abo auswaehlen koennten, MUESSEN vor einer Anfrage gemeldet werden
        (03 §4) — kein stiller Versand mit potenziell falscher Abrechnung."""
        present = [v for v in BILLING_RISK_ENV_VARS if os.environ.get(v)]
        if present:
            raise ProviderUnavailableError(
                f"persona_claude_code[{self.persona_key}]: Umgebungsvariable(n) {present} "
                f"koennten versehentlich API-Abrechnung statt Abo auswaehlen — kein Request "
                f"ohne Bereinigung der Umgebung."
            )

    def decide(self, context: dict) -> ParticipantDecision:
        if not self._isolation_checked:
            self.check_isolation()
        self._check_billing_vars()
        argv = [self.config.binary, "-p", "--output-format", "json"]
        argv.extend(self.config.extra_isolation_flags)
        system_text = context.get("system", "")
        user_text = render_public_wire_text(context)
        # I2: identischer semantischer Vertrag wie der API-Adapter -- system
        # UND user werden transportiert (vorher: system verworfen). STDIN
        # bleibt der einzige Kanal (kein aus Spielertext gebauter Shellbefehl).
        stdin_payload = f"[SYSTEM]\n{system_text}\n\n[USER]\n{user_text}" if system_text else user_text
        # A5/D4 (WEGKARTE §8, Plan-Critic A5 Befund 2, Test 11): MINIMALES
        # Kind-Env -- nur eine kuratierte Allowlist (PATH/HOME/... fuer einen
        # lauffaehigen Kindprozess, B2), KEINE volle `os.environ`-Vererbung
        # mehr. Rollen-/Secret-Keys (z.B. `OPENWEBUI_API_KEY`) werden NICHT
        # an die Persona-CLI weitergereicht.
        env = {k: v for k, v in os.environ.items() if k in _CHILD_ENV_ALLOWLIST}
        env["CLAUDE_WORKDIR"] = self.config.isolated_workdir or ""
        try:
            rc, out, err = self._runner.run(
                argv, stdin=stdin_payload, env=env, cwd=self.config.isolated_workdir,
            )
        except FileNotFoundError as e:
            raise ProviderUnavailableError(
                f"persona_claude_code[{self.persona_key}]: Binary nicht gefunden: {e}"
            ) from e
        except subprocess.TimeoutExpired as e:
            raise ProviderUnavailableError(
                f"persona_claude_code[{self.persona_key}]: Zeitueberschreitung: {e}"
            ) from e
        if rc != 0:
            raise ProviderUnavailableError(
                f"persona_claude_code[{self.persona_key}]: Prozess rc={rc}: {err[:300]}"
            )
        # I2/Test 03: die --output-format-json-Huelle DEKODIEREN statt als
        # rohen stdout durchzureichen. Faellt das Parsen aus (aeltere CLI
        # ohne JSON-Huelle o.ae.), bleibt der rohe stdout ein defensiver
        # Fallback -- kein Absturz, aber keine stille Fehlmaskierung von
        # `is_error`.
        text = out.strip()
        meta: dict = {"returncode": rc}
        try:
            payload = json.loads(out)
        except (json.JSONDecodeError, ValueError):
            payload = None
        if isinstance(payload, dict) and "result" in payload:
            if payload.get("is_error"):
                raise ProviderUnavailableError(
                    f"persona_claude_code[{self.persona_key}]: CLI meldet is_error: "
                    f"{str(payload.get('result'))[:300]}"
                )
            text = payload.get("result", "")
            meta["usage"] = payload.get("usage") or {}
            meta["cli_type"] = payload.get("type")
            meta["cli_subtype"] = payload.get("subtype")
        return ParticipantDecision(
            text=text,
            origin_source=f"persona_claude_code:{self.config.binary}",
            meta=meta,
        )
