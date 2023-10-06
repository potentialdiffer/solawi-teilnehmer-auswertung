import pgeocode
from typing import List
from logging import DEBUG, getLogger, StreamHandler

logger = getLogger("solawi_teilnehmer_auswertung")


class TeilnehmerLocation:

    nomi = None


    def __init__(self):
        self.nomi = pgeocode.Nominatim('de')


    def get_location(self, postal_code: int) -> str:
        location = self.nomi.query_postal_code(str(postal_code)).place_name
        if location != location:
            logger.error(f'postal_code {postal_code} is nan')

        return location

    def get_locations(self, postal_codes: List[int]) -> List[str]:
        locations: List[str] = []

        for code in postal_codes:
            location = self.get_location(code)
            if location not in locations:

                locations.append(location)
        
        return locations


