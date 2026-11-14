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

_CONTROL_CHARS = ("\r", "\n", "\x00")
_URL_RE = re.compile(r"^(https?)://([^/@\s?#]+)(/.*)?$")


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


def _has_control_chars(s: str) -> bool:
    return any(c in s for c in _CONTROL_CHARS)


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


def resolve_provider(env: dict) -> str:
    """Gibt 'cloud' | 'local' | 'legacy' | 'hold' zurueck.

    'legacy' = ZEITRISS_MODEL_PROVIDER fehlt komplett (Schluessel nicht im
    dict) -> bisheriges Cloud-/CLI-/API-Verhalten unveraendert. 'hold' =
    Schluessel vorhanden, aber Wert ausdruecklich leer/unbekannt/inkonsistent
    -- MUSS sichtbar halten, niemals raten/auf 'legacy' zurueckfallen.
    N1-03: ein fehlendes Feld (Datei/Env erwaehnt den Schluessel nie) und ein
    ausdruecklich leeres Feld (`ZEITRISS_MODEL_PROVIDER=`) sind NICHT
    derselbe Zustand -- nur das echte Fehlen des Schluessels ist 'legacy'."""
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


def resolve_local_profile(env: dict) -> LocalModelProfile:
    """Validiert alle ZEITRISS_LOCAL_*-Felder aus einem bereits gelesenen
    env-dict (z.B. `_read_env_file(Path.home() / ".openwebui_env")`).
    Wirft `ProfileHold` mit konkretem Grund statt stillem Fallback/Erbe
    von Cloud-Werten (64000/reasoning/Vision/variant_base_model etc. werden
    hier bewusst NICHT gelesen)."""
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
