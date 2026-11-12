#!/usr/bin/env python3
"""
mmo_sim/ui/sheet_view.py — lokaler, read-only Charakterbogen (ZR-SPIEL-
FINISH-P2 Block B).

Reine Projektion eines bereits VORHANDENEN v7-Save-Blocks (`core.store.
load_current_save_or_raise`, s. `ui/tui.py:TuiSession._cmd_show_bogen`) auf
lesbare Textzeilen -- KEINE Regelberechnung, KEINE Mutation, KEIN GM-/
Netzaufruf, KEIN neuer mmo_sim-Spielstart. Fehlende Felder erscheinen
explizit als "nicht gespeichert"/"—" statt stillschweigend erfundener
Null-/Vollwerte (Flo will seinen gespeicherten Stand ansehen, nicht eine
Vermutung darüber).

Feldquelle: das kanonische v7-`characters[0]`-Schema aus `meta/
masterprompt_v6.md` §F (`attr`, `lp`/`lp_max`, `has_psi`/`pp`/`pp_max`/
`psi_heat`, `sys_installed`, `talents`/`equipment`/`implants` als
Namensliste ODER Objektliste mit `name`/`tier`/`effect`, `reputation.iti`/
`reputation.faction`, `wallet`) -- mit defensiven Fallbacks auf ältere
Beispielfeldnamen (`attributes`, `hp`/`hp_max`), falls ein Altstand vor
seiner Migration gelesen wird. Talente/Ausrüstung/Implantate werden NUR so
detailliert angezeigt, wie sie TATSÄCHLICH im Save stehen (reine Namen
bleiben reine Namen) -- keine Stufen/Wirkungen werden aus einem externen
Regel-/Talentkatalog nachgeschlagen.

Separat (`try_open_in_external_terminal`): optionaler Fensteröffner für
einen VORHANDENEN Terminalemulator (xterm/gnome-terminal) über einen
kleinen, direkten argv-Aufruf -- KEINE Shell-Interpolation von Namen/
Inhalten, kein FIFO-Gastprozess, keine neue IPC/einen zweiten Spielprozess.
Schreibt den fertigen Text in eine PRIVATE temporäre Datei (keine Save-
Autorität) und startet denselben Renderer hier (`main()`, `--show`) als
reinen Anzeige-Unterprozess. Liefert `False`, wenn kein Emulator verfügbar
ist oder der Start fehlschlägt -- der Aufrufer (`TuiSession._cmd_show_
bogen`) zeigt dann denselben Inhalt inline im vorhandenen Terminal, ohne
den aktuellen Prompt zu verlassen.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from . import rendering

NOT_SAVED = "nicht gespeichert"
DASH = "—"

#: Dauerhafter Kopf (Vertrag Block B): macht JEDEM Blick sofort klar, dass
#: dies eine statische Projektion ist, kein Live-Fenster -- der GM-Bogen
#: (laufendes Spiel) kann aktueller sein als dieser Snapshot.
HEADER_LINES = (
    "ZIRKEL · Nadia Kersten — letzter gespeicherter Stand",
    "Statische Anzeige. Laufende Aenderungen im Spiel sind hier nicht "
    "enthalten; der GM-Bogen kann aktueller sein.",
)


def _get(d: object, *keys: str) -> object:
    """Erster vorhandener, nicht-`None`-Wert unter `keys` in `d` (`d` muss
    ein dict sein, sonst `None`) -- EIN Helfer fuer die kanonische UND die
    aeltere Fallback-Feldbenennung, kein Raten/Default-Erfinden."""
    if not isinstance(d, dict):
        return None
    for key in keys:
        value = d.get(key)
        if value is not None:
            return value
    return None


def _fmt_item(item: object) -> str:
    if isinstance(item, dict):
        name = _get(item, "name") or NOT_SAVED
        extras = [
            str(v) for k, v in item.items()
            if k != "name" and v not in (None, "", [])
        ]
        return f"{name} ({', '.join(extras)})" if extras else str(name)
    return str(item)


def _fmt_talent(talent: object) -> str:
    """Talente stehen im Save MEIST als reiner Namensstring; manche
    Exporte tragen zusaetzlich `tier`/`stufe` + `effect`/`wirkung` direkt
    im Save-Objekt (belegt in Spielprotokollen) -- NUR dann werden Stufe/
    Wirkung angezeigt, nie aus einem externen Katalog nachgeschlagen."""
    if isinstance(talent, dict):
        name = _get(talent, "name") or NOT_SAVED
        tier = _get(talent, "tier", "stufe", "level")
        effect = _get(talent, "effect", "wirkung")
        bits = []
        if tier not in (None, ""):
            bits.append(f"Stufe {tier}")
        if effect:
            bits.append(str(effect))
        return f"{name} — {'; '.join(bits)}" if bits else str(name)
    return str(talent)


def render_character_sheet(save: dict, *, persona_key: str) -> list[str]:
    """Reine, read-only Darstellungszeilen fuer `save["characters"][0]`.
    Ruft NICHTS auf ausser bereits uebergebenen Daten -- keine Datei-/
    Netz-/Modell-Zugriffe, kein Speichern/Reparieren/Adoptieren."""
    chars = save.get("characters") if isinstance(save, dict) else None
    char = chars[0] if isinstance(chars, list) and chars and isinstance(chars[0], dict) else {}

    lines: list[str] = list(HEADER_LINES)
    lines.append("")

    lines.append(f"Name: {_get(char, 'name') or NOT_SAVED}")
    lines.append(f"Callsign: {_get(char, 'callsign') or NOT_SAVED}")

    origin = _get(char, "origin") or {}
    herkunft = [v for v in (
        _get(origin, "epoch"), _get(origin, "hominin"), _get(origin, "role"),
    ) if v]
    lines.append(f"Herkunft: {', '.join(str(h) for h in herkunft) if herkunft else NOT_SAVED}")

    rang = _get(char, "rank") or NOT_SAVED
    lvl = _get(char, "lvl", "level")
    xp = _get(char, "xp")
    lines.append(
        f"Rang: {rang} — Level: {lvl if lvl is not None else NOT_SAVED} — "
        f"XP: {xp if xp is not None else NOT_SAVED}"
    )

    attr = _get(char, "attr", "attributes") or {}
    attr_bits = [
        f"{k} {attr.get(k) if isinstance(attr, dict) and attr.get(k) is not None else DASH}"
        for k in ("STR", "GES", "INT", "CHA", "TEMP", "SYS")
    ]
    lines.append("Attribute: " + " · ".join(attr_bits))

    lp = _get(char, "lp", "hp")
    lp_max = _get(char, "lp_max", "hp_max")
    lines.append(
        f"LP: {lp if lp is not None else DASH}/{lp_max if lp_max is not None else DASH}"
    )

    stress = _get(char, "stress")
    lines.append(f"Stress: {stress if stress is not None else NOT_SAVED}")

    psi_sys_bits = []
    if _get(char, "has_psi"):
        pp = _get(char, "pp")
        pp_max = _get(char, "pp_max")
        psi_heat = _get(char, "psi_heat")
        if pp is not None or pp_max is not None:
            psi_sys_bits.append(
                f"PP {pp if pp is not None else DASH}/{pp_max if pp_max is not None else DASH}"
            )
        if psi_heat is not None:
            psi_sys_bits.append(f"Psi-Heat {psi_heat}")
    sys_val = attr.get("SYS") if isinstance(attr, dict) else None
    sys_installed = _get(char, "sys_installed")
    if sys_val is not None:
        psi_sys_bits.append(f"SYS {sys_val}")
    if sys_installed is not None:
        psi_sys_bits.append(f"installiert {sys_installed}")
    lines.append(f"Psi/SYS: {' · '.join(psi_sys_bits) if psi_sys_bits else NOT_SAVED}")

    talents = _get(char, "talents")
    lines.append("Talente:")
    if isinstance(talents, list) and talents:
        for t in talents:
            lines.append(f"  - {_fmt_talent(t)}")
    else:
        lines.append(f"  {NOT_SAVED}")

    for label, key in (("Ausruestung", "equipment"), ("Implantate", "implants")):
        items = _get(char, key)
        lines.append(f"{label}:")
        if isinstance(items, list) and items:
            for it in items:
                lines.append(f"  - {_fmt_item(it)}")
        else:
            lines.append(f"  {NOT_SAVED}")

    wallet = _get(char, "wallet")
    lines.append(f"Geld: {wallet if wallet is not None else NOT_SAVED}")

    reputation = _get(char, "reputation") or {}
    ruf_bits = []
    iti = _get(reputation, "iti")
    faction = _get(reputation, "faction")
    if iti is not None:
        ruf_bits.append(f"ITI {iti}")
    if faction:
        ruf_bits.append(f"Fraktion {faction}")
    lines.append(f"Ruf: {' · '.join(ruf_bits) if ruf_bits else NOT_SAVED}")

    lines.append("")
    char_id = _get(char, "id") or NOT_SAVED
    save_id = save.get("save_id") if isinstance(save, dict) else None
    lines.append(
        f"Quelle: Char-ID {char_id} · Save-ID {save_id or NOT_SAVED} · "
        f"Teilnehmer {persona_key}"
    )

    # WP-P2-B: dieselbe bestehende Sicherheitsstufe wie jeder andere
    # Modelltext (`rendering.strip_dangerous_control_chars`) -- Save-Werte
    # (Name, Talente, ...) sind urspruenglich Modelltext und koennten
    # theoretisch rohe Steuerzeichen (insb. ESC) tragen. Reine ANSI-
    # Markdown-Uebersetzung (`render_for_terminal`) ist hier NICHT
    # gewuenscht (strukturierte Datenzeilen, kein Fliesstext).
    return [rendering.strip_dangerous_control_chars(line) for line in lines]


#: (Programm, Praefix-Argv) -- probiert in dieser Reihenfolge, der erste
#: tatsaechlich vorhandene Emulator gewinnt. Kein Shell-String, reines argv.
_TERMINAL_CANDIDATES = (
    ("xterm", ["-T", "ZEITRISS - Bogen", "-e"]),
    ("gnome-terminal", ["--"]),
)


def try_open_in_external_terminal(lines: list[str], *, popen_fn=subprocess.Popen) -> bool:
    """Versucht, `lines` in einem EIGENEN Terminalfenster zu zeigen (kein
    neuer Spielprozess, reiner Renderer -- s. `main()`/`--show`). Schreibt
    die Zeilen in eine PRIVATE temporaere Datei (keine Save-Autoritaet,
    `tempfile.NamedTemporaryFile(delete=False)`) und startet GENAU EINEN
    kleinen, direkten argv-Aufruf (kein Shell, keine String-Interpolation
    von Namen/Inhalten). Liefert `True` nur bei erfolgreichem Prozessstart;
    `False`, wenn kein bekannter Emulator installiert ist oder der Start
    fehlschlaegt -- der Aufrufer zeigt denselben Inhalt dann inline."""
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", prefix="zr-bogen-", delete=False, encoding="utf-8",
    )
    try:
        tmp.write("\n".join(lines) + "\n")
    finally:
        tmp.close()

    renderer_argv = [sys.executable, "-m", "mmo_sim.ui.sheet_view", "--show", tmp.name]
    for exe, prefix_args in _TERMINAL_CANDIDATES:
        if shutil.which(exe) is None:
            continue
        argv = [exe, *prefix_args, *renderer_argv]
        try:
            popen_fn(argv)
            return True
        except OSError:
            continue
    return False


def _show_file_and_wait(path: str, *, input_fn=input, print_fn=print) -> None:
    text = Path(path).read_text(encoding="utf-8")
    print_fn(text)
    try:
        input_fn("\n(Enter zum Schliessen) ")
    except EOFError:
        pass


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) == 2 and argv[0] == "--show":
        _show_file_and_wait(argv[1])
        return 0
    print("Nutzung: python3 -m mmo_sim.ui.sheet_view --show <datei>")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
