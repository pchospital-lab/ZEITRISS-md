# ZEITRISS®-md: Plattform‑Onboarding, portable JSON‑Saves und README‑Neuschliff

## Executive Summary

Das Repository positioniert **ZEITRISS®-md** bereits klar als KI‑geleitetes Tech‑Noir‑Zeitreise‑RPG mit **explodierenden Würfeln** und **JSON‑Charakterbögen** sowie einem schnellen Einstieg über **Script‑Setup in OpenWebUI**. fileciteturn8file7L1-L33  
Die zentrale Stärke, die in deinem Briefing (Screenshot) besonders stark herauskommt, ist jedoch in der aktuellen README noch „zu leise“: **Der JSON‑Speicherstand ist nicht nur eine Exportfunktion – er ist dein portabler Charakterbogen, also das Ownership‑Objekt des Spiels.** Spieler*innen können ihren Charakter (und damit ihre Kampagne) **plattformübergreifend** mitnehmen: Wohnzimmer‑Runde → danach Save splitten → zuhause solo weiterspielen → später wieder drop‑in/drop‑out mit einer anderen Gruppe. Diese „dezentral‑MMO‑ohne‑Server“-Erzählung ist das emotionale und technische Alleinstellungsmerkmal und sollte deshalb **oben** in die README, noch vor (oder direkt nach) dem 5‑Minuten‑Setup. fileciteturn8file7L1-L33

Technisch ist die Architektur dafür bereits sauber angelegt:  
- Der **Masterprompt** ist als **Systemprompt** gedacht (nicht als Wissensdatei) und enthält u. a. das **Save‑Schema v6** und die Kommandos für Start/Load. fileciteturn8file11L1-L45  
- Die Plattform‑Referenz ist ein **Wissensspeicher mit 20 Modulen** (Spieler‑Handbuch + 19 Runtime‑Module). fileciteturn8file9L1-L14  
- Das Speicher‑/Fortsetzungssystem definiert einen klaren HQ‑Loop und Cross‑Mode‑Regeln (Solo↔Koop↔Arena), inklusive Host‑Priorität beim Merge. fileciteturn18file6

Was jetzt fehlt, ist vor allem **Onboarding‑Copy**: ein „plattformagnostischer“ Setup‑Abschnitt (Systemprompt‑Feld vs. kein Systemprompt‑Feld → dann erste Chatnachricht) und ein „Bring‑Your‑Character“-Abschnitt, der das portable Savegame als Kernfeature verkauft.

## Kernidee und Differenzierung

ZEITRISS ist im Repo bereits als **KI‑first Betrieb** beschrieben: Die Spielleitung läuft „im Chat“, optional mit Voice, und das Projekt setzt bewusst auf Self‑Hosting/DIY statt zentrale Serverinstanz. fileciteturn8file7L113-L139  
Genau hier greift deine stärkste Produktstory: **Nicht Server‑Persistenz, sondern Spieler‑Persistenz.** Der Save ist ein **versionierter JSON‑Block**, der den Zustand in einem stabilen Schema abbildet und dadurch „mitwandert“ – du bist nicht an eine geschlossene Plattform‑Save‑Datenbank gebunden, sondern hast etwas, das du **kopieren, sichern, versionieren, teilen und wieder importieren** kannst. (Diese Logik wird im Masterprompt und im Speicher‑Modul explizit als Schema/Flow beschrieben.) fileciteturn8file11L1-L45 fileciteturn18file6

Das schafft genau das, was du „MMO‑Punkt“ nennst: **Drop‑in/Drop‑out‑Multiplayer über Chat**, ohne Matchmaking‑Server, ohne proprietäre Charakter‑Locks. Inhaltlich ist außerdem der „One‑Build“-Gedanke konsistent: *ein* Regelstand, der (über Wissensmodule + Masterprompt) auf unterschiedliche Plattformen gespiegelt werden kann. fileciteturn8file0L20-L43

Zusätzlich passt diese Story sehr gut zu eurer Privacy‑Ausrichtung („kein Zwang zur zentralen Infrastruktur“). In den internen Hosting‑Notizen wird explizit ein dezentraler Betrieb und Datensparsamkeit über Exporte empfohlen. fileciteturn8file0L44-L77  
Wenn Nutzer*innen bewusst eine privacy‑zentrierte Umgebung wählen wollen, ist **Proton Lumo** ein Beispiel für ein System, das „no‑logs“ und „zero‑access encryption“ für Chat‑Historien betont (wichtig: Plattformdetails können sich ändern; als Marketing‑/Policy‑Statement ist es aber eine starke Option für die README‑Sektion „Privacy‑Optionen“). citeturn4search1turn4search5

