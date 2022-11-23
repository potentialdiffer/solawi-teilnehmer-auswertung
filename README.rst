.. These are examples of badges you might want to add to your README:
   please update the URLs accordingly

    .. image:: https://api.cirrus-ci.com/github/<USER>/solawi-teilnehmer-auswertung.svg?branch=main
        :alt: Built Status
        :target: https://cirrus-ci.com/github/<USER>/solawi-teilnehmer-auswertung
    .. image:: https://readthedocs.org/projects/solawi-teilnehmer-auswertung/badge/?version=latest
        :alt: ReadTheDocs
        :target: https://solawi-teilnehmer-auswertung.readthedocs.io/en/stable/
    .. image:: https://img.shields.io/coveralls/github/<USER>/solawi-teilnehmer-auswertung/main.svg
        :alt: Coveralls
        :target: https://coveralls.io/r/<USER>/solawi-teilnehmer-auswertung
    .. image:: https://img.shields.io/pypi/v/solawi-teilnehmer-auswertung.svg
        :alt: PyPI-Server
        :target: https://pypi.org/project/solawi-teilnehmer-auswertung/
    .. image:: https://img.shields.io/conda/vn/conda-forge/solawi-teilnehmer-auswertung.svg
        :alt: Conda-Forge
        :target: https://anaconda.org/conda-forge/solawi-teilnehmer-auswertung
    .. image:: https://pepy.tech/badge/solawi-teilnehmer-auswertung/month
        :alt: Monthly Downloads
        :target: https://pepy.tech/project/solawi-teilnehmer-auswertung
    .. image:: https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter
        :alt: Twitter
        :target: https://twitter.com/solawi-teilnehmer-auswertung

.. image:: https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold
    :alt: Project generated with PyScaffold
    :target: https://pyscaffold.org/

|

============================
solawi-teilnehmer-auswertung
============================

    Teilnehmeranalyse für aus S-Verein exportierte Daten.



Installation
=============

```
$ git clone https://github.com/potentialdiffer/solawi-teilnehmer-auswertung
$ cd solawi-teilnehmer-auswertung
$ pip install .
```

Usage
=====

1. Folgende zwei Listen aus S-Verein exportieren:
    - Export-Skript (ist die abteilungsliste)
    - Übersicht (ist die teilnehmerliste)
2. Die Listen in diesen Ordner laden
3. Ausführen des Skripts mit zwei Parametern:
    - `abteilungen.csv`
    - `mitglieder.csv`
    - `output-markdown-path`: Name der output Datei. Sie ist mit Markdown formatiert. Kann z.b. README.md oder HEADER.md heißen, dann wird sie direkt in Nextcloud gerendert.

```
$ python teilnehmer-analyse.py <abteilungen.csv> <mitglieder.csv> <output-bericht-path> <stichtag [dd-mm-yyyy]> <--plot start_year end_year>
```

- `stichtag`: ist das Datum zu welchem Zeitpunkt die Teilnehmerzahl bestimmt werden soll.
- `--plot start_year end_year`: erzeugt Graphen mit den Teilnehmerzahlen im angegebenen Jahreszeitraum.

TODO
====

Gemüse und andere Listen erstellen
- (Adressen exportieren) PLZ und Ort
- Anteile
- (Telefon)
- Nach "Zugehörigkeit" Filtern
- Person hat keine Email hinterlegt. Wie verfährt man damit?


.. _pyscaffold-notes:

Note
====

This project has been set up using PyScaffold 4.3.1. For details and usage
information on PyScaffold see https://pyscaffold.org/.
