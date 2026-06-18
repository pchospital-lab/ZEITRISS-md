#!/usr/bin/env python3
"""G3-Token-Last-Probe: Wie nah kommt eine volle 12-Szenen-5er-Mission an
Sonnets 256k-Kontext? Statt 80 echte Turns zu fahren, injizieren wir ein
kuenstlich langes, REALISTISCH dimensioniertes History-Array und lesen das
echte usage.prompt_tokens von OpenWebUI (inkl. Masterprompt + RAG + History).

Methodik:
- Masterprompt (~26k Tokens laut MEMORY) + KB-RAG kommen serverseitig oben drauf.
- Wir fuellen die messages[]-History mit realistisch grossen SL-Turns
  (Briefings/Szenen ~1.5-4k Zeichen) + Persona-Turns (kurz) + einem 5er-HQ-Save
  (gross). 12 Szenen × (SL-Beat + Persona) + Save-Bloecke an Szenenenden.
- Ausgabe: prompt_tokens pro Stufe, Anteil an 256k, Extrapolation.
"""
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from owui_client import OWUIChat  # noqa: E402

BASE_URL = os.environ.get("OPENWEBUI_URL", "http://127.0.0.1:8080")
API_KEY = os.environ["OPENWEBUI_API_KEY"]
SL_MODEL = "zeitriss-v426-uncut"
KB_ID = "a56706c9-e427-4c6c-9dcb-0eb7cea095c0"
CONTEXT_LIMIT = 256_000

REPO = Path("/mnt/agent_share/cloud/repos/ZEITRISS-md-git")
ANCHOR = REPO / "internal/qa/fixtures/savegame_v7_5er_hq_highlevel.json"

# Realistisch grosse Bausteine (gemessen an echten Runs: SL-Beats 1.5-4k Zeichen)
SL_BEAT = (
    "Die Szene entfaltet sich: Neon spiegelt sich in nassem Asphalt, das HUD "
    "flackert mit Tarnstatus-Anzeige. " * 40
)  # ~4000 Zeichen
PERSONA_TURN = "Ich pruefe die Umgebung und gehe vorsichtig zum Zielpunkt. Was sehe ich?"
SAVE_BLOCK = None  # wird aus Anker geladen


def build_history(n_scenes: int, save_every: int = 3) -> list[dict]:
    """Baut eine 5er-Missions-History: pro Szene ein SL-Beat + Persona-Turn,
    alle `save_every` Szenen ein voller 5er-Save-Block (gross)."""
    hist: list[dict] = []
    save_json = json.dumps(SAVE_BLOCK, ensure_ascii=False)
    for sc in range(1, n_scenes + 1):
        hist.append({"role": "assistant", "content": f"[Szene {sc}] {SL_BEAT}"})
        hist.append({"role": "user", "content": PERSONA_TURN})
        if sc % save_every == 0:
            hist.append({"role": "assistant",
                         "content": f"Speicherstand Szene {sc}:\n```json\n{save_json}\n```"})
            hist.append({"role": "user", "content": "Spiel laden:\n```json\n" + save_json + "\n```"})
    return hist


def measure(n_scenes: int) -> dict:
    sl = OWUIChat(BASE_URL, API_KEY, SL_MODEL, kb_id=KB_ID, timeout=420)
    sl.history = build_history(n_scenes)
    t0 = time.time()
    res = sl.say("Kurzer Lagecheck: Wo steht die Gruppe gerade? Zwei Saetze.")
    dt = time.time() - t0
    u = res["usage"] or {}
    ptok = u.get("prompt_tokens", 0)
    ctok = u.get("completion_tokens", 0)
    det = u.get("prompt_tokens_details") or {}
    cached = det.get("cached_tokens", 0)
    return {"scenes": n_scenes, "msgs": len(sl.history), "prompt_tokens": ptok,
            "completion_tokens": ctok, "cached": cached,
            "pct_256k": round(ptok / CONTEXT_LIMIT * 100, 1), "latency_s": round(dt, 1),
            "rag": len(res["sources"])}


def main():
    global SAVE_BLOCK
    SAVE_BLOCK = json.loads(ANCHOR.read_text(encoding="utf-8"))
    print(f"Anker: {ANCHOR.name} ({len(json.dumps(SAVE_BLOCK))} chars/Save-Block)")
    print(f"Sonnet-Kontext: {CONTEXT_LIMIT:,} Tokens\n")
    results = []
    for n in (4, 8, 12):
        r = measure(n)
        results.append(r)
        print(f"  {n:2d} Szenen | {r['msgs']:3d} msgs | "
              f"prompt={r['prompt_tokens']:>7,} ({r['pct_256k']:>4}% von 256k) | "
              f"cached={r['cached']:>7,} | {r['latency_s']}s | RAG={r['rag']}")
    # Extrapolation auf Worst-Case (langer History, kein Save-Reset)
    if len(results) >= 2:
        a, b = results[-2], results[-1]
        per_scene = (b["prompt_tokens"] - a["prompt_tokens"]) / (b["scenes"] - a["scenes"])
        print(f"\n  ~{per_scene:,.0f} prompt-Tokens pro zusaetzlicher Szene")
        headroom = (CONTEXT_LIMIT - b["prompt_tokens"]) / per_scene if per_scene > 0 else 0
        print(f"  Headroom ab 12 Szenen: ~{headroom:,.0f} weitere Szenen bis 256k")
    out = Path(__file__).resolve().parent.parent / "runs" / f"g3-token-probe-{time.strftime('%Y%m%d-%H%M')}.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\n  -> {out}")


if __name__ == "__main__":
    main()