## Technische Bausteine, die plattformübergreifend stabil bleiben

Das Repo trennt bereits sauber zwischen „Regel-/Wissensbasis“ und „Steuerung“:

Die Wissensbasis besteht aus einem fixen Satz an Modulen, die in OpenWebUI als Knowledge Base mit 20 Slots geladen werden (Spieler‑Handbuch plus 19 Runtime‑Module). fileciteturn8file9L1-L14  
Die SSOT‑Logik dazu liegt im `master-index.json` (Slots markieren, Varianten/Aliase zählen nicht). fileciteturn6file13

Der Masterprompt (`meta/masterprompt_v6.md`) ist ausdrücklich **System Prompt (Uncut v4.2.6)** und soll nur im Systemfeld liegen (nicht im Wissensspeicher). fileciteturn8file11L1-L15  
Er definiert außerdem den Start‑Dispatcher (Start‑Kommandos vs. Load‑Flow) sowie den Output‑Contract und enthält ein vollständiges JSON‑Save‑Schema, das bei `!save`/`speichern` ausgegeben werden muss. fileciteturn8file11L150-L220

Das Speicher‑/Fortsetzungssystem ist als eigenes Runtime‑Modul dokumentiert und setzt die wichtigen Invarianten: **HQ‑Only Save**, klarer Load‑Flow, Cross‑Mode‑Import (Solo→Koop/Arena) und Host‑Priorität beim Merge. fileciteturn18file6  
Wichtig für „plattformübergreifend kompatibel“ ist der dort beschriebene Versions‑ und Guard‑Gedanke (v6‑Schema, semver‑Gate, deterministische Pflichtpfade). Das ist genau der Hebel, mit dem ihr „dein Save ist überall derselbe“ sagen könnt – mit der präzisen Einschränkung: **so lange Major/Minor kompatibel sind** (Patch‑Level ist toleranter). fileciteturn18file6

## Plattform‑Kompatibilität und Setup‑Rezepte

Für die README ist es hilfreich, nicht „jede Plattform der Welt“ aufzuzählen, sondern **Kompatibilitäts‑Stufen** festzunageln. Das macht die Anleitung langlebig, selbst wenn UIs sich umbenennen.

### Mindestanforderungen für „ZEITRISS‑kompatibel“

Eine Plattform ist praktisch kompatibel, wenn sie Folgendes kann:

- **Systemprompt/Instruktionsfeld** (oder ersatzweise: ihr könnt eine lange erste Nachricht als „Regelvertrag“ setzen).  
- **Dokument‑Kontext** (ideal: Knowledge/Files/RAG; Minimum: Dateiupload oder Copy‑Paste großer Texte).  
- **Stabile Chat‑Session** (Kontext groß genug für Mission/Briefing/Debrief; je größer, desto stabiler).  
- **Unveränderte JSON‑Copy/Paste** (Saves dürfen nicht „formatiert kaputt“ gemacht werden).

Diese Logik deckt sich mit dem OpenWebUI‑Ansatz, wo „Model Presets“ explizit System Prompts, Knowledge Collections und Tooling an ein Base‑Model binden. citeturn2search0

### Referenzpfad: OpenWebUI (Script‑Setup)

Das Repo benennt den Standardpfad: Script‑Setup in OpenWebUI plus danach kurzer Check „Masterprompt gesetzt, Wissensspeicher verknüpft (20 Slots)“. fileciteturn8file7L15-L33  
Das Setup‑Script selbst ist als idempotent dokumentiert und erwartet: OpenWebUI läuft lokal, Provider‑Key (z. B. OpenRouter) ist in den Verbindungen gesetzt, und ein OpenWebUI‑API‑Key existiert. fileciteturn10file1L1-L30  

Wichtig (für eure README‑Copy): OpenWebUI ist in den offiziellen Docs **protokollorientiert** (OpenAI Chat Completions API) und arbeitet mit OpenAI‑kompatiblen Providern, Proxies und lokalen Servern. Das ist exakt die Brücke, um „fast überall lauffähig“ sauber zu begründen. citeturn2search5turn2search7

### Provider‑Beispiele: OpenRouter und Groq

Für eure „plattformagnostische“ README‑Anleitung ist es wertvoll, zwei Dinge konkret zu nennen: „OpenAI‑kompatibel“ heißt (a) Chat‑Completions‑Endpoint und (b) Modell‑IDs.

