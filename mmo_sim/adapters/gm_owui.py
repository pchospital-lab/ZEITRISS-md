#!/usr/bin/env python3
"""
mmo_sim/adapters/gm_owui.py — `openwebui_sl`-GM-Transport (echter
Produktionspfad, nutzt `agent_mp/sl_client.SLSession`, PLAN.md §2).

`agent_mp/sl_client.py` (OWUI-SL-Transport, echte HTTP-Anfragen ueber
`owui_client.OWUIChat`) bleibt an seinem P1-Ort — es ist bereits ein echter,
funktionierender Produktionspfad, keine Extraktion noetig. Dieser Adapter
importiert ihn ueber einen EXPLIZIT uebergebenen Pfad (`sl_client_path`,
Konstruktor-Pflichtparameter) statt einer `__file__`-relativen Vermutung
(Konsistenz mit der A2-Lehre: kein impliziter Pfad in neuem Code).

P2-Fertigstellung (I6, PLAN-CRITIC.md A7): Resume-Kriterium EXPLIZIT --
liegt unter `run_dir` bereits eine lokale `sl_history.jsonl` (persistierter
Verlauf eines fruehereren `SLSession.turn()`-Aufrufs fuer GENAU dieses
`run_dir`), wird der unterbrochene Abschnitt ueber `SLSession.from_history()`
fortgesetzt (gleicher Chat, gleiche Historie). Fehlt die Datei (echter neuer
Abschnitt), wird weiterhin `new_sl_session()` (neuer Chat) verwendet -- nicht
am Abschnitts-/Order-Zustand vorbei entschieden."""
from __future__ import annotations

import importlib.util
import math
import re
import sys
from pathlib import Path

from .base import GMTransport, ProviderQuotaPausedError

# FIX5 (GM-Seite, net-new -- dieser Adapter hatte zuvor KEINE Quota-/
# Ratelimit-Behandlung): derselbe getypte Pausen-Zustand wie beim Persona-
# Adapter (s. adapters.base.ProviderQuotaPausedError), aber an der fuer den
# HTTP-Transport passenden Struktur erkannt -- dem von
# `agent_mp/sl_client.py`/`owui_client.OWUIChat._post` IMMER deterministisch
# als `f"HTTP {code}: {body}"` formatierten Fehlertext (der numerische
# Statuscode ist hier das strukturierte Feld, keine freie Wortsuche) ODER
# dem literalen, provider-standardisierten Fehlertyp-Token
# `insufficient_quota` (OpenAI-/OpenRouter-Fehlerschema) im Response-Body.
# Jeder andere Transportfehler (401/403/404/Netzwerk/unerwartete Struktur)
# bleibt unveraendert ein gewoehnlicher, durchgereichter Fehler.
_GM_QUOTA_HTTP_CODES = frozenset({402, 429})
_GM_QUOTA_HTTP_CODE_RE = re.compile(r"^HTTP (\d+):")
_GM_QUOTA_BODY_MARKERS = ("insufficient_quota",)
# P4 (R4-Rundenabschluss): 429 ALLEIN ist ein reines Ratenlimit (zu viele
# Anfragen in kurzer Zeit), KEIN Guthaben-/Kontingentproblem -- anders als
# 402 ODER ein 429 MIT dem Guthaben-/Limit-Marker `insufficient_quota` im
# Body. Stoppen bleibt in BEIDEN Faellen konservativ (`ProviderQuotaPausedError`
# unveraendert), nur der Spielermeldungstext unterscheidet sich (s.
# `adapters.base.quota_pause_player_message`).
_GM_RATE_LIMIT_ONLY_HTTP_CODE = 429


def _gm_quota_pause_detail(exc: Exception) -> tuple[str, bool] | None:
    """Liefert `(detail, is_rate_limit_only)` -- `detail` eine (auf 300
    Zeichen begrenzte, secret-freie) Detailzeile, wenn `exc` eine
    Kontingent-/Ratelimit-Antwort des GM-Transports traegt, sonst `None`.
    `is_rate_limit_only=True` NUR bei HTTP 429 OHNE den Guthaben-/Limit-
    Marker `insufficient_quota` im Body (reines Ratenlimit) -- 402 ODER
    ein 429 MIT diesem Marker bleibt `False` (Guthaben-/Kontingentpause)."""
    text = str(exc)
    has_quota_body_marker = any(marker in text for marker in _GM_QUOTA_BODY_MARKERS)
    m = _GM_QUOTA_HTTP_CODE_RE.match(text)
    if m and int(m.group(1)) in _GM_QUOTA_HTTP_CODES:
        is_rate_limit_only = int(m.group(1)) == _GM_RATE_LIMIT_ONLY_HTTP_CODE and not has_quota_body_marker
        return text[:300], is_rate_limit_only
    if has_quota_body_marker:
        return text[:300], False
    return None


