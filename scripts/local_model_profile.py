"""Gemeinsamer Daten-/Validierungsresolver fuer den lokalen Tokenhost-Pfad
(ZR-LOCAL-TOKENHOST-L1).

Nur Datenlesen/Validierung/Profilauflösung -- KEIN Transport, KEIN Prozess,
keine automatische Einrichtung. Die eigentliche Datei-IO bleibt bei den
bestehenden Helfern in `scripts/setup.py` (`_read_env_file` /
`_update_env_file_preserving`); dieses Modul bekommt ein bereits gelesenes
dict und liefert entweder ein validiertes `LocalModelProfile` oder einen
benannten `ProfileHold`-Grund. Kein Modul-/Prozessstatus wird hier
gecacht -- jeder Aufruf bewertet genau das übergebene dict neu, sodass ein
frisch geladener Resolver nie eine In-Memory-Zuweisung eines fremden
Aufrufs erbt.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

PROVIDER_CLOUD = "cloud"
PROVIDER_LOCAL = "local"

ENV_KEY_PROVIDER = "ZEITRISS_MODEL_PROVIDER"
ENV_KEY_BASE_URL = "ZEITRISS_LOCAL_BASE_URL"
ENV_KEY_MODEL = "ZEITRISS_LOCAL_MODEL"
ENV_KEY_API_KEY = "ZEITRISS_LOCAL_API_KEY"
ENV_KEY_OWUI_BASE_URL = "ZEITRISS_LOCAL_OWUI_BASE_URL"
ENV_KEY_GM_MAX_TOKENS = "ZEITRISS_LOCAL_GM_MAX_TOKENS"
ENV_KEY_PERSONA_MAX_TOKENS = "ZEITRISS_LOCAL_PERSONA_MAX_TOKENS"

DEFAULT_GM_MAX_TOKENS = 4096
DEFAULT_PERSONA_MAX_TOKENS = 400

LOCAL_FIELD_KEYS = frozenset(
    {
        ENV_KEY_BASE_URL,
        ENV_KEY_MODEL,
        ENV_KEY_API_KEY,
        ENV_KEY_OWUI_BASE_URL,
        ENV_KEY_GM_MAX_TOKENS,
        ENV_KEY_PERSONA_MAX_TOKENS,
    }
)

_URL_RE = re.compile(r"^(https?)://([^/@\s?#]+)(/.*)?$")


def _has_control_chars(s: str) -> bool:
    """A3-Fix (02_NACHARBEIT.md Gruppe A.3, "URLs lehnen ALLE Steuerzeichen
    ab, nicht nur CR/LF/NUL"): VORHER prueften diese Felder nur `\\r`/`\\n`/
    `\\x00` -- jedes andere ASCII-Steuerzeichen (z.B. `\\t`, `\\x01..\\x1f`,
    `\\x7f`) rutschte unerkannt durch. Jetzt JEDES Zeichen mit Codepoint
    < 0x20 ODER == 0x7F (DEL) gilt als Steuerzeichen -- gilt fuer URL-
    UND Secret-/Modellfelder gleich (`is_valid_local_url`/
    `is_valid_secret_field` rufen beide diese eine Funktion)."""
    return any(ord(c) < 0x20 or ord(c) == 0x7F for c in s)


def _round_trips_as_bare_value(value: str) -> bool:
    """N4-02 ("Token niemals still trimmen/entquoten. Ein akzeptierter Token
    muss exakt roundtrippen; schwer darstellbare Eingaben duerfen wertfrei
    vor jedem Schreiben abgelehnt werden"): ein roher `KEY=value`-Schreib-
    zugriff (kein Escaping, s. `setup._update_env_file_preserving`) roundtrippt
    nur exakt, wenn `parse_env_text` (derselbe Vertrag, den `setup._read_env_
    file`/`_auto_load_owui_env`/`launcher._parse_env_file` jetzt alle benutzen)
    denselben Wert zurueckliest -- also KEIN fuehrendes/abschliessendes
    Leerzeichen (wird beim Lesen gestrippt) UND KEIN fuehrendes+abschliessendes
    Quotezeichen (wird als umschliessendes Quote-Paar interpretiert und
    entfernt). Reine Formpruefung, kein Werteabgleich -- die Aufrufstelle
    entscheidet, ob sie bei `False` wertfrei (ohne den Wert selbst zu
    drucken/loggen) ablehnt."""
    if value != value.strip():
        return False
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return False
    return True


def parse_env_text(text: str) -> tuple[dict, frozenset]:
    """N4-02: EIN gemeinsamer KEY=VALUE-Parservertrag fuer alle drei Leser
    (`setup._read_env_file`, `setup._auto_load_owui_env`,
    `launcher._parse_env_file`) -- vorher drei fast identische, aber
    unabhaengig gepflegte Schleifen. Unterstuetzt optionales `export `-
    Praefix, Kommentare (`#`) und leere Zeilen, genau EIN umschliessendes
    Quote-Paar (einfach/doppelt). Keine Shellauswertung, kein rekursives/
    mehrfaches Quote-Stripping (anders als das frühere `.strip('"').strip("'")`
    an allen drei Stellen, das theoretisch mehrere Quote-Zeichen an einer
    Kante entfernt haette -- "genau EIN Paar" ist jetzt wirklich exakt EIN
    Paar).

    Liefert `(values, conflicting_keys)`: `values` ist das flache
    KEY->VALUE-dict (bei mehrfacher Nennung desselben Keys gilt der zuletzt
    gesehene Wert als Fallback fuer Aufrufer, die den Vertrag nicht extra
    pruefen). `conflicting_keys` enthaelt jeden Key, der MEHRFACH mit
    UNTERSCHIEDLICHEN Werten auftaucht (identische Duplikate sind erlaubt
    und tauchen dort NICHT auf) -- `resolve_provider`/`resolve_local_profile`
    pruefen das fuer ihre jeweils relevanten Felder und halten sichtbar
    (kein last-wins) statt eines der widerspruechlichen Werte stillschweigend
    zu uebernehmen."""
    values: dict = {}
    conflicting: set = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):]
        if "=" not in line:
            continue
        k, _, v = line.partition("=")
        k = k.strip()
        if not k:
            continue
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in ('"', "'"):
            v = v[1:-1]
        if k in values and values[k] != v:
            conflicting.add(k)
        values[k] = v
    return values, frozenset(conflicting)


class ProfileHold(Exception):
    """Benannter Haltegrund. Kein stiller Cloudfallback, keine
    Session-only-Scheinaktivierung -- jeder Aufrufer MUSS bei dieser
    Exception den bisherigen/sicheren Zustand behalten statt lokal
    "erfolgreich" zu melden."""


@dataclass(frozen=True)
class LocalModelProfile:
    base_url: str
    model: str
    api_key: str
    owui_base_url: Optional[str]
    gm_max_tokens: int
    persona_max_tokens: int


def is_valid_local_url(url: str) -> bool:
    """http(s) + Host[:Port], kein eingebettetes Credential/Query/Fragment,
    keine Steuerzeichen."""
    if not url or _has_control_chars(url):
        return False
    url = url.strip()
    if "?" in url or "#" in url:
        return False
    m = _URL_RE.match(url)
    if not m:
        return False
    scheme, host = m.group(1), m.group(2)
    if scheme not in ("http", "https"):
        return False
    if "@" in host:
        return False
    if ":" in host:
        hostpart, _, portpart = host.rpartition(":")
        if not hostpart or not portpart.isdigit():
            return False
        port = int(portpart)
        if not (1 <= port <= 65535):
            return False
    return True


def is_valid_secret_field(value: str) -> bool:
    """Modell-ID/Token: nicht leer, keine CR/LF/NUL."""
    return bool(value) and not _has_control_chars(value)


def _valid_positive_int(value) -> Optional[int]:
    try:
        n = int(str(value).strip())
    except (TypeError, ValueError, AttributeError):
        return None
    if n <= 0:
        return None
    return n


def resolve_provider(env: dict, conflicting_keys: frozenset = frozenset()) -> str:
    """Gibt 'cloud' | 'local' | 'legacy' | 'hold' zurueck.

    'legacy' = ZEITRISS_MODEL_PROVIDER fehlt komplett (Schluessel nicht im
    dict) -> bisheriges Cloud-/CLI-/API-Verhalten unveraendert. 'hold' =
    Schluessel vorhanden, aber Wert ausdruecklich leer/unbekannt/inkonsistent
    -- MUSS sichtbar halten, niemals raten/auf 'legacy' zurueckfallen.
    N1-03: ein fehlendes Feld (Datei/Env erwaehnt den Schluessel nie) und ein
    ausdruecklich leeres Feld (`ZEITRISS_MODEL_PROVIDER=`) sind NICHT
    derselbe Zustand -- nur das echte Fehlen des Schluessels ist 'legacy'.

    N4-02: `conflicting_keys` (aus `parse_env_text`) -- steht
    `ZEITRISS_MODEL_PROVIDER` selbst mehrfach mit WIDERSPRECHENDEN Werten in
    der Datei, haelt dieser Resolver sichtbar statt last-wins einen der
    beiden Werte zu uebernehmen. Optional/leer per Default, damit bestehende
    Aufrufer, die nur ein bereits geparstes dict uebergeben, unveraendert
    funktionieren."""
    if ENV_KEY_PROVIDER in conflicting_keys:
        return "hold"
    if ENV_KEY_PROVIDER not in env:
        return "legacy"
    raw = (env.get(ENV_KEY_PROVIDER) or "").strip()
    if raw == "":
        return "hold"
    low = raw.lower()
    if low == PROVIDER_CLOUD:
        return PROVIDER_CLOUD
    if low == PROVIDER_LOCAL:
        return PROVIDER_LOCAL
    return "hold"


def resolve_local_profile(env: dict, conflicting_keys: frozenset = frozenset()) -> LocalModelProfile:
    """Validiert alle ZEITRISS_LOCAL_*-Felder aus einem bereits gelesenen
    env-dict (z.B. `_read_env_file(Path.home() / ".openwebui_env")`).
    Wirft `ProfileHold` mit konkretem Grund statt stillem Fallback/Erbe
    von Cloud-Werten (64000/reasoning/Vision/variant_base_model etc. werden
    hier bewusst NICHT gelesen).

    N4-02: `conflicting_keys` (aus `parse_env_text`) -- erscheint eines der
    `LOCAL_FIELD_KEYS` mehrfach mit WIDERSPRECHENDEN Werten in der Datei,
    haelt diese Funktion sichtbar (`ProfileHold`) statt last-wins einen der
    Werte zu uebernehmen. Optional/leer per Default, identisch zu
    `resolve_provider`."""
    _conflicting_local = conflicting_keys & LOCAL_FIELD_KEYS
    if _conflicting_local:
        raise ProfileHold(
            "widersprüchliche doppelte Werte für " + ", ".join(sorted(_conflicting_local))
        )
    base_url = (env.get(ENV_KEY_BASE_URL) or "").strip()
    model = (env.get(ENV_KEY_MODEL) or "").strip()
    api_key = env.get(ENV_KEY_API_KEY) or ""
    owui_base_url_raw = (env.get(ENV_KEY_OWUI_BASE_URL) or "").strip()

    if not is_valid_local_url(base_url):
        raise ProfileHold(f"{ENV_KEY_BASE_URL} fehlt oder ist ungueltig")
    if not is_valid_secret_field(model):
        raise ProfileHold(f"{ENV_KEY_MODEL} fehlt oder ist ungueltig")
    if not is_valid_secret_field(api_key):
        raise ProfileHold(f"{ENV_KEY_API_KEY} fehlt oder ist ungueltig")

    owui_base_url = None
    if owui_base_url_raw:
        if not is_valid_local_url(owui_base_url_raw):
            raise ProfileHold(f"{ENV_KEY_OWUI_BASE_URL} ist ungueltig")
        owui_base_url = owui_base_url_raw

    gm_raw = env.get(ENV_KEY_GM_MAX_TOKENS)
    gm_max = DEFAULT_GM_MAX_TOKENS if gm_raw in (None, "") else _valid_positive_int(gm_raw)
    if gm_max is None:
        raise ProfileHold(f"{ENV_KEY_GM_MAX_TOKENS} muss positiv und endlich sein")

    persona_raw = env.get(ENV_KEY_PERSONA_MAX_TOKENS)
    persona_max = (
        DEFAULT_PERSONA_MAX_TOKENS
        if persona_raw in (None, "")
        else _valid_positive_int(persona_raw)
    )
    if persona_max is None:
        raise ProfileHold(f"{ENV_KEY_PERSONA_MAX_TOKENS} muss positiv und endlich sein")

    return LocalModelProfile(
        base_url=base_url,
        model=model,
        api_key=api_key,
        owui_base_url=owui_base_url,
        gm_max_tokens=gm_max,
        persona_max_tokens=persona_max,
    )


def build_local_profile_updates(
    *,
    base_url: str,
    model: str,
    api_key: str,
    owui_base_url: Optional[str] = None,
    gm_max_tokens: int = DEFAULT_GM_MAX_TOKENS,
    persona_max_tokens: int = DEFAULT_PERSONA_MAX_TOKENS,
) -> dict:
    """Validiert neue Eingaben (z.B. aus getpass/input in launcher.py) und
    liefert das `updates`-dict fuer `_update_env_file_preserving` -- reines
    Daten-Mapping, kein Dateizugriff hier. Wirft `ProfileHold` bei
    ungueltigen Eingaben (Aufrufer darf dann NICHT persistieren)."""
    if not is_valid_local_url(base_url):
        raise ProfileHold(f"{ENV_KEY_BASE_URL} ist ungueltig")
    if not is_valid_secret_field(model):
        raise ProfileHold(f"{ENV_KEY_MODEL} ist ungueltig")
    if not is_valid_secret_field(api_key):
        raise ProfileHold(f"{ENV_KEY_API_KEY} ist ungueltig")
    if not _round_trips_as_bare_value(api_key):
        # N4-02: wertfreie Ablehnung VOR jedem Schreiben -- dieser Token
        # wuerde beim naechsten Readback (ueber `parse_env_text`) NICHT
        # bytegleich zurueckgelesen (fuehrendes/abschliessendes Leerzeichen
        # oder Quote-Zeichen). Die Meldung nennt bewusst NICHT den Wert
        # selbst.
        raise ProfileHold(
            f"{ENV_KEY_API_KEY} laesst sich nicht verlustfrei als KEY=VALUE roundtrippen "
            "(fuehrendes/abschliessendes Leerzeichen oder Quote-Zeichen) -- wertfrei abgelehnt"
        )
    gm_max = _valid_positive_int(gm_max_tokens if gm_max_tokens is not None else DEFAULT_GM_MAX_TOKENS)
    if gm_max is None:
        raise ProfileHold(f"{ENV_KEY_GM_MAX_TOKENS} muss positiv und endlich sein")
    persona_max = _valid_positive_int(
        persona_max_tokens if persona_max_tokens is not None else DEFAULT_PERSONA_MAX_TOKENS
    )
    if persona_max is None:
        raise ProfileHold(f"{ENV_KEY_PERSONA_MAX_TOKENS} muss positiv und endlich sein")

    updates = {
        ENV_KEY_PROVIDER: PROVIDER_LOCAL,
        ENV_KEY_BASE_URL: base_url.strip(),
        ENV_KEY_MODEL: model.strip(),
        ENV_KEY_API_KEY: api_key,
        ENV_KEY_GM_MAX_TOKENS: str(gm_max),
        ENV_KEY_PERSONA_MAX_TOKENS: str(persona_max),
    }
    if owui_base_url:
        if not is_valid_local_url(owui_base_url):
            raise ProfileHold(f"{ENV_KEY_OWUI_BASE_URL} ist ungueltig")
        updates[ENV_KEY_OWUI_BASE_URL] = owui_base_url.strip()
    return updates


def cloud_provider_updates() -> dict:
    """Bewusster Rueckwechsel auf cloud: Provider explizit setzen. Die
    ZEITRISS_LOCAL_*-Felder bleiben in der Datei stehen (kein Datenverlust
    bei einem spaeteren erneuten Wechsel zurueck zu local), aber
    `resolve_provider` liefert danach 'cloud' und `factories.py` darf das
    lokale Profil nicht mehr verwenden."""
    return {ENV_KEY_PROVIDER: PROVIDER_CLOUD}