- OpenRouter dokumentiert ein OpenAI‑kompatibles Chat‑Completions‑API und beschreibt u. a. Model‑Routing, Parameter‑Forwarding und Fallback‑Verhalten. citeturn0search1  
- Groq dokumentiert explizit „OpenAI Compatibility“ und nennt das Base‑URL‑Pattern für die OpenAI‑kompatiblen Endpoints (`https://api.groq.com/openai/v1`). citeturn0search0  

Diese beiden Quellen reichen, um in der README seriös zu sagen: „Wenn dein Anbieter OpenAI‑kompatible Endpoints anbietet, funktioniert ZEITRISS in der Regel auch dort.“

### Privacy‑Option: Proton Lumo

Wenn ihr in der README alternative Spielumgebungen nennen wollt, ist **Proton Lumo** ein gutes Beispiel für „privacy‑orientierter Chat“: Proton beschreibt u. a. „no‑logs“, „zero‑access encrypted chat history“ und „no training“, sowie optionales Web‑Search‑Opt‑in und Serverbetrieb unter eigener Kontrolle. citeturn4search1turn4search5  
Außerdem erwähnt Proton, dass Lumo Dokumente über (u. a.) Proton Drive in den Arbeitskontext holen kann und dass man Chat‑Instruktionen/Stilvorgaben setzen kann – was sich gut mit eurem „Masterprompt + Wissenspaket“‑Paradigma verbindet. citeturn4search6  

Für eure README‑Formulierung ist wichtig: Nicht behaupten, Lumo hätte „ein Systemprompt‑Feld wie OpenWebUI“, sondern sauber die generische Regel nennen: *Wenn es ein Instruktionsfeld gibt → Masterprompt dort rein; wenn nicht → Masterprompt als erste Chatnachricht.*

### Local Runner: LM Studio als Beispiel

Für Local‑Runner solltet ihr in der README nicht in UI‑Klickpfade verfallen (Screenshots altern schnell), sondern nur sagen: „System/Instruction Prompt setzen; Prompt‑Template nicht in Template‑Syntax kippen lassen; Dateien als Kontext hinzufügen“. LM Studio dokumentiert, dass Prompt‑Templates modellabhängig sind und man sie ggf. anpassen kann. citeturn2search1  

## Multiplayer‑Handoffs und Save‑Splits als „Drop‑in/Drop‑out“

Die README erwähnt Multiplayer aktuell nur als kurzer Hinweis („lokal oder online … Save‑Stand und Chatlog teilen“). fileciteturn8file7L126-L132  
Die eigentliche Stärke liegt aber darin, Multiplayer als **Workflow** zu erklären – und zwar so, dass Leute sofort verstehen: „Ich bringe meinen Charakter mit.“

Das Speicher‑Modul beschreibt dafür die entscheidenden Mechaniken, die ihr in README‑Copy übersetzen könnt:

- **HQ‑Only Save** als Spannungsgarantie und Standard‑Loop „Mission → Debrief → HQ → Save → neuer Chat empfohlen“. fileciteturn18file6  
- **Host‑Regel** beim Mehrfach‑Import: Wenn mehrere Saves gepostet werden, gilt der zuerst gepostete Save als Host; sein Kampagnenblock gewinnt, weitere Saves liefern Charakter/Loadout/Wallet‑Anteile. fileciteturn18file6  
- **Cross‑Mode‑Transfers** (Solo→Koop→Arena etc.) sind als Transferlogik beschrieben, was ideal zum „Save split & zuhause weiter“ passt. fileciteturn18file6  

Wenn ihr das in 8–12 Zeilen in die README gießt, sinkt die Einstiegshürde massiv: Menschen sehen sofort, **wie** man gemeinsam spielt, ohne dass ihr Discord‑Bots, Pipes oder „später“ braucht.

## Copy‑Paste‑Bausteine für die README

Die folgenden Textblöcke sind bewusst so geschrieben, dass du sie 1:1 übernehmen kannst. Sie sind „plattformagnostisch“ formuliert, nennen aber euren Referenzpfad klar.

```markdown
## Das Besondere an ZEITRISS: Dein Save IST dein Charakter (und gehört dir)

ZEITRISS ist kein klassisches „Spiel mit Server-Account“.  
Du spielst in einem Chat – und **dein Charakterbogen ist ein versionierter JSON‑Speicherstand**.

Das heißt:
- Du kannst deinen Charakter **überall hin mitnehmen** (jede kompatible Chat‑Plattform, lokal oder Cloud).
- Du kannst **mit Freunden lokal spielen**, danach den Save **splitten** und zuhause solo weiterspielen.
- Du kannst später wieder **drop‑in/drop‑out** mit einer anderen Gruppe spielen – ohne Matchmaking-Server, ohne proprietären Lock‑In.

**Merksatz:** Wenn du deinen JSON‑Save hast, kann dir niemand deinen Charakter wegnehmen.
```

