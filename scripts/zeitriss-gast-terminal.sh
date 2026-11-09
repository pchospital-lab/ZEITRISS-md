#!/usr/bin/env sh
# ZEITRISS -- duenne lokale Gast-Anschlusshilfe (lokale Vollendung vor LAN).
#
# Zweck (N1, ZR-VOLLENDUNG-OHNE-LAN-NACHZUG-20261106-R2): EIN zusammengehoeriges
# Terminal pro Gast. Die Hilfe verbindet NUR die beiden FIFO-Kanaele, die der
# Betreiber ohnehin schon via `--guest-terminal GAST_ID:IN_FIFO:OUT_FIFO`
# angelegt hat: sie zeigt die Betreiberprozess-Ausgabe (inkl. der jetzt
# sichtbar gespiegelten Fragen/Bestaetigungen) UND sendet die getippten
# Zeilen des Gastes zurueck. Dadurch sieht der Gast seine Beitritts-/
# Zustimmungs-/Import-/Menuefrage VOR seiner Antwort in demselben Fenster.
#
# Was diese Hilfe NICHT ist (bewusste Grenze): kein eigener Host-/Modellstack,
# keine zweite Speicher-/Berechtigungswelt, kein LAN, kein Reconnect-/Parallel-
# Komfort. Sie startet keinen `scripts/mmo_sim.py` und ruft kein Modell. Alle
# Spiel-/Admissions-/Save-Logik bleibt im einen Betreiberprozess. Faellt die
# Hilfe weg, bleibt das rohe Pipe-Plumbing (`cat OUT &` / `cat > IN`) als
# gleichwertiger Fallback moeglich.
#
# Aufruf:
#   scripts/zeitriss-gast-terminal.sh --id GAST_ID --in IN_FIFO --out OUT_FIFO
#   scripts/zeitriss-gast-terminal.sh GAST_ID IN_FIFO OUT_FIFO
#
# Ende: Strg-D (EOF) oder Strg-C beendet NUR dieses Gastfenster sauber. Der
# Betreiber beendet den ganzen Tisch im Hauptmenue mit `beenden`.
set -eu

PROG="$(basename "$0")"

usage() {
    cat >&2 <<EOF
$PROG -- duenne lokale ZEITRISS-Gast-Anschlusshilfe (verbindet nur vorhandene FIFOs)

  $PROG --id GAST_ID --in IN_FIFO --out OUT_FIFO
  $PROG GAST_ID IN_FIFO OUT_FIFO

IN_FIFO/OUT_FIFO sind genau die Pfade, die der Betreiber bei
--guest-terminal GAST_ID:IN_FIFO:OUT_FIFO angegeben hat.
EOF
    exit 2
}

GUEST_ID=""
IN_FIFO=""
OUT_FIFO=""

# Flags ODER drei Positionsargumente -- ehrlicher Abbruch bei falscher Form.
if [ "$#" -eq 3 ] && [ "${1#-}" = "$1" ]; then
    GUEST_ID="$1"; IN_FIFO="$2"; OUT_FIFO="$3"
else
    while [ "$#" -gt 0 ]; do
        case "$1" in
            --id)  GUEST_ID="${2:-}"; shift 2 || usage ;;
            --in)  IN_FIFO="${2:-}";  shift 2 || usage ;;
            --out) OUT_FIFO="${2:-}"; shift 2 || usage ;;
            -h|--help) usage ;;
            *) printf '%s: unbekanntes Argument: %s\n' "$PROG" "$1" >&2; usage ;;
        esac
    done
fi

[ -n "$GUEST_ID" ] && [ -n "$IN_FIFO" ] && [ -n "$OUT_FIFO" ] || usage

for f in "$IN_FIFO" "$OUT_FIFO"; do
    if [ ! -p "$f" ]; then
        printf '%s: %s ist keine benannte Pipe (FIFO). Hat der Betreiber den Prozess schon mit --guest-terminal gestartet?\n' "$PROG" "$f" >&2
        exit 1
    fi
done

# Kopf: Identitaet, Modus, Figur-Hinweis, Hilfe, naechster Schritt, Ende.
# Bewusst statisch/ehrlich -- die Hilfe kennt den Live-Spielzustand nicht,
# sie bridget nur die Kanaele. Der echte Figur-/Menuestatus kommt als
# Prozessausgabe unten im selben Fenster an.
cat <<EOF
================ ZEITRISS -- lokaler Gast-Anschluss ================
 Teilnehmer : $GUEST_ID  (Gast am Betreiber-Tisch, keine eigenen Modellaufrufe)
 Kanaele    : Eingabe  -> $IN_FIFO
              Anzeige  <- $OUT_FIFO   (Fragen/Bestaetigungen erscheinen hier)
 Figur      : vorhandenen Save importieren -> 'charaktere' dann '2'
              noch keine Figur -> 'charaktere' dann '4' (Betreiber aus der
              angezeigten Auswahl waehlen, keine rohe ID noetig)
 Hilfe      : '?' oder '/hilfe' zeigt die Steuerzeilen (verbraucht keinen Zug)
              '/stand' zeigt deinen eigenen Stand
 Naechster  : auf die unten eingeblendete Frage/Empfaengerzeile warten,
   Schritt    dann hier antworten (nichts blind vorab tippen)
 Ende       : Strg-D beendet nur dieses Fenster sauber; der Betreiber
              beendet den ganzen Tisch im Hauptmenue mit 'beenden'
====================================================================
EOF

# Anzeige-Kanal im Hintergrund mitlesen. Beendet sich, wenn der
# Betreiberprozess den out-Kanal schliesst.
cat "$OUT_FIFO" &
DISP_PID=$!

cleanup() {
    kill "$DISP_PID" 2>/dev/null || true
    wait "$DISP_PID" 2>/dev/null || true
    printf '\n[%s] Gastfenster beendet. Der zuletzt GESPEICHERTE persoenliche Stand bleibt erhalten;\n' "$GUEST_ID" >&2
    printf '      ein so beendeter Kanal wird nicht allein durch erneutes Oeffnen wieder lebendig --\n' >&2
    printf '      zuverlaessig ist ein erklaerter Schluss und danach ein vollstaendiger Neustart des Tisches.\n' >&2
}
trap cleanup EXIT INT TERM

# Eingabekanal EINMAL nicht-blockierend oeffnen (O_RDWR-Pipe-Trick, exakt wie
# der Betreiberprozess seinen out-Kanal oeffnet) -- kein Haengen beim Start,
# falls der Betreiber die Leseseite erst spaeter oeffnet. EIN offener Writer
# pro Fenster, bytegleiches Verhalten zu einem gehaltenen `cat > IN_FIFO`.
exec 3<>"$IN_FIFO"

# Getippte Zeilen zeilenweise an den Betreiberprozess weiterreichen.
while IFS= read -r line; do
    printf '%s\n' "$line" >&3
done

# Hierher nur bei EOF (Strg-D) auf der Tastatur -- sauberer, erklaerter Schluss.
exit 0
