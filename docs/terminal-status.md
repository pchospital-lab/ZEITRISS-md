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

Stand 22. Oktober 2026 (R4-Mehrspieler-Anschluss, Endstand): Ein zusätzlicher
Erstharvest-Savekonflikt wurde behoben — zwei abweichende, jeweils gültige
Speicherstände derselben Figur in einer Spielleitungsantwort werden jetzt VOR
jeder Abschlussveröffentlichung erkannt und der Abschnitt gehalten, statt still
den ersten zu übernehmen (identische Wiederholungen bleiben zulässig). Für den
Mehrfiguren-Weg wurden zwei weitere Ursachen adressiert: die KI-Mitspieler laufen
jetzt standardmäßig ohne erweitertes Nachdenken (deutlich schnellere, kurze
Spielerzüge; in einem realen Livelauf lösten sich die zuvor beobachteten
Zeitüberschreitungen vollständig auf), und die Mitspieler-Personas erhalten eine
knappe Terminal-Bedienungsnotiz, damit sie das Speicherkommando am
Abschnittsende selbst absetzen (zuvor umschrieben sie es nur narrativ). In
realen, bezahlten Liveläufen wurden daraufhin alle fünf regulären
Bestandsfiguren tatsächlich erschaffen bzw. importiert und eine organische
Gruppe spielte eine vollständige Mission bis zur HQ-Rückkehr. Ein strukturell
abgeschlossener Mehrfiguren-Abschnitt (Abschnitts-Finalrecord live) wurde dabei
noch NICHT erreicht — die Ursache liegt NICHT im geprüften Produktcode, sondern
in einem eng umrissenen Verhalten des privaten Test-Treibers (ein gutartiges
Zeitfenster-Ende eines Einzelschritts wird derzeit als terminaler Halt
fehlklassifiziert) zusammen mit dem begrenzten Live-Budget dieses Zyklus. Der
kommandobasierte Abschnittsabschluss, der Savekonflikt-Fix und die
Save-Kommando-Erkennung bleiben durch den Einzelspieler-Livebeleg, die
synthetische Fünf-Figuren-A/B-Prüfung und gezielte Komponententests bestätigt.

Stand 23. Oktober 2026 (R4-Gruppenabschluss-Anschluss, beobachteter Stand): In
einem realen, bezahlten Mehrspieler-Lauf wurden alle fünf regulären
Bestandsfiguren tatsächlich bereitgestellt (zwei über den Importweg, drei
organisch erschaffen), eine organische Gruppe bildete einen Zweier- und einen
Dreiertisch, und der Dreiertisch spielte Abschnitt A bis in den Speicher- und
Abschlussablauf: das Leader-Speicherkommando wurde ausgelöst, die
Gruppen-Speicherstände der Mitglieder wurden geerntet und schema-korrigiert und
der Abschluss-Plan wurde geschrieben. Ein strukturell abgeschlossener Abschnitt
(Abschnitts-Finalrecord, danach Prozessneustart und zweiter Abschnitt) wurde in
diesem Lauf noch nicht erreicht: der Lauf endete an einer einzelnen
vorübergehenden Störung des isolierten Mitspieler-Prozesses (Exitcode ungleich
null ohne jede Fehlerausgabe), während der Abschnitt bereits finalisiert wurde.
Die Ursache liegt nicht im geprüften Produktcode, sondern war eine transiente
Infrastruktur-Störung; der private Test-Treiber behandelt eine solche
vorübergehende Störung in der Abschnittsphase jetzt wie eine Zeitpause (begrenzte
Wiederaufnahme im nächsten Schritt) statt als endgültigen Halt. Der vollständige
strukturelle Mehrfiguren-Abschluss über zwei Abschnitte bleibt damit der noch
offene Live-Nachweis und ist durch das verbleibende Live-Budget dieses Zyklus
begrenzt, nicht durch einen Produkt- oder Regelfehler.

Stand 23. Oktober 2026 (R4-Beta-Anschluss, beobachteter Stand): Der Generalreview der Rohbelege identifizierte vier konkrete Produktursachen (offener Abschlussplan wurde im Lobby-Resume nicht fortgesetzt; ein alleinstehendes Leader-Speicherkommando ohne nutzbaren Export lief in weitere Spielrunden; die A/B-Bindung erkannte den zweiten Abschnitt nicht an die beobachtete Gruppe; der Mitspieler-Adapter verwarf bei Fehlern den Standardausgabekanal). Diese vier Ursachen wurden am normalen Produktpfad behoben und sind durch gezielte Tests belegt. Zusätzlich fängt das Terminal ein Kontingent-/Budgetende mitten im Spiel (Abo- bzw. OpenRouter-Limit) jetzt als klaren, speichernden Pausenhinweis ab und ist danach nahtlos fortsetzbar, statt mit einem Fehler abzubrechen. In einem realen, bezahlten Lauf wurde Abschnitt A strukturell abgeschlossen, der Prozess regulär neu gestartet und Abschnitt B tatsächlich weitergespielt (fortgeschriebene Speicherstände über den Prozessneustart hinweg); ein Mitspieler-Prozess traf dabei real ein Kontingentende, das der neue Pausenhinweis sauber abfing. Ein strukturell abgeschlossener zweiter Abschnitt (Finalrecord für Abschnitt B) wurde in diesem Lauf noch nicht erreicht: im langen Abschnitts-B-Kontext wichen einzelne Mitspieler-Antworten in erklärende Meta-Kommentare aus, sodass das abschließende Speicherkommando am Abschnittsende ausblieb; dies ist der präzise benannte, noch offene Punkt für eine gezielte Folgeiteration und keine Aussage über vollständige Stable-Reife. Produktseitig sind die genannten Korrekturen und der Kontingent-Pausenhinweis in diesem Stand enthalten.

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