```markdown
## Plattform‑Setup: ZEITRISS läuft überall, wo Systemprompt + Wissenspaket möglich sind

ZEITRISS ist „LLM‑ready“. Du brauchst nur zwei Dinge:

1) **Wissenspaket (20 Module)**  
   Lade `core/spieler-handbuch.md` + 19 Runtime‑Module als Knowledge/Files/Docs in deine Plattform.
2) **Masterprompt (Systemprompt)**  
   Kopiere den Inhalt von `meta/masterprompt_v6.md` in das **Systemprompt-/Instructions‑Feld**.

👉 **Wenn deine Plattform kein Systemprompt‑Feld hat:**  
Dann poste `meta/masterprompt_v6.md` **als allererste Chatnachricht**, bevor du „Spiel starten“ tippst.

Danach startest du ZEITRISS mit:
- `Spiel starten (solo klassisch)` (empfohlen)
- oder `Spiel starten (solo schnell)`
- oder `Spiel laden` + JSON‑Save
```

```markdown
## In 5 Minuten starten (Referenzpfad)

### Standard (empfohlen): OpenWebUI + Setup‑Script

1. OpenWebUI starten.
2. Provider verbinden (OpenAI‑kompatibel, z. B. OpenRouter / Groq / lokaler Server).
3. In OpenWebUI einen API‑Key erzeugen (Einstellungen → Konto → API‑Schlüssel).
4. Repo holen (Git oder ZIP), dann im Repo‑Ordner:
   `./scripts/setup-openwebui.sh`
5. Neuen Chat → Modell „ZEITRISS … Uncut“ wählen → `Spiel starten (solo klassisch)`
```

```markdown
## Multiplayer ohne Server: Bring‑Your‑Character

Du kannst ZEITRISS schon heute als Gruppe spielen – mit einem simplen Ablauf:

- Eine Person ist **Host** und hat den Chat offen (vor Ort oder per Stream/Screenshare).
- Alle spielen gemeinsam, sagen ihre Aktionen an.
- Im HQ wird gespeichert (`!save`) → der Host postet den JSON‑Block in euren Chat/Drive.
- Jeder kann später:
  - denselben Gruppen‑Save wieder laden, oder
  - seinen Charakter als eigenen save weiterführen (z. B. zuhause solo).

Das ist Drop‑in/Drop‑out Multiplayer – ohne Infrastruktur, nur mit Chat + JSON.
```

## Issue‑Backlog für Codex: konkrete Fixes am Onboarding‑Text

Die meisten „Einstiegshürde“-Probleme sind Copy/Struktur, nicht Regeln. Dafür sind diese Issues am wertvollsten (und direkt aus Repo‑Iststand ableitbar):

Erweitere die README‑Hero‑Section um „Bring‑Your‑Character“  
Warum: Aktuell steht „JSON‑Charakterbögen“ zwar in der Kurzfassung, aber die Ownership‑Story fehlt als Aufhänger. fileciteturn8file7L1-L12

Füge eine plattformagnostische Setup‑Sektion hinzu (Systemprompt‑Feld vs. erste Chatnachricht)  
Warum: Das Setup‑Guide‑Prinzip „Masterprompt ins Systemfeld, 20 Module als Knowledge“ ist da, aber im README‑Top fehlt die universelle Regel. fileciteturn8file7L24-L44 fileciteturn8file9L1-L14

Bringe README‑Setup und Script‑Voraussetzungen sprachlich zusammen  
Warum: Das Script setzt explizit OpenWebUI‑API‑Key + Provider‑Connection voraus; README nennt derzeit eher grob „OpenWebUI installieren und OpenRouter‑Konto erstellen“. Präziser Text reduziert Setup‑Fehlversuche. fileciteturn10file1L1-L30 fileciteturn8file7L17-L33

Optional, aber stark: „Kompatibilitäts‑Stufen“ als Mini‑Matrix  
Warum: OpenWebUI‑Docs betonen „OpenAI‑kompatible Provider“ und „Preset/Knowledge‑Binding“. Das lässt sich als zeitloser Kompatibilitäts‑Check formulieren, ohne jeden Anbieter einzeln pflegen zu müssen. citeturn2search0turn2search5turn2search7

Optional: „Privacy‑Optionen“ als kurzer Absatz  
Warum: Eure Verteilungs-/Hosting‑Notizen zielen auf dezentral/privat; Proton Lumo liefert dafür ein starkes, offizielles Privacy‑Narrativ (no‑logs, zero‑access encryption). fileciteturn8file0L44-L77 citeturn4search1turn4search5