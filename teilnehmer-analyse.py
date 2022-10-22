#!/bin/python3
import sys
import os
import re
import pandas as pd
import numpy as np
from datetime import date
from datetime import datetime
from dateutil.parser import parse
import argparse

class DataEvaluation:

    teilnehmer_data = {}
    in_abteilungen_file = ""
    in_mitglieder_file = ""
    output_file = ""

    def __init__(self, in_abteilungen_file, in_mitglieder_file, out_path, stichtag):

        # define input and output file names
        self.in_abteilungen_file = in_abteilungen_file
        self.in_mitglieder_file = in_mitglieder_file
        self.output_file = out_path
        self.stichtag = parse(stichtag).date()

        print(f"Teilnehmer Auswertung für Stichtag: {self.stichtag}")

        # open file exported from s-verein
        try:
            print("Reading %s" % self.in_abteilungen_file)
            table_abteilungen = pd.read_csv(self.in_abteilungen_file, sep=";")#, on_bad_lines='warn')
        # except if file is not found and write error message to file
        except FileNotFoundError:
            print("[Error] Cannot find file named %s" % self.in_abteilungen_file)
            with open(self.output_file, 'w') as f:
                f.write('__Fehler: kann Datei %s nicht finden.__' % self.in_abteilungen_file)
            exit(1)
        # except all other errors
        except Exception as e:
            print("Error exiting.")
            print(e)
            exit(1)

        # open file exported from s-verein
        try:
            print("Reading %s" % self.in_mitglieder_file)
            table_mitglieder = pd.read_csv(self.in_mitglieder_file, sep=';')#, on_bad_lines='warn')
        # except if file is not found and write error message to file
        except FileNotFoundError:
            print("[Error] Cannot find file named %s" % self.in_mitglieder_file)
            with open(self.output_file, 'w') as f:
                f.write('__Fehler: kann Datei %s nicht finden.__' % self.in_mitglieder_file)
            exit(1)
        # except all other errors
        except Exception as e:
            print("Error exiting.")
            print(e)
            exit(1)

        today = date.today()
        date_sommer = self.get_date_summer(self.stichtag)
        date_winter = self.get_date_winter(self.stichtag)

        t_abteilungen = table_abteilungen.filter(items=['Mitglieds-Nr', 'Abteilungsbezeichnung',
                                'Beitragsbezeichnung', 'Abteilungsaustritt',
                                'Beitragsaustritt'])
        t_mitglieder = table_mitglieder.filter(items=['Mitglieds-Nr', 'E-Mail'])

        # filter die Beitragsbezeichnungen
        beitragsbez = t_abteilungen['Beitragsbezeichnung'].unique()
        map_dict = {}

        for b in beitragsbez:
            if isinstance(b, float):
                b = '1'
            amount = [int(i) for i in b.split() if i.isdigit()]
            map_dict[b] = int(amount[0]) if amount else int(1)

        t_abteilungen['Beitragsbezeichnung'] = t_abteilungen['Beitragsbezeichnung'].map(map_dict)

        # convert string to datetime
        for i, d in enumerate(t_abteilungen['Abteilungsaustritt']):
            if not isinstance(d, float):
                t_abteilungen.loc[i, 'Abteilungsaustritt'] = datetime.strptime(d, '%d.%m.%Y').date()

            # if no date is available, set date to start of next term
            else:
                t_abteilungen.loc[i, 'Abteilungsaustritt'] = date_winter if t_abteilungen.loc[i, 'Abteilungsbezeichnung'] == 'Winter' else date_sommer

            # other cooperations usually have no exit date. Simply set to today.
            if (t_abteilungen.loc[i, 'Abteilungsbezeichnung'] == 'Eier' or t_abteilungen.loc[i, 'Abteilungsbezeichnung'] == 'Käse' or t_abteilungen.loc[i, 'Abteilungsbezeichnung'] == 'Brot'):
                t_abteilungen.loc[i, 'Abteilungsaustritt'] = self.stichtag

        for i, d in enumerate(t_abteilungen['Beitragsaustritt']):
            if not isinstance(d, float):
                t_abteilungen.loc[i, 'Beitragsaustritt'] = datetime.strptime(d, '%d.%m.%Y').date()

            # if no date is available, set date to start of next term
            else:
                t_abteilungen.loc[i, 'Beitragsaustritt'] = date_winter if t_abteilungen.loc[i, 'Abteilungsbezeichnung'] == 'Winter' else date_sommer

            # other cooperations usually have no exit date. Simply set to today.
            if (t_abteilungen.loc[i, 'Abteilungsbezeichnung'] == 'Eier' or t_abteilungen.loc[i, 'Abteilungsbezeichnung'] == 'Käse' or t_abteilungen.loc[i, 'Abteilungsbezeichnung'] == 'Brot'):
                t_abteilungen.loc[i, 'Abteilungsaustritt'] = self.stichtag

        sommer = t_abteilungen.loc[
            (t_abteilungen['Abteilungsbezeichnung'] == 'Sommer') &
            (t_abteilungen['Abteilungsaustritt'] >= self.stichtag) &
            (t_abteilungen['Beitragsaustritt'] >= self.stichtag)
            ]
        sommer_ausgetreten = t_abteilungen.loc[
            (t_abteilungen['Abteilungsbezeichnung'] == 'Sommer') &
            (t_abteilungen['Abteilungsaustritt'] < self.stichtag) &
            (t_abteilungen['Beitragsaustritt'] < self.stichtag)
            ]

        winter = t_abteilungen.loc[
            (t_abteilungen['Abteilungsbezeichnung'] == 'Winter') &
            (t_abteilungen['Abteilungsaustritt'] >= self.stichtag) &
            (t_abteilungen['Beitragsaustritt'] >= self.stichtag)
            ]
        winter_ausgetreten = t_abteilungen.loc[
            (t_abteilungen['Abteilungsbezeichnung'] == 'Winter') &
            (t_abteilungen['Abteilungsaustritt'] < self.stichtag) &
            (t_abteilungen['Beitragsaustritt'] < self.stichtag)
            ]

        eier = t_abteilungen.loc[
            (t_abteilungen['Abteilungsbezeichnung'] == 'Eier') &
            (t_abteilungen['Abteilungsaustritt'] >= self.stichtag) &
            (t_abteilungen['Beitragsaustritt'] >= self.stichtag)
            ]
        eier_ausgetreten = t_abteilungen.loc[
            (t_abteilungen['Abteilungsbezeichnung'] == 'Eier') &
            (t_abteilungen['Abteilungsaustritt'] < self.stichtag) &
            (t_abteilungen['Beitragsaustritt'] < self.stichtag)
            ]

        kase = t_abteilungen.loc[
            (t_abteilungen['Abteilungsbezeichnung'] == 'Käse') &
            (t_abteilungen['Abteilungsaustritt'] >= self.stichtag) &
            (t_abteilungen['Beitragsaustritt'] >= self.stichtag)
            ]
        kase_ausgetreten = t_abteilungen.loc[
            (t_abteilungen['Abteilungsbezeichnung'] == 'Käse') &
            (t_abteilungen['Abteilungsaustritt'] < self.stichtag) &
            (t_abteilungen['Beitragsaustritt'] < self.stichtag)
            ]

        brot = t_abteilungen.loc[
            (t_abteilungen['Abteilungsbezeichnung'] == 'Brot') &
            (t_abteilungen['Abteilungsaustritt'] >= self.stichtag) &
            (t_abteilungen['Beitragsaustritt'] >= self.stichtag)
            ]
        brot_ausgetreten = t_abteilungen.loc[
            (t_abteilungen['Abteilungsbezeichnung'] == 'Brot') &
            (t_abteilungen['Abteilungsaustritt'] < self.stichtag) &
            (t_abteilungen['Beitragsaustritt'] < self.stichtag)
            ]

        self.teilnehmer_data["s_ausgetreten"] = []
        self.teilnehmer_data["s_ausgetreten"].append(sommer_ausgetreten['Mitglieds-Nr'].unique())
        self.teilnehmer_data["w_ausgetreten"] = []
        self.teilnehmer_data["w_ausgetreten"].append(winter_ausgetreten['Mitglieds-Nr'].unique())
        self.teilnehmer_data["b_ausgetreten"] = []
        self.teilnehmer_data["b_ausgetreten"].append(brot_ausgetreten['Mitglieds-Nr'].unique())
        self.teilnehmer_data["e_ausgetreten"] = []
        self.teilnehmer_data["e_ausgetreten"].append(eier_ausgetreten['Mitglieds-Nr'].unique())
        self.teilnehmer_data["k_ausgetreten"] = []
        self.teilnehmer_data["k_ausgetreten"].append(kase_ausgetreten['Mitglieds-Nr'].unique())

        self.teilnehmer_data["s_teilnehmer"] = []
        self.teilnehmer_data["s_teilnehmer"].append(sommer['Mitglieds-Nr'].unique())
        self.teilnehmer_data["s_teilnehmer"] = t_mitglieder.loc[
                t_mitglieder['Mitglieds-Nr'].isin(["".join(item) for item in self.teilnehmer_data["s_teilnehmer"][0].astype(str)])]
        self.teilnehmer_data["w_teilnehmer"] = []
        self.teilnehmer_data["w_teilnehmer"].append(winter['Mitglieds-Nr'].unique())
        self.teilnehmer_data["w_teilnehmer"] = t_mitglieder.loc[
                t_mitglieder['Mitglieds-Nr'].isin(["".join(item) for item in self.teilnehmer_data["w_teilnehmer"][0].astype(str)])]
        self.teilnehmer_data["b_teilnehmer"] = []
        self.teilnehmer_data["b_teilnehmer"].append(brot['Mitglieds-Nr'].unique())
        self.teilnehmer_data["b_teilnehmer"] = t_mitglieder.loc[
                t_mitglieder['Mitglieds-Nr'].isin(["".join(item) for item in self.teilnehmer_data["b_teilnehmer"][0].astype(str)])]
        self.teilnehmer_data["e_teilnehmer"] = []
        self.teilnehmer_data["e_teilnehmer"].append(eier['Mitglieds-Nr'].unique())
        self.teilnehmer_data["e_teilnehmer"] = t_mitglieder.loc[
                t_mitglieder['Mitglieds-Nr'].isin(["".join(item) for item in self.teilnehmer_data["e_teilnehmer"][0].astype(str)])]
        self.teilnehmer_data["k_teilnehmer"] = []
        self.teilnehmer_data["k_teilnehmer"].append(kase['Mitglieds-Nr'].unique())
        self.teilnehmer_data["k_teilnehmer"] = t_mitglieder.loc[
                t_mitglieder['Mitglieds-Nr'].isin(["".join(item) for item in self.teilnehmer_data["k_teilnehmer"][0].astype(str)])]

        ausgetreten_gesamt = np.concatenate([self.teilnehmer_data["s_ausgetreten"][0],
                              self.teilnehmer_data["w_ausgetreten"][0],
                              self.teilnehmer_data["b_ausgetreten"][0],
                              self.teilnehmer_data["e_ausgetreten"][0],
                              self.teilnehmer_data["k_ausgetreten"][0]])

        self.teilnehmer_data["ausgetretene_mitglieder"] = t_mitglieder.loc[
                t_mitglieder['Mitglieds-Nr'].isin(["".join(item) for item in ausgetreten_gesamt.astype(str)])]
        pd.set_option('display.max_rows', None)


        for i, row in self.teilnehmer_data["ausgetretene_mitglieder"].iterrows():
            number = int(row['Mitglieds-Nr'])
            if not (sommer.loc[(sommer['Mitglieds-Nr'] == number)]).empty:
                self.teilnehmer_data["ausgetretene_mitglieder"]. \
                    drop(self.teilnehmer_data["ausgetretene_mitglieder"]. \
                     loc[self.teilnehmer_data["ausgetretene_mitglieder"].index == i].index, inplace=True)
            if not (winter.loc[(winter['Mitglieds-Nr'] == number)]).empty:
                self.teilnehmer_data["ausgetretene_mitglieder"]. \
                    drop(self.teilnehmer_data["ausgetretene_mitglieder"]. \
                     loc[self.teilnehmer_data["ausgetretene_mitglieder"].index == i].index, inplace=True)
            if not (brot.loc[(brot['Mitglieds-Nr'] == number)]).empty:
                self.teilnehmer_data["ausgetretene_mitglieder"]. \
                    drop(self.teilnehmer_data["ausgetretene_mitglieder"]. \
                     loc[self.teilnehmer_data["ausgetretene_mitglieder"].index == i].index, inplace=True)
            if not (kase.loc[(kase['Mitglieds-Nr'] == number)]).empty:
                self.teilnehmer_data["ausgetretene_mitglieder"]. \
                    drop(self.teilnehmer_data["ausgetretene_mitglieder"].
                     loc[self.teilnehmer_data["ausgetretene_mitglieder"].index == i].index, inplace=True)
            if not (eier.loc[(eier['Mitglieds-Nr'] == number)]).empty:
                self.teilnehmer_data["ausgetretene_mitglieder"]. \
                    drop(self.teilnehmer_data["ausgetretene_mitglieder"]. \
                     loc[self.teilnehmer_data["ausgetretene_mitglieder"].index == i].index, inplace=True)

        now = datetime.now()
        today_str = now.strftime("%Y%m%d")
        os.makedirs(today_str, exist_ok=True)
        self.teilnehmer_data["w_teilnehmer"].to_csv(today_str + "/winter.csv", sep=';')
        self.teilnehmer_data["s_teilnehmer"].to_csv(today_str + "/sommer.csv", sep=';')
        self.teilnehmer_data["e_teilnehmer"].to_csv(today_str + "/eier.csv", sep=';')
        self.teilnehmer_data["k_teilnehmer"].to_csv(today_str + "/kase.csv", sep=';')
        self.teilnehmer_data["b_teilnehmer"].to_csv(today_str + "/brot.csv", sep=';')
        self.teilnehmer_data["ausgetretene_mitglieder"].to_csv(today_str + "/ausgetreten.csv", sep=';')

        self.teilnehmer_data["aktive_mitglieder"] = []
        self.teilnehmer_data["aktive_mitglieder"] = pd.concat([
            self.teilnehmer_data["w_teilnehmer"],
            self.teilnehmer_data["s_teilnehmer"],
            self.teilnehmer_data["e_teilnehmer"],
            self.teilnehmer_data["k_teilnehmer"],
            self.teilnehmer_data["b_teilnehmer"]]).dropna()
        # print(self.teilnehmer_data["aktive_mitglieder"])
        # print(pd.unique(self.teilnehmer_data["aktive_mitglieder"]['E-Mail']))
        aktive_mitglieder = pd.unique(self.teilnehmer_data["aktive_mitglieder"]['E-Mail'])

        self.write_mail_to_file(aktive_mitglieder, '/aktive_mitglieder.txt', today_str)
        self.write_mail_to_file(self.teilnehmer_data["ausgetretene_mitglieder"]['E-Mail'], '/ausgetretene_mitglieder.txt', today_str)
        self.write_mail_to_file(self.teilnehmer_data["w_teilnehmer"]['E-Mail'], '/winter-mail.txt', today_str)
        self.write_mail_to_file(self.teilnehmer_data["s_teilnehmer"]['E-Mail'], '/sommer-mail.txt', today_str)
        self.write_mail_to_file(self.teilnehmer_data["e_teilnehmer"]['E-Mail'], '/eier-mail.txt', today_str)
        self.write_mail_to_file(self.teilnehmer_data["k_teilnehmer"]['E-Mail'], '/kase-mail.txt', today_str)
        self.write_mail_to_file(self.teilnehmer_data["b_teilnehmer"]['E-Mail'], '/brot-mail.txt', today_str)


        self.teilnehmer_data["s_teilnehmer"] = sommer.count()['Abteilungsbezeichnung']
        self.teilnehmer_data["s_anteile"] = sommer['Beitragsbezeichnung'].sum()
        self.teilnehmer_data["w_teilnehmer"] = winter.count()['Abteilungsbezeichnung']
        self.teilnehmer_data["w_anteile"] = winter['Beitragsbezeichnung'].sum()
        self.teilnehmer_data["e_teilnehmer"] = eier.count()['Abteilungsbezeichnung']
        self.teilnehmer_data["e_anteile"] = eier['Beitragsbezeichnung'].sum()
        self.teilnehmer_data["k_teilnehmer"] = kase.count()['Abteilungsbezeichnung']
        self.teilnehmer_data["k_anteile"] = kase['Beitragsbezeichnung'].sum()
        self.teilnehmer_data["b_teilnehmer"] = brot.count()['Abteilungsbezeichnung']
        self.teilnehmer_data["b_anteile"] = brot['Beitragsbezeichnung'].sum()


    def set_stichtag(sekf, stichtag):
        self.stichtag = parse(stichtag).date()


    def write_mail_to_file(self, mails, file_name, today_str):
        file = open(today_str + file_name, 'w')
        i = 0
        for mail in mails:
            i = i + 1
            try:
                emails = re.findall(r"[a-zA-Z0-9\.\-+_]+@[a-zA-Z0-9\.\-+_]+\.[a-zA-Z]+", mail)
                for m in emails:
                    file.writelines(m.lower() + '\n')
            except Exception as e:
                print(f"Exception {e} occured on member {i} who probably has no mail adress: {mail}")
        file.close()


    def return_months(self, start, end):
        sm  = start.month
        sy = start.year
        em  = end.month
        ey = end.year
        months = []
        m = []
        for y in range(sy, ey):
            if y == sy:
                m = [range(sm, 12)]
            if y == ey:
                m = [range(em, 12)]
            else:
                m = [range(1, 12)]
            if months is None:
                months = m

            months = months.append(m)

        return months


    def get_date_summer(self, today: date) -> date:
        # Sommer Start: 01. Mai
        year = today.year if (today.month < date(year=2020, month=5, day=1).month) else today.year + 1
        return date(year=year, month=5, day=1)


    def get_date_winter(self, today: date) -> date:
        # Sommer Start: 01. November
        year = today.year if (today.month < date(year=2020, month=11, day=1).month) else today.year + 1
        return date(year=year, month=11, day=1)


    def write_to_file(self, output_file: str) -> None:
        # write to file
        with open(output_file, 'w') as f:
            f.write('# Aktuelle Solawi Teilnehmer und Anteile\n\n')
            f.write('__Diese Datei wird automatisch erstellt. Alle Angaben momentan ohne Gewähr!__\n\n')
            f.write(f'Stichtag: {self.stichtag}\n\n')
            f.write('| Bezeichnung | Teilnehmer | Anteile | \n')
            f.write('| --- | --- | --- | \n')
            f.write(('| Sommer | %i | %i | \n') % (self.teilnehmer_data["s_teilnehmer"], self.teilnehmer_data["s_anteile"]))
            f.write(('| Winter | %i | %i | \n') % (self.teilnehmer_data["w_teilnehmer"], self.teilnehmer_data["w_anteile"]))
            f.write(('| Eier | %i | %i | \n') % (self.teilnehmer_data["e_teilnehmer"], self.teilnehmer_data["e_anteile"]))
            f.write(('| Käse | %i | %i | \n') % (self.teilnehmer_data["k_teilnehmer"], self.teilnehmer_data["k_anteile"]))
            f.write(('| Brot | %i | %i | \n') % (self.teilnehmer_data["b_teilnehmer"], self.teilnehmer_data["b_anteile"]))
            f.write(('\n'))
            f.write('## Aktualisieren der aktuellen Teilnehmerdaten\n\n')
            f.write(('Die Tabelle mit den Teilnehmerzahlen und den Anteilen wird in etwa jede Stunde von der Datei `.s-verein-export.csv` erstellt. Sie kann nicht manuell erstellt werden. Die `csv` Datei ist ein Export der S-Verein Liste *Gesamt-Skript*.\n'))
            f.write(('Um die Daten zu aktualisieren muss:\n\n1. Ein Export der Liste in S-Verein erstellt werden\n2. Die Liste muss in `.s-verein-export.csv` umbenannt werden\n3. Die umbenannte Liste muss in diesen Ordner geladen werden\n\n'))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Solawi Teilnehmerauswertung von SVerein Export')
    parser.add_argument('abteilungen', metavar='Abteilugstabelle', type=str,
                        help='Pfad zur Abteilungs CSV-Datei')
    parser.add_argument('teilnehmer', metavar='Teilnehmertabelle', type=str,
                        help='Pfad zur Teilnehmer CSV-Datei')
    parser.add_argument('bericht', metavar='Pfad zum Bericht', type=str,
                        help='Pfad zum erzeugtem Bericht')
    parser.add_argument('stichtag', metavar='Stichtag', type=str,
                        help='Datum, zu welchem der Bericht erzeugt werden soll im Format: yyyy-mm-dd')
    parser.add_argument('--plot', metavar='Plot', type=bool, default=False,
                        help='Option, um die Ernteanteile über die Zeit zu plotten [true, false]')


    args = parser.parse_args()

    out_file = args.bericht
    in_mitglieder_file = args.teilnehmer
    in_abteilungen_file = args.abteilungen
    stichtag = args.stichtag
    d = DataEvaluation(in_abteilungen_file, in_mitglieder_file, out_file, stichtag)
    d.write_to_file(out_file)
    print("Exit with Success!")

    # PLOT data

    if args.plot:

        import matplotlib.pyplot as plt
        dates = ['2018-05-01',
                '2018-11-01',
                '2019-05-01',
                '2019-11-01',
                '2020-05-01',
                '2020-11-01',
                '2021-05-01',
                '2021-11-01',
                '2022-05-01',
                '2022-11-01',
                '2023-05-01',
                '2023-11-01']

        sommer = []
        winter = []
        for d in dates:
            deval = DataEvaluation(in_abteilungen_file, in_mitglieder_file, out_file, d)
            sommer.append(deval.teilnehmer_data["s_anteile"])
            winter.append(deval.teilnehmer_data["w_anteile"])

        fig, ax = plt.subplots()
        ax.plot(dates, sommer, label='Sommer Anteile')
        ax.plot(dates, winter, label='Winter Anteile')

        ax.set_xlabel("Datum")
        ax.set_ylabel("Anteile")
        ax.legend()
        plt.xticks(rotation=45)
        plt.grid()
        plt.show()
