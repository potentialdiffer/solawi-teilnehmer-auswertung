from enum import Enum, auto
from typing import List
from dataclasses import dataclass
from datetime import date
from dateutil.parser import parse
import re
import pandas as pd
from pandas import DataFrame as df
import numpy as np
from logging import DEBUG, getLogger, StreamHandler

from solawi_teilnehmer_auswertung.location import TeilnehmerLocation

logger = getLogger("solawi_teilnehmer_auswertung")

locator = TeilnehmerLocation()

class MembershipType(Enum):
    SOMMER = 'Sommer'
    ORGA_SOMMER = 'Orga Sommer'
    WINTER = 'Winter'
    ORGA_WINTER = 'Orga Winter'
    BROT = 'Brot'
    EIER = 'Eier'
    KASE = 'Käse'
    AKTION = 'Aktionen'
    OBST = 'Obst'


@dataclass
class Membership:
    membership_type: MembershipType
    start: date
    end: date
    amount: int


@dataclass
class Teilnehmer:
    id: int
    name: str
    mails: List[str] = None
    memberships: List[Membership] = None
    postal_code: int = None
    location: str = None


    def __post_init__(self) -> None:
        self.memberships = list()
        self.location = locator.get_location(self.postal_code)


    def add_memberships(self, abteilungen: df) -> None:
        for idx in abteilungen.index:
            if self.id == abteilungen['Mitglieds-Nr'][idx]:
                if abteilungen['Beitragsbezeichnung'][idx] != abteilungen['Beitragsbezeichnung'][idx]:
                    continue
                self.add_membership(
                    abteilungen['Abteilungsbezeichnung'][idx],
                    parse(abteilungen['Abteilungseintritt'][idx]).date(),
                    self.get_earlier_date(
                        abteilungen['Beitragsaustritt'][idx], 
                        abteilungen['Abteilungsaustritt'][idx]),
                    abteilungen['Beitragsbezeichnung'][idx],
                )

    def get_earlier_date(self, a, b) -> date:
        return a if a < b else b


    def add_membership(self, membership_type: MembershipType, start: date, end: date, amount: int) -> None:
        self.memberships.append(
            Membership(MembershipType(membership_type), start, end, amount)
        )


    def add_mails(self, mails) -> None:
        try:
            self.mails = re.findall(r"[a-zA-Z0-9\.\-+_]+@[a-zA-Z0-9\.\-+_]+\.[a-zA-Z]+", mails)
        except Exception as e:
            logger.error(f"{e}: On member {self.name} who probably has no mail address: {mails}")