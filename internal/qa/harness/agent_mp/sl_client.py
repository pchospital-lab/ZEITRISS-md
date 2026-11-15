#!/usr/bin/env python3
"""
agent_mp/sl_client.py — schlanker OWUI-SL-Client für den 'Leader schreibt'-Harness.

Wiederverwendet owui_client.OWUIChat (Browser-Pfad, local:-Temp-Chat, OWUI-
eigenes RAG) 1:1 — dieser Client fügt nur das Datei-Persistieren des SL-Chats
(sl_history.md + sl_history.jsonl) hinzu, wie es die datei-vermittelte
Architektur B (siehe DESIGN.md) braucht. KEINE eigene Save-Detection/Quality-
Logik hier — die lebt weiterhin in solo_journey.py/coreops_split_merge.py und
wird von Altair direkt auf den zurückgegebenen SL-Text angewendet, damit sie
nicht dupliziert wird.

Env: OPENWEBUI_URL, OPENWEBUI_API_KEY (wie bestehender Harness).
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from owui_client import OWUIChat  # noqa: E402

# ─── Config (verifiziert gegen solo_journey.py, 2026-09-15 die aktuellste Quelle) ──
BASE_URL = os.environ.get("OPENWEBUI_URL", "http://127.0.0.1:8080")
API_KEY = os.environ.get("OPENWEBUI_API_KEY", "")
SL_MODEL = "zeitriss-v426-uncut"
# Live-KB verifiziert 2026-09-15 in solo_journey.py. Ältere Skripte
# (group-harness.py: a56706c9, coreops-harness.py: bb266c62) referenzieren
# historische/tote Collections — NICHT verwenden.
KB_ID = "9ad88aff-f881-4920-9fca-75094294ead8"
TIMEOUT_SL = 420
PRICE_IN, PRICE_OUT = 3.0, 15.0  # Sonnet-4.6 USD/1M, nur Anzeige


def _redact_secret_text(text: str, *secrets: str | None) -> str:
    """A5 (02_NACHARBEIT.md Gruppe A5, O1-D): GM-Fehlerecho-Grenze an
    `SLSession.turn` -- `owui_client.OWUIChat` (read-only/frozen an dieser
    Grenze) kann im Fehlerfall den rohen Serverbody (bis 400 Zeichen) oder
    eine formfalsche Response 1:1 in die Exceptionmeldung uebernehmen; ein
    (ggf. absichtlich fehlerhaft antwortendes) Double kann darin den
    konfigurierten OWUI-Key echoen. Entfernt bekannte Secretwerte, BEVOR
    die Meldung weitergereicht wird -- Fehlertyp (Exceptionklasse),
    HTTP-Status/Kategorietext (401/403/429/...) und Timeout-Erkennung
    bleiben UNVERAENDERT erhalten, nur der Geheimnisanteil wird ersetzt."""
    redacted = text
    for secret in secrets:
        if secret:
            redacted = redacted.replace(secret, "[REDACTED]")
    return re.sub(r"Bearer\s+\S+", "Bearer [REDACTED]", redacted)


class SLSession:
    """Ein SL-Turn-Zyklus mit Datei-Persistenz für die datei-vermittelte Architektur B.

    Hält EINEN OWUIChat (= EIN geteilter SL-Chat für den ganzen Run) und
    schreibt jeden Turn in sl_history.md (lesbar) + sl_history.jsonl
    (maschinenlesbar), so wie DESIGN.md §3 es vorsieht.
    """

    def __init__(self, run_dir: Path, sl_model: str | None = None,
                 kb_id: str | None = None, timeout: int = TIMEOUT_SL,
                 max_retries: int | None = None, backoff: float | None = None,
                 dollar_billed: bool = True):
        if not API_KEY:
            raise RuntimeError(
                "OPENWEBUI_API_KEY fehlt — erst: set -a; . ~/.openwebui_env; set +a")
        # ZR-LOCAL-TOKENHOST-L1: additiv/optional (Default True = bisheriges
        # Sonnet-Preisverhalten unveraendert). False (lokaler Tokenhost)
        # haelt die echte Tokenusage, setzt aber keinen Sonnet-USD-Preis an
        # -- kein globaler Cloudtarif-Wechsel, nur diese EINE Instanz.
        self.dollar_billed = bool(dollar_billed)
        self.run_dir = Path(run_dir)
        self.md_path = self.run_dir / "sl_history.md"
        self.jsonl_path = self.run_dir / "sl_history.jsonl"
        # W51 (01_RESTAUFTRAG.md §3, 03_LIVE3_FUENFER_UND_LAUFZEIT.md
        # "hoechstens EIN Transportversuch je Liveaktion ... keine
        # zusaetzlichen HTTP-Retries bei unklarem Ausgang"): `max_retries`/
        # `backoff` sind additiv und OPTIONAL (Default `None`) -- nur
        # explizit uebergeben (per-Run-Threading, SCOPE.json
        # semantic_constraints.adapters), sonst behaelt `OWUIChat` SEINEN
        # eigenen Default (3 Versuche mit Backoff, P1-Verhalten fuer jeden
        # bestehenden Aufrufer dieses Harness-Clients UNVERAENDERT). Fuer
        # LIVE3 konstruiert `mmo_sim/adapters/gm_owui.py` mit `max_retries=1`
        # -- EIN physischer POST pro `.turn()`-Aufruf, kein automatischer
        # Zweitversand bei einer bereits serverseitig moeglicherweise
        # ausgefuehrten, nur clientseitig unklar beantworteten Anfrage.
        owui_kwargs: dict = {}
        if max_retries is not None:
            owui_kwargs["max_retries"] = max_retries
        if backoff is not None:
            owui_kwargs["backoff"] = backoff
        self.chat = OWUIChat(
            BASE_URL, API_KEY, sl_model or SL_MODEL,
            kb_id=kb_id or KB_ID, timeout=timeout, **owui_kwargs,
        )
        # ZR-LOCAL-TOKENHOST-N1-04: `dollar_billed=False` (lokaler Tokenhost)
        # hat KEINEN Providerpreis -- `None`/JSON-null ("UNKNOWN") statt
        # einer erfundenen `0.0`-Gesamtkostenbehauptung. Cloud (`True`)
        # bleibt unveraendert ein echter Float-Akkumulator.
        self.cum_cost = 0.0 if self.dollar_billed else None
        if not self.md_path.exists():
            self.md_path.write_text(
                f"# SL-Chat-Verlauf\n\nchat_id: `{self.chat.chat_id}`  \n"
                f"model: `{self.chat.model}`  \nkb_id: `{self.chat.kb_id}`\n\n---\n",
                encoding="utf-8",
            )

    def turn(self, turn_idx: int, user_text: str, output_limit_tokens: float | None = None) -> dict:
        """Schickt user_text an die SL, persistiert Turn, gibt Ergebnis zurück.

        Rückgabe-Vertrag identisch zu OWUIChat.say(): {content, usage,
        sources, latency_s, chat_id} — Save-Detection/Quality-Checks aus dem
        bestehenden Harness lassen sich unverändert darauf anwenden.

        E4 (Auflage 4, MAIN-ENTSCHEIDUNG I2-Nachzug GM-Weg): `output_limit_tokens`
        additiv durchgereicht an `OWUIChat.say()` -- Default `None` sendet
        keinen `max_tokens`-Body-Key (unveraendertes P1-Verhalten).
        """
        try:
            res = self.chat.say(user_text, output_limit_tokens=output_limit_tokens)
        except Exception as exc:
            # A5 (02_NACHARBEIT.md Gruppe A5, O1-D): die bereits erlaubte
            # GM-Fehlerecho-Grenze -- redigiert einen etwaigen Tokenecho in
            # der Fehlermeldung, BEVOR sie weiterpropagiert. `from None`
            # unterdrueckt zusaetzlich die (sonst gerenderte) Exceptionkette
            # auf die urspruengliche, NICHT redigierte Ausnahme -- Typ/
            # Status-/Quota-/Retrytext in der NEUEN Meldung bleiben
            # unveraendert erhalten (reine Textredaktion, keine neue
            # Kategorisierung).
            # R7-Fix (01 §"Materielle Restfehler", 02 Block D): `type(exc)
            # (text)` nimmt einen Ein-Argument-Konstruktor an -- fuer
            # Exceptions mit mehreren Pflichtargumenten (z.B.
            # `json.JSONDecodeError(msg, doc, pos)`, von einem durch den
            # eingefrorenen OWUI-Unterbau bereits gekuerzten/formfalschen
            # Echo ausgeloest) wirft die Rekonstruktion selbst ein
            # `TypeError` und ersetzt die eigentliche, bereits redigierte
            # Fehlermeldung durch eine nichtssagende Konstruktorbeschwerde.
            # Faellt bei einem solchen Konstruktorfehler auf eine
            # vereinbarte sichere Fehlerkategorie (`RuntimeError`) zurueck --
            # HTTP-Status/Quota-/Retrytext bleiben im (redigierten)
            # Nachrichtentext erhalten, nur die exakte Python-Klasse wechselt
            # fuer diesen Randfall. Fuer jeden Ein-Argument-Exceptiontyp
            # (die bisher tatsaechlich auftretenden Faelle) bleibt das
            # Altverhalten bytegleich.
            redacted_text = _redact_secret_text(str(exc), API_KEY)
            try:
                reraised = type(exc)(redacted_text)
            except TypeError:
                reraised = RuntimeError(redacted_text)
            raise reraised from None
        ptok = res["usage"].get("prompt_tokens", 0)
        ctok = res["usage"].get("completion_tokens", 0)
        # ZR-LOCAL-TOKENHOST-N1-04: echte Tokenusage bleibt in JEDEM Fall
        # erhalten (ptok/ctok oben); fuer `dollar_billed=False` ist der
        # monetaere Preis ausdruecklich UNKNOWN (`None`/JSON-null), NICHT
        # `0.0` -- `0.0` wuerde eine tatsaechlich gemessene Nullkosten-
        # Rechnung behaupten, die es fuer einen ungepreisten lokalen
        # Tokenhost nicht gibt.
        cost = (ptok / 1e6 * PRICE_IN + ctok / 1e6 * PRICE_OUT) if self.dollar_billed else None
        if self.dollar_billed:
            self.cum_cost += cost
        sources = self.chat.source_files()

        with self.md_path.open("a", encoding="utf-8") as fh:
            fh.write(f"\n## Turn {turn_idx:02d} — Leader-Post\n\n{user_text}\n")
            fh.write(f"\n## Turn {turn_idx:02d} — SL\n\n{res['content']}\n")
            if sources:
                fh.write(f"\n> _RAG: {', '.join(sources)}_\n")

        record = {
            "turn": turn_idx,
            "leader_post": user_text,
            "sl_content": res["content"],
            "prompt_tokens": ptok,
            "completion_tokens": ctok,
            "cost_usd": round(cost, 6) if self.dollar_billed else None,
            "cum_cost_usd": round(self.cum_cost, 6) if self.dollar_billed else None,
            "dollar_billed": self.dollar_billed,
            "pricing": "sonnet_usd" if self.dollar_billed else "local_unpriced",
            "rag_sources": sources,
            "latency_s": res["latency_s"],
            "chat_id": res["chat_id"],
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        with self.jsonl_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

        return res

    def usage_summary(self) -> dict:
        return {
            "chat_id": self.chat.chat_id,
            "model": self.chat.model,
            "kb_id": self.chat.kb_id,
            "cum_cost_est_usd": round(self.cum_cost, 6) if self.dollar_billed else None,
            "dollar_billed": self.dollar_billed,
            "pricing": "sonnet_usd" if self.dollar_billed else "local_unpriced",
        }

    @classmethod
    def from_history(cls, run_dir: Path, sl_model: str | None = None,
                     kb_id: str | None = None, timeout: int = TIMEOUT_SL,
                     max_retries: int | None = None, backoff: float | None = None,
                     dollar_billed: bool = True) -> "SLSession":
        """Rekonstruiert eine SLSession aus sl_history.jsonl (M1-Fix).

        Schliesst die in ORCHESTRATION.md §2 selbst benannte Luecke: bei einem
        Mehr-Turn-Run ueber GETRENNTE Python-Aufrufe (Altair ruft sl_client pro
        Turn neu auf) haelt kein Prozess die OWUIChat-Historie im Speicher.
        Diese Factory liest jede JSONL-Zeile, baut die chat.history als
        User/Assistant-Paare wieder auf und uebernimmt die chat_id — VOR dem
        naechsten .turn()-Aufruf. Korrupte Zeilen werden uebersprungen, nicht
        fatal. Ohne diese Funktion muesste jeder Turn die fehleranfaellige
        Handrekonstruktion wiederholen.

        `max_retries`/`backoff`: wie `__init__` additiv/optional durchgereicht
        (W51, s. dortiger Docstring) -- ein fortgesetzter Abschnitt behaelt
        dieselbe Transportkonfiguration wie sein erster Aufruf.

        ZR-LOCAL-TOKENHOST-L1: `dollar_billed` gilt fuer DIESEN Resume genauso
        wie fuer `__init__` (New/Resume gleich behandelt). Alte JSONL-Zeilen
        bleiben unveraendert auf der Platte -- aber ihr `cum_cost_usd` wird
        NUR uebernommen, wenn die fortgesetzte Session wieder `dollar_billed`
        ist. Ein jetzt lokal (`dollar_billed=False`) fortgesetzter Abschnitt
        startet mit `cum_cost=0.0` statt eine alte Cloud-Dollarsumme als
        aktuelle lokale Messung weiterzufuehren (02: "alte Cloudhistory darf
        nicht als lokale aktuelle Rechnung erscheinen")."""
        sess = cls(
            run_dir, sl_model=sl_model, kb_id=kb_id, timeout=timeout,
            max_retries=max_retries, backoff=backoff, dollar_billed=dollar_billed,
        )
        if not sess.jsonl_path.exists():
            return sess
        history: list[dict] = []
        last_chat_id: str | None = None
        last_cum = 0.0
        for line in sess.jsonl_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue  # korrupte Zeile ueberspringen, Run bleibt lauffaehig
            history.append({"role": "user", "content": rec.get("leader_post", "")})
            history.append({"role": "assistant", "content": rec.get("sl_content", "")})
            if rec.get("chat_id"):
                last_chat_id = rec["chat_id"]
            # ZR-LOCAL-TOKENHOST-N1-04/G9-Fix (02_NACHARBEIT.md Gruppe E,
            # O5-D): nur eine NUMERISCHE alte Cloud-Summe ist eine echte
            # Rechnung, die ein jetzt wieder Cloud-fortgesetzter Abschnitt
            # uebernehmen darf. Ein `None`/JSON-null-Eintrag einer frueher
            # lokal (unpriced) protokollierten Zeile ist bereits kein
            # Treffer (`isinstance`-Check). G9: eine AELTERE, VOR diesem Fix
            # geschriebene lokale Zeile konnte `cum_cost_usd` noch als
            # numerische `0.0` statt `null` tragen (`dollar_billed=False`,
            # aber zahlenwertig) -- ohne die zusaetzliche `dollar_billed`-
            # Pruefung wuerde eine SPAETERE echte Cloud-Summe durch diese
            # alte lokale Nullzeile wieder geloescht. `rec.get("dollar_billed",
            # True)` behandelt einen fehlenden Schluessel (Record aelter als
            # dieses Feld -- "die alte Welt kannte nur dollarbepflichtete
            # Rollen", s. request_ledger.py) weiterhin als Cloud/priced.
            if rec.get("dollar_billed", True) and isinstance(rec.get("cum_cost_usd"), (int, float)):
                last_cum = rec["cum_cost_usd"]
        sess.chat.history = history
        if last_chat_id:
            sess.chat.chat_id = last_chat_id
        # ZR-LOCAL-TOKENHOST-N1-04: `dollar_billed=False` startet unbekannt
        # (`None`/JSON-null), NICHT `0.0` -- `0.0` wuerde fuer den jetzt
        # lokal fortgesetzten Abschnitt eine echte Nullkosten-Messung
        # behaupten (02: "alte Cloudhistory darf nicht als lokale aktuelle
        # Rechnung erscheinen", symmetrisch: auch nicht als lokale Nullsumme).
        sess.cum_cost = last_cum if dollar_billed else None
        return sess


def new_sl_session(run_dir: str | Path, sl_model: str | None = None,
                    kb_id: str | None = None, timeout: int = TIMEOUT_SL,
                    max_retries: int | None = None, backoff: float | None = None,
                    dollar_billed: bool = True) -> SLSession:
    """Convenience-Factory, wie new_sl_chat() in solo_journey.py. `timeout`/
    `max_retries`/`backoff`/`dollar_billed` additiv/optional durchgereicht
    (W51/ZR-LOCAL-TOKENHOST-L1, s. `SLSession.__init__`)."""
    return SLSession(
        Path(run_dir), sl_model=sl_model, kb_id=kb_id, timeout=timeout,
        max_retries=max_retries, backoff=backoff, dollar_billed=dollar_billed,
    )


if __name__ == "__main__":
    print(f"agent_mp.sl_client: SL_MODEL={SL_MODEL} KB_ID={KB_ID} "
          f"BASE_URL={BASE_URL} API_KEY_set={bool(API_KEY)}")