def _validate_gm_output_limit_tokens(value: object) -> int | None:
    """B2 (MAIN-KORREKTUR I2-Nacharbeit 2026-09-24, REVIEW-I2.md §4
    0-Edge): EINZIGE Validierungsstelle fuer die GM-Ausgabegrenze -- JEDER
    Aufrufer (echte CLI-Konfiguration `scripts/mmo_sim.py` UND direkte
    Testkonstruktion) geht durch `GmOwuiTransport.__init__`. Nur eine ECHTE
    positive, endliche Ganzzahl gilt als bekannte, durchsetzbare Grenze --
    `0`, negative Werte, `bool` (technisch eine `int`-Unterklasse), nicht
    endliche Werte (`inf`/`nan`) und Bruchwerte werden NICHT stillschweigend
    als 'unbegrenzt' (`None`) behandelt, sondern fail-closed abgelehnt
    (`ValueError`) -- eine erkennbare Fehlkonfiguration darf weder lautlos
    eine budgetierte Anfrage durchwinken NOCH (der 0-Randfall) als bekannt
    gelten und dann am HTTP-Body wieder verschwinden (`runtime.py` liest
    `output_bound_known` ausschliesslich ueber `is not None` an diesem
    bereits validierten Attribut -- nach dieser Validierung ist `0` dort
    strukturell nicht mehr erreichbar). Ein gueltiger Wert wird auf `int`
    normalisiert (derselbe wirksame Wert erreicht so `output_bound_known`,
    Reservierung, Requestdatensatz UND `max_tokens` im OWUI-Body als
    echten JSON-`int`, kein `50.0`). `None` (nicht konfiguriert, Legacy-P1)
    bleibt unveraendert `None`."""
    if value is None:
        return None
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value <= 0
        or value != int(value)
    ):
        raise ValueError(
            f"gm_output_limit_tokens={value!r} ist keine positive endliche Ganzzahl -- "
            f"0/negativ/bool/nicht-endlich/Bruch sind keine durchsetzbare GM-Ausgabegrenze "
            f"(B2 fail-closed, MAIN-KORREKTUR I2-Nacharbeit 2026-09-24)."
        )
    return int(value)


