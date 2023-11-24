import csv
from app.common.utils import MonoState
from app.constant import DrivingLicenseParser
from app.service.helper.certificate_of_title_parser import parse_title_number, parse_vin, parse_year, parse_address


def load_us_cities():
    with open(DrivingLicenseParser.WORLD_CITIES_LIST, newline='') as csvfile:
        reader = csv.reader(csvfile)
        us_cities = [row[0] for row in reader if row[4] == 'United States']
    return us_cities


class CertificateOfTitleOCR(MonoState):
    _internal_state = {'us_cities': load_us_cities()}

    def get_address(self, text):
        address = parse_address(text, cities=self.us_cities)
        return address
