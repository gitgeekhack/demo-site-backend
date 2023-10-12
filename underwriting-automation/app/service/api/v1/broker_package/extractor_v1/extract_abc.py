import abc
from datetime import datetime

from app import logger
from app.constant import BrokerPackageTemplate
from app.service.api.v1.signature.validate_signature_v1 import ValidateSignatureV1
from app.service.helper import pdf_helper


class BrokerPackageExtractABC():
    __metaclass__ = abc.ABCMeta

    def __init__(self, uuid, doc):
        self.uuid = uuid
        self.doc = doc
        self.signature_validator = ValidateSignatureV1()

        self.response_key = BrokerPackageTemplate.ResponseKey
        self.pdf_helper = pdf_helper.PDFHelper(self.doc)

    async def is_valid_month(self, month):
        try:
            if month.isalpha():
                if month in BrokerPackageTemplate.SPANISH_MONTHS:
                    month = BrokerPackageTemplate.SPANISH_MONTHS[month]
                month = (datetime.strptime(month[:3], '%b').month if month.isalpha() else None)
            month = int(month)
        except ValueError:
            month = None
            logger.warning(f'Request ID: [{self.uuid}] -> Invalid Month number')
        return month
