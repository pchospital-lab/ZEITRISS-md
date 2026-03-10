# Fahrplan – Durchlauf 186 (Hard-Final-Review Watchguard-Neuanlage-Playbook)

## Kontext

Der Loader-/Label-Standard ist technisch gut abgesichert, aber die Neuanlage von
Watchguards hatte bisher kein kompaktes, verbindliches Playbook. Dadurch bleibt
Onboarding für neue Guards unnötig manuell.

## Ziel

- Einheitliches Neuanlage-Playbook für `test_*watchguard.js` bereitstellen.
- Ein Starttemplate im Repo verankern, das den Loader-Standard bereits korrekt
  vorgibt.
- QA-/Prozessspur auf Durchlauf-186-Stand fortführen.

## Arbeitspakete

1. Neues Template `tools/templates/watchguard.template.js` anlegen
   (Loader/`scopeLabel`/`...-ok`-Muster).
2. Neue Checkliste `internal/qa/process/watchguard-neuanlage-checkliste.md`
   ergänzen.
3. Prozessseiten (`known-issues.md`, `hard-final-review-next-steps.md`) auf
   Durchlauf 186 synchronisieren.
4. Pflicht-Smoke ausführen (`bash scripts/smoke.sh`).

## Abnahme

- Template ist im Repo verfügbar und direkt nutzbar.
- Checkliste dokumentiert verbindliche Mindestschritte.
- Prozessseiten verweisen auf den neuen 186er Stand.
- `bash scripts/smoke.sh` läuft vollständig grün.
