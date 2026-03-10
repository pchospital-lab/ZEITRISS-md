# Fahrplan – Durchlauf 168 (Hard-Final-Review Chronopolis Runtime-Entdevifizierung)

## Kontext

Nach Durchlauf 166/167 war der Chronopolis-Block bereits von offensichtlichem
API-/Stub-Ballast bereinigt. Im Runtime-Modul stand jedoch weiterhin ein großer
Static-Blueprint mit technischen Vermessungs- und Spawn-Details, der als
Dev-Maintainer-Material besser außerhalb des geladenen Wissensspeichers liegt.

## Ziel

- Chronopolis im Runtime-Kanon auf spielleitungsrelevante Leitplanken,
  Regie-Output und Inworld-Stadtbild-Pattern fokussieren.
- Technische Blueprint-Details explizit auf die Maintainer-Doku verweisen, statt
  sie im Runtime-Modul auszuspielen.
- QA-Anschlussfähigkeit über Plan/Log/Prozessseiten für den nächsten Durchlauf
  sichern.

## Arbeitspakete

1. `gameplay/kampagnenstruktur.md` im Chronopolis-Abschnitt entdevifizieren
   (Runtime-Fokus, kein Implementations-/Blueprint-Ballast).
2. Den Abschnitt durch kompaktes Runtime-Stadtbild-Pattern ersetzen und auf
   `docs/dev/chronopolis-map-blueprint.md` verweisen.
3. Pflicht-Smoke (`bash scripts/smoke.sh`) ausführen und Ergebnis loggen.
4. `known-issues.md` und Anschlussübersicht auf Durchlauf-168-Stand nachziehen.

## Abnahme

- `bash scripts/smoke.sh` vollständig grün.
- `gameplay/kampagnenstruktur.md` enthält im Chronopolis-Block nur
  runtime-relevante Leitplanken/Regie-Inhalte; technische Detailblueprints sind
  klar als Maintainer-Doku außerhalb des Runtime-Wissensspeichers markiert.
