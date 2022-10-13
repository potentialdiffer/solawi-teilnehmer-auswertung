# Teilnehmeranalyse

Dieses Skript erstellt eine Teilnehmeranalyse aus exportierten `.csv` Dateien von S-Verein.

## Requirements

Am besten eine virtuelle Environment erstellen:

```
python -m venv .venv-teilnehmer-analyse
source .venv-teilnehmeranalyse/bin/activate
pip install -r requirements.txt
```

## Auswetung der aktuellen Teilnehmerdaten

1. Folgende zwei listen aus S-Verein exportieren:
    - Export-Skript (ist die abteilungsliste)
    - Übersicht (ist die teilnehmerliste)
2. Die Listen in diesen Ordner laden
3. Ausführen des Skripts mit zwei Parametern:
    - `abteilungen.csv`
    - `mitglieder.csv`
    - `output-markdown-path`: Name der output Datei. Sie ist mit Markdown formatiert. Kann z.b. README.md oder HEADER.md heißen, dann wird sie direkt in Nextcloud gerendert.

```
python teilnehmer-analyse.py <abteilungen.csv> <mitglieder.csv> <output-bericht-path> <stichtag [dd-mm-yyyy]> <--plot [true, false]>
```

- `stichtag`: ist das Datum zu welchem Zeitpunkt die Teilnehmerzahl bestimmt werden soll.
- `plot`: erzeugt Graphen mit den Teilnehmerzahlen üer die vergangenen Jahre. Kann im Code weiter Konfiguriert werden.

## TODO

Gemüse und andere Listen erstellen
- (Adressen exportieren) PLZ und Ort
- Anteile
- (Telefon)
- Nach "Zugehörigkeit" Filtern
- Person hat keine Email hinterlegt. Wie verfährt man damit?
