# 07-hacking-tokio-sonnet
- **Model:** zeitriss-v426-uncut-sonnet
- **Cost:** $0.034641
- **Tokens:** in:5717 out:1166

## Output

`EP 1 · MS 1 · SC 4/12 · PHASE Intel · MODE CORE · COMMS OK · Lvl 5 ▓▓▓▓▓▓░░░░ 1.240/2.000 XP · Px 0/5 · Stress 2/10 · Obj: Mainframe-Zugang Sicherheitsstufe Rot · Exfil T-04:30`

---

Das Serverraumklima ist arktisch. Kondensstreifen an den Rack-Gehäusen. Neonblau flackert über Zeros Gesicht, während die Finger bereits auf der Tastatur des fest installierten Wartungsterminals liegen — kein eigener Laptop, zu heiß, zu viel RF-Signatur. Das hier ist Hausgerät. Feindliches Terrain.

Das Terminal zeigt drei Authentifizierungsschichten. Die äußerste ist Standard-AES — Zero hat sie in neunzehn Sekunden geknackt, Fingergelenke schnappen rhythmisch, der Handscanner am Handgelenk liest die lokale Netzwerktopologie. Schicht zwei: proprietäres Keiretsu-Protokoll. Hier hört die Routine auf.

Zero zieht das Kabel aus dem Handscanner, steckt es direkt in den Diagnoseport des Terminals. Hardware-Bridge. Der Scanner läuft jetzt als Proxy — die Anfrage kommt nicht von Zero, sie kommt scheinbar vom Rack selbst.

---

**Probe: SYS-Hack (Sicherheitsstufe Rot)**
Schwierigkeitsgrad: **12** — verschlüsselt, aktives Intrusion-Detection-System, Zeitdruck.

`W10 (ab SYS 5 → W10): [7] + ⌊INT 6 / 2⌋ 3 + Talent Systemeinbruch 2 + Gear Handscanner 1 = 13 vs SG 12 → TREFFER`

---

Schicht zwei fällt. Der Scanner-Proxy hält die Verbindung stabil. Dann: Schicht drei. Biometrische Token-Anfrage — das System will einen registrierten Mitarbeiter-Handabdruck. Zero hat keinen. Aber der Handscanner hat in den letzten vier Minuten die Wärmeresiduen des letzten Technikers auf der Tastatur gelesen. Unvollständig. Riskant.

`Kodex: Handscanner — Wärmeabdruck-Sample 61% Übereinstimmung. Schwellenwert: 70%. Margin of error: kritisch.`

Das Raumklima arbeitet gegen Zero. Jede Sekunde kühlt das Residuum weiter ab. Die Uhr läuft.

---

**Intel / Risiken / Zeitfenster**
- Wache: **T-01:12** bis zur nächsten Patrouille durch Serverraum B
- Biometrischer Abgleich: 61% — System akzeptiert ab 70%; zweiter Versuch löst Silent Alarm aus
- IDS aktiv: Jede weitere manuelle Anfrage erhöht Noise +1
- Handscanner: Akku 40%, Kabel-Bridge belegt den einzigen Diagnoseport

---

Die drei Optionen. Die Uhr tickt hörbar im HUD.

**1 — Temperatur manipulieren:** Rack-Kühlung am nächsten Panel kurz drosseln. Wärme im Raum steigt, Residuum reaktiviert sich leicht — Abgleich könnte auf 72–75% klettern. Kostet Zeit. Noise +1.

**2 — Mitarbeiter-Token faken:** Zero greift auf die im Handscanner gespeicherte Netzwerktopologie zurück — ein Service-Account ohne Biometrie, niedrigere Rechte, aber Zugang zu Teilbereichen von Rot. Schnell. Aber nur 80% des Ziels erreichbar.

**3 — Warten und Techniker holen:** Patrouille kommt in 72 Sekunden. Einer der Techniker läuft diese Route. Abfangen, Social Engineering oder Härte — Zugang mit echtem Abdruck. Hohes Risiko, voller Zugang.

**Freie Aktion** — Du hast das Terminal, den Scanner, das Kabel und 72 Sekunden. Was tust du?
