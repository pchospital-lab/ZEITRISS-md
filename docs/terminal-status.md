# Terminalstatus und Prüfstand

Stand dieser Dokumentationsvorlage: 15. Oktober 2026.
Die Vorlage gehört zu einem privaten Integrationskandidaten, nicht zu einer
bereits veröffentlichten neuen Terminalversion.

## Was vorhanden ist

Lokaler Einstieg, Figurenwahl und -erschaffung, Import und Export,
Rundenzusammenstellung, lokale Mehrpersonenführung und Wiederaufnahme sind
implementiert. In der dokumentierten LA1-Live-Erprobung wurden Start,
Menübedienung und die Budgetablehnung geprüft; drei von fünf vorgesehenen
Testfiguren wurden über den Produktweg abgeschlossen. Der gesamte Lauf
bleibt **LIVE_ASSISTED_PARTIAL**, nicht vollständige Endnutzerabnahme.

Die jüngste private Recoverylieferung wurde mit 49 beauftragten
Offlinefällen erneut geprüft. Normale Terminal-Wiederaufnahme über einen
Prozessneustart und die Originalantwortbindung beim Abschnittsabschluss
bestehen in den bezeichneten synthetischen Prüfungen. Die neue
CLI-Kontextkorrektur ist ein separat zu integrierender Kandidat.

Stand 22. Oktober 2026 (R4-Anschluss, neuer Livebeleg): Für einen
**einzelnen** Spieler ist der vollständige Abschnitts-Schluss jetzt live
gegen die gehostete Spielleitung belegt — `!save` im HQ erntet den
Save-Block strukturell in den Store (`__final.json`, Save-Versionszähler
steigt), über einen echten Prozessneustart hinweg und mit wirksamem
Folgezug (zweiter Abschluss). Die Abschluss-Erkennung ist an das
`!save`-Kommando plus den Save-Block gebunden und damit unabhängig von
der jeweiligen Formulierung der Spielleitung. Das ersetzt NICHT die unten
genannte vollständige Mehrfiguren-Live-Abnahme.

## Was für eine vollständige Live-Abnahme noch fehlt

Ein tatsächlich durchgespielter Lauf mit fünf regulär erschaffenen Figuren,
zwei aufeinanderfolgenden Abschnitten, den Endsaves aus A als Startsaves von
B, regulärem Prozessneustart und getrennt belegter Abschlusswiederaufnahme.
Erschaffung ist dabei noch kein Spielabschnitt; fünf Endsaves zählen nicht
zweimal als zehn eigenständige Ergebnisse.

Skriptierte Testantworten, nachträglich eingesetzte Endstände oder ein
sauberer Prozess-Exit allein belegen keine Live-Spielbarkeit. Eine
vollständige Runde umfasst echte Entscheidungen und sichtbare Folgen sowie
nachvollziehbar gespeicherten Fortschritt. Die konkrete Modellroute,
Anfragen- und Kostengrenzen gehören zum jeweiligen Livebeleg.

## Bestehender LA1-Lauf und neue Testkampagne

Im eingefrorenen LA1-Bestand bleibt P3s Originalrequest gesendet mit
unbekanntem Ausgang. Ein additiver Audit löst diese Sperre nicht. P5 bleibt
im dokumentierten HOLD nach einem Korrekturversuch. Die ursprünglichen
Bestände werden weder ersetzt noch als nachträglich bestanden umbenannt.

Ein später ausdrücklich beauftragter, getrennter Qualifikationslauf mit
neuen regulären Figuren wäre eine **neue** Testkampagne. Er wäre kein
Nachweis, dass der alte P3-Request wiederhergestellt oder der frühere LA1-Lauf
abgeschlossen wurde. Eine solche Kampagne benötigt eine eigene endliche
Freigabe und darf keine alten Budgets erneuern.

Stand 16. Oktober 2026 (Belegpräzisierung, keine neue Reifeaussage): die
private offline Generalprobe (nicht Teil dieser öffentlichen Kopie) belegt
inzwischen fünf reguläre Figurenannahmen, zwei echte Abschnitte mit
organischer A→B-Savekontinuität über den Store, einen echten
Prozessneustart und einen getrennt ausgewiesenen Lobby-Wiederaufruf nach
Abschnittsabschluss (0 Spielleitungs-, 5 Personaanfragen) — weiterhin
ausschließlich mit skriptierten Antworten, kein Livebeleg. Ein ebenfalls
privater `--check`/`--dry-run`/`--execute`-Qualifikationstreiber orchestriert
denselben Produktweg über echte Adapterfactories; `--execute` bleibt ohne
eine gesondert gebundene, nach dem bedingten Feature-Push erteilte Freigabe
abgewiesen. Kein bezahlter Lauf, keine neue Kampagne wurde dadurch
eröffnet.

## Reifeaussagen

Der Integrationsstand ist noch kein Stable-Release. Eine bestandene
Offlineprüfung belegt ihren jeweiligen Umfang, nicht automatische
Live-Reife, plattformweite Regeltreue, LAN-Spielbarkeit oder vollständige
Backup-/Restore-Fähigkeit. Nach tatsächlichem Liveabschluss wird diese
Seite anhand der konkreten Ergebnisse aktualisiert; die Kennzeichnung
ändert sich nicht allein wegen einer schöneren README.

Historische Details: [Betriebsdokumentation](mmo-sim.md), insbesondere der
[LA1-Abschnitt](mmo-sim.md#la1--live-alltagsabnahme-2026-10-13).