def _load_sl_client_module(sl_client_path: Path):
    """Laedt `agent_mp/sl_client.py` per Dateipfad (kein Paket-Import noetig).
    `sl_client.py` selbst importiert `owui_client` per `sys.path.insert(0,
    str(Path(__file__).resolve().parent.parent))` — das bleibt gueltig, weil
    diese Datei sich NICHT bewegt."""
    spec = importlib.util.spec_from_file_location("agent_mp_sl_client", sl_client_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"gm_owui: konnte sl_client nicht laden von {sl_client_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("agent_mp_sl_client", module)
    spec.loader.exec_module(module)
    return module


def _safe_component(value: str) -> str:
    return value.replace("/", "_").replace("\\", "_")


class GmOwuiTransport:
    """`GMTransport`-Implementierung: delegiert 1:1 an eine echte
    `SLSession`-Instanz (Contract bereits identisch zu `SLStub.turn()`, s. P1
    `sl_stub.py`-Docstring — keine erneute Vertragsanpassung noetig).

    A6/D3 (WEGKARTE §8, Plan-Critic A6, Test 10): `table_id` bindet die
    Historie an EIN eindeutiges Unterverzeichnis von `run_dir`
    (`run_dir/gm_sessions/<table_id>/sl_history.jsonl`) -- "Unterverzeichnisse
    desselben Stores OK" (Vertrag 04 §3), kein neuer Backend-Store. Ohne
    `table_id` (Default `None`, z.B. bestehende Unit-Tests, die den Adapter
    direkt gegen ein eigenes `run_dir` konstruieren) bleibt das alte
    Verhalten erhalten -- `run_dir` selbst traegt dann bereits die
    Tisch-Identitaet des Aufrufers."""

    def __init__(self, sl_client_path: str | Path, run_dir: str | Path,
                 table_id: str | None = None,
                 sl_model: str | None = None, kb_id: str | None = None,
                 gm_output_limit_tokens: float | None = None,
                 transport_max_retries: int | None = None,
                 transport_backoff: float | None = None,
                 transport_timeout: int | None = None):
        # B2 (MAIN-KORREKTUR I2-Nacharbeit 2026-09-24): Wertegueltigkeit VOR
        # jedem Seiteneffekt (Modulladen/Session-Aufbau/Verzeichnisanlage)
        # pruefen -- eine erkennbare Fehlkonfiguration bricht sofort ab, statt
        # zuerst eine (potenziell live gebundene) SL-Session aufzubauen.
        validated_output_limit_tokens = _validate_gm_output_limit_tokens(gm_output_limit_tokens)
        module = _load_sl_client_module(Path(sl_client_path))
        run_dir = Path(run_dir)
        effective_dir = run_dir / "gm_sessions" / _safe_component(table_id) if table_id else run_dir
        effective_dir.mkdir(parents=True, exist_ok=True)
        history_path = effective_dir / "sl_history.jsonl"
        # W51 (01_RESTAUFTRAG.md §3, 03_LIVE3_FUENFER_UND_LAUFZEIT.md
        # "hoechstens EIN Transportversuch je Liveaktion"; SCOPE.json
        # semantic_constraints.adapters "per-run timeout/retry threading"):
        # `transport_max_retries`/`transport_backoff` sind additiv und
        # OPTIONAL (Default `None`) -- ohne Angabe bleibt JEDER bestehende
        # Aufrufer (`adapters.factories.default_gm_transport_factory`, jeder
        # bestehende Test) unveraendert beim P1-Default des Harness-Clients
        # (3 Versuche mit Backoff). Fuer einen LIVE3-Lauf uebergibt der
        # Aufrufer explizit `transport_max_retries=1` -- EIN physischer POST
        # pro `.turn()`, kein automatischer, vom Client selbst ausgeloester
        # Zweitversand bei unklarem Ausgang (s. `operator/`-Skripte).
        # `timeout` traegt denselben additiv/optionalen Charakter wie
        # `max_retries`/`backoff` (s.o.) -- ohne Angabe bleibt `SLSession`s
        # eigener Default (`TIMEOUT_SL=420`) unveraendert; ein Offline-
        # Beleg (s. `operator/resume_proof.py`) kann hierueber ein kurzes,
        # deterministisches Fenster erzwingen, ohne den echten LIVE3-Default
        # zu beruehren.
        timeout_kwargs: dict = {}
        if transport_timeout is not None:
            timeout_kwargs["timeout"] = transport_timeout
        if history_path.exists():
            # I6/A7: unterbrochener Abschnitt -- lokale Verlaufsdatei im
            # effective_dir vorhanden -> denselben Chat samt Historie
            # fortsetzen (GENAU dieses Tisches, kein fremder Verlauf).
            self._session = module.SLSession.from_history(
                effective_dir, sl_model=sl_model, kb_id=kb_id,
                max_retries=transport_max_retries, backoff=transport_backoff,
                **timeout_kwargs,
            )
        else:
            # Echter neuer Abschnitt -- keine Verlaufsdatei -> neuer Chat.
            self._session = module.new_sl_session(
                effective_dir, sl_model=sl_model, kb_id=kb_id,
                max_retries=transport_max_retries, backoff=transport_backoff,
                **timeout_kwargs,
            )
        # E1 (Auflage 1, MAIN-ENTSCHEIDUNG I2-Nachzug GM-Weg): optionale, vom
        # Aufrufer der `gm_transport_factory` konfigurierte GM-Ausgabegrenze
        # -- analog `sl_model`/`kb_id`, NICHT ueber `lab.status.json`/
        # `LabStatus` (Auflage 2 der Vorrunde bleibt bindend). Ohne Angabe
        # (Default `None`) bleibt jedes P1-Aufrufverhalten unveraendert. B2
        # (MAIN-KORREKTUR I2-Nacharbeit 2026-09-24): bereits oben validiert --
        # `self.output_limit_tokens` ist GARANTIERT entweder `None` oder eine
        # echte positive Ganzzahl, nie `0`/negativ/Bruch (s.
        # `_validate_gm_output_limit_tokens`).
        self.output_limit_tokens = validated_output_limit_tokens

    @property
    def base_url(self) -> str | None:
        """E3 (Auflage 3, MAIN-ENTSCHEIDUNG): duck-typed Routen-Attribut fuer
        Q03 (`core.runtime._route_for`-artiges Muster) -- reicht die
        tatsaechliche OWUI-Zieladresse durch, die sonst zwei Objektebenen
        tief in `self._session.chat.base` versteckt waere."""
        return getattr(getattr(self._session, "chat", None), "base", None)

    def turn(self, turn_idx: int, user_text: str, output_limit_tokens: float | None = None) -> dict:
        try:
            return self._session.turn(turn_idx, user_text, output_limit_tokens=output_limit_tokens)
        except Exception as exc:  # noqa: BLE001 -- typisierte Reklassifikation, s. _gm_quota_pause_detail.
            quota_detail = _gm_quota_pause_detail(exc)
            if quota_detail is not None:
                detail, is_rate_limit_only = quota_detail
                # P4: `rate_limited=True`-Anhang NUR beim reinen 429-
                # Ratenlimit (s. `adapters.base.quota_pause_is_rate_limited`/
                # `quota_pause_player_message`) -- weggelassen (Default
                # `False`) bei 402/Guthaben, identisch zum bestehenden
                # `reset_hint=...`-Anhangmuster.
                rate_limit_suffix = ", rate_limited=True" if is_rate_limit_only else ""
                raise ProviderQuotaPausedError(
                    f"gm_owui: Kontingent-/Budgetpause erkannt: {detail}{rate_limit_suffix}"
                ) from exc
            raise

    def usage_summary(self) -> dict:
        return self._session.usage_summary()
