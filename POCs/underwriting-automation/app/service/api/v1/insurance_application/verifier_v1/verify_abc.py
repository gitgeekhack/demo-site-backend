import abc
from datetime import datetime

from fuzzywuzzy import fuzz

from app.constant import VerificationTemplate, ISO_DATE_FORMAT


class VerifyABC():
    __metaclass__ = abc.ABCMeta

    def __init__(self, uuid, data):
        self.uuid = uuid
        self.data = data

    @abc.abstractmethod
    async def validate(self, *args, **kwargs):
        """Required method"""

    async def is_equal_date(self, x, y):
        try:
            return datetime.strptime(x, ISO_DATE_FORMAT) == datetime.strptime(y, ISO_DATE_FORMAT)
        except Exception:
            return False

    async def is_equal(self, x, y):
        if x and y:
            if str(x).isdigit() and str(y).isdigit(): return x == y
            if await self.is_equal_date(x, y): return True
            if fuzz.token_sort_ratio(x, y) == VerificationTemplate.SORT_SIMILARITY_RATIO: return True
            return False
        return None

    async def is_subset(self, x, y):
        if x and y:
            if fuzz.token_set_ratio(x, y) == VerificationTemplate.SET_SIMILARITY_RATIO:
                return True
            return False
        return None

    async def get_object_by_id(self, document, object_id):
        if document:
            for obj in document:
                if obj.id == object_id:
                    return obj
        return None

    async def get_driver_with_lic_no(self, document, license_number):
        if document and license_number:
            for driver in document:
                if driver and await self.is_equal(driver.license_number, license_number):
                    return driver
        return None

    async def get_insured_dl_by_license_number(self, application, driving_licenses):
        insured_app = await self.get_object_by_id(application.driver_information.drivers, 1)
        insured_dl = None
        if insured_app:
            insured_dl = await self.get_driver_with_lic_no(driving_licenses, insured_app.license_number)
        return insured_dl

    async def get_insured_mvr_by_license_number(self, insured_dl, mvrs):
        insured_mvr = None
        if insured_dl:
            insured_mvr = await self.get_driver_with_lic_no(mvrs, insured_dl.license_number)
        return insured_mvr
