import sys
import os
import re
from logging import DEBUG, getLogger, StreamHandler
import pandas as pd
import numpy as np
from datetime import date
from datetime import datetime
from dateutil.parser import parse
import argparse
import matplotlib.pyplot as plt
from typing import List, Tuple



from solawi_teilnehmer_auswertung.teilnehmer import Teilnehmer, MembershipType


logger = getLogger("topic_cluster")


class DataEvaluation:

    teilnehmer_data = {}
    in_abteilungen_file = ""
    in_mitglieder_file = ""
    output_file = ""
    teilnehmer: List[Teilnehmer] = None
    stichtag: date = None


    def __init__(self, in_abteilungen_file, in_mitglieder_file, out_path, stichtag):

        # define input and output file names
        self.in_abteilungen_file = in_abteilungen_file
        self.in_mitglieder_file = in_mitglieder_file
        self.output_file = out_path
        self.stichtag = parse(stichtag).date()

        logger.info(f"Teilnehmer Auswertung für Stichtag: {self.stichtag}")


        self.parse_data()

    
    def set_stichtag(self, stichtag):
        self.stichtag = parse(stichtag).date()


    def write_mailing_lists_to_file(self):
        now = datetime.now()
        today_str = now.strftime("%Y%m%d")
        os.makedirs(today_str, exist_ok=True)

        mails_all = self.get_mails_of_memberships([
            MembershipType.ORGA_WINTER, 
            MembershipType.ORGA_SOMMER,
            MembershipType.SOMMER,
            MembershipType.WINTER,
            MembershipType.EIER,
            MembershipType.BROT,
            MembershipType.KASE,
            MembershipType.OBST,
            ])
        mails_winter = self.get_mails_of_memberships([MembershipType.WINTER])
        mails_sommer = self.get_mails_of_memberships([MembershipType.SOMMER])
        mails_brot = self.get_mails_of_memberships([MembershipType.BROT])
        mails_eier = self.get_mails_of_memberships([MembershipType.EIER])
        mails_kase = self.get_mails_of_memberships([MembershipType.KASE])

        mail_left = self.get_left_solawis()
        mail_left = self.clean_left_list(mail_left, mails_all)

        self.write_mail_to_file(mails_all, '/mails_all.txt', today_str)
        self.write_mail_to_file(mail_left, '/ausgetretene_mitglieder.txt', today_str)
        self.write_mail_to_file(mails_winter, '/winter-mail.txt', today_str)
        self.write_mail_to_file(mails_sommer, '/sommer-mail.txt', today_str)
        self.write_mail_to_file(mails_eier, '/eier-mail.txt', today_str)
        self.write_mail_to_file(mails_kase, '/kase-mail.txt', today_str)
        self.write_mail_to_file(mails_brot, '/brot-mail.txt', today_str)


    def parse_data(self) -> None:
        # open file exported from s-verein
        try:
            logger.info("Reading %s" % self.in_abteilungen_file)
            table_abteilungen = pd.read_csv(self.in_abteilungen_file, sep=";")#, on_bad_lines='warn')
        # except if file is not found and write error message to file
        except FileNotFoundError:
            logger.error("Cannot find file named %s" % self.in_abteilungen_file)
            with open(self.output_file, 'w') as f:
                f.write('__Fehler: kann Datei %s nicht finden.__' % self.in_abteilungen_file)
            exit(1)
        # except all other errors
        except Exception as e:
            logger.error(f"{e}")
            exit(1)

        # open file exported from s-verein
        try:
            logger.info("Reading %s" % self.in_mitglieder_file)
            table_mitglieder = pd.read_csv(self.in_mitglieder_file, sep=';')#, on_bad_lines='warn')
        # except if file is not found and write error message to file
        except FileNotFoundError:
            logger.error("[Error] Cannot find file named %s" % self.in_mitglieder_file)
            with open(self.output_file, 'w') as f:
                f.write('__Fehler: kann Datei %s nicht finden.__' % self.in_mitglieder_file)
            exit(1)
        # except all other errors
        except Exception as e:
            logger.error(f"{e}")
            exit(1)

        today = date.today()
        date_sommer = self.get_date_summer(self.stichtag)
        date_winter = self.get_date_winter(self.stichtag)

        t_abteilungen = table_abteilungen.filter(items=
            ['Mitglieds-Nr',
            'Abteilungsbezeichnung',
            'Beitragsbezeichnung',
            'Abteilungseintritt',
            'Abteilungsaustritt', 
            'Beitragsaustritt'])
        t_mitglieder = table_mitglieder.filter(items=
            ['Mitglieds-Nr',
            'E-Mail',
            'Nachname',
            'Vorname',
            'PLZ'])

        # filter die Beitragsbezeichnungen
        beitragsbez = t_abteilungen['Beitragsbezeichnung'].unique()
        map_dict = {}

        # Map Strings der Beitragsbezeichnung auf Integer Werte
        for b in beitragsbez:
            if isinstance(b, float):
                b = '1'
            amount = [float(i) for i in b.split() if i.isdigit()]
            map_dict[b] = float(amount[0]) if amount else float(1)

        t_abteilungen['Beitragsbezeichnung'] = t_abteilungen['Beitragsbezeichnung'].map(map_dict).astype(float)

        # filter out asteriks and convert to integure
        for i, m in enumerate(t_mitglieder['Mitglieds-Nr']):
            number = [j for j in m.split() if j.isdigit()]
            t_mitglieder.loc[i, 'Mitglieds-Nr'] = number[0]

        t_mitglieder['Mitglieds-Nr'] = t_mitglieder['Mitglieds-Nr'].astype(int)
        
        # convert string to datetime
        for i, d in enumerate(t_abteilungen['Abteilungsaustritt']):
            if not isinstance(d, float):
                t_abteilungen.loc[i, 'Abteilungsaustritt'] = datetime.strptime(d, '%d.%m.%Y').date()

            # if no date is available, set date to start of next term
            else:
                t_abteilungen.loc[i, 'Abteilungsaustritt'] = date_winter if t_abteilungen.loc[i, 'Abteilungsbezeichnung'] == 'Winter' else date_sommer


        for i, d in enumerate(t_abteilungen['Beitragsaustritt']):
            if not isinstance(d, float):
                t_abteilungen.loc[i, 'Beitragsaustritt'] = datetime.strptime(d, '%d.%m.%Y').date()

            # if no date is available, set date to start of next term
            else:
                t_abteilungen.loc[i, 'Beitragsaustritt'] = date_winter if t_abteilungen.loc[i, 'Abteilungsbezeichnung'] == 'Winter' else date_sommer



        # derive dataclass and create dataframe

        self.teilnehmer_data = list()

        for idx in t_mitglieder.index:

            # Get mail addresses from datapoint
            mails = t_mitglieder['E-Mail'][idx]
            # create new dataclass instance for each teilnehmer
            t = Teilnehmer(
                id=t_mitglieder['Mitglieds-Nr'][idx],
                name=t_mitglieder['Vorname'][idx] + ' ' + t_mitglieder['Nachname'][idx],
                postal_code=t_mitglieder['PLZ'][idx]
            )
            t.add_memberships(t_abteilungen)
            t.add_mails(mails)

            self.teilnehmer_data.append(t)


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
                logger.error(f"Exception {e} occured on member {i} who probably has no mail adress: {mail}")
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


    def write_amout_data_to_file(self, output_file: str) -> None:
        # write to file
        with open(output_file, 'w') as f:
            f.write('# Aktuelle Solawi Teilnehmer und Anteile\n\n')
            f.write('__Diese Datei wird automatisch erstellt. Alle Angaben momentan ohne Gewähr!__\n\n')
            f.write(f'Stichtag: {self.stichtag}\n\n')
            f.write('| Bezeichnung | Teilnehmer | Anteile | \n')
            f.write('| --- | --- | --- | \n')
            f.write(('| Sommer | %i | %.1f | \n') % (self.get_amount_of_membership(MembershipType.SOMMER)))
            f.write(('| Winter | %i | %.1f | \n') % (self.get_amount_of_membership(MembershipType.WINTER)))
            f.write(('| Eier | %i | %.1f | \n') % (self.get_amount_of_membership(MembershipType.EIER)))
            f.write(('| Käse | %i | %.1f | \n') % (self.get_amount_of_membership(MembershipType.KASE)))
            f.write(('| Brot | %i | %.1f | \n') % (self.get_amount_of_membership(MembershipType.BROT)))
            f.write(('\n'))
            f.write('## Aktualisieren der aktuellen Teilnehmerdaten\n\n')
            f.write(('Die Tabelle mit den Teilnehmerzahlen und den Anteilen wird in etwa jede Stunde von der Datei `.s-verein-export.csv` erstellt. Sie kann nicht manuell erstellt werden. Die `csv` Datei ist ein Export der S-Verein Liste *Gesamt-Skript*.\n'))
            f.write(('Um die Daten zu aktualisieren muss:\n\n1. Ein Export der Liste in S-Verein erstellt werden\n2. Die Liste muss in `.s-verein-export.csv` umbenannt werden\n3. Die umbenannte Liste muss in diesen Ordner geladen werden\n\n'))


    def get_amount_of_membership(self, mt: MembershipType) -> Tuple[int, float]:
        """
        for type t on date d
        """

        teilnehmer = 0
        amount = 0.0
        for member in self.teilnehmer_data:
            for membership in member.memberships:
                if membership.membership_type == mt:
                    if membership.start <= self.stichtag and self.stichtag < membership.end:
                        amount = amount + membership.amount
                        teilnehmer = teilnehmer + 1

        return (teilnehmer, amount)

    def get_mails_of_memberships(self, mt: List[MembershipType], sorted=False) -> List[str]:

        mails = list()
        for member in self.teilnehmer_data:
            for membership in member.memberships:
                if membership.membership_type in mt:
                    if membership.start <= self.stichtag and self.stichtag < membership.end:
                        if member.mails is not None :
                            mails.extend(member.mails)
                        break
        if sorted:
            mails.sort()
        return mails


    def get_left_solawis(self, sorted=False) -> List[str]:

        mails = list()
        for member in self.teilnehmer_data:
            left = False
            for membership in member.memberships:
                if membership.end <= self.stichtag:
                    left = True
                else:
                    left = False

            if left and member.mails is not None:
                mails.extend(member.mails)

        if sorted:
            mails.sort()
        return mails

    def clean_left_list(self, left: List[str], right: List[str], sorted=False) -> List[str]:
        """
        merge right list in left list
        """

        new_left = list()

        for l in left:
            if l not in right:
                new_left.extend(l)

        if sorted:
            new_left.sort()
        return new_left



def plot_analysis() -> None:
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
        deval.set_stichtag(d)
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


def main(
    in_abteilungen_path: str,
    in_teilnehmer_path: str,
    out_bericht_path: str,
    stichtag: str,
    plot: bool = False,
    ) -> None:

    logger.debug(
        f"Creating analysis from files: {in_abteilungen_path} and {in_teilnehmer_path}")

    d = DataEvaluation(
        in_abteilungen_path,
        in_teilnehmer_path,
        out_bericht_path,
        stichtag)

    d.write_amout_data_to_file(out_bericht_path)
    d.write_mailing_lists_to_file()

    if plot:
        plot_analysis()




if __name__ == "__main__":

    out_file = "output.md"
    in_mitglieder_file = "teilnehmer.csv"
    in_abteilungen_file = "abteilungen.csv"
    stichtag = "2022-11-01"
    main(in_abteilungen_file, in_mitglieder_file, out_file, stichtag)
    logger.info("Exit with Success!")
