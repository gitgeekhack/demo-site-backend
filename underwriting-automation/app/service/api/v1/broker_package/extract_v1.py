import fitz

from app import logger
from app.business_rule_exception import InvalidPDFStructureTypeException
from app.constant import BrokerPackageTemplate
from app.service.api.v1.broker_package.extractor_v1 import Template1Extractor, Template2Extractor


class BrokerPackageDataPointExtractorV1():

    def __init__(self, uuid, file):
        self.uuid = uuid
        self.file = file
        self.doc = fitz.open(stream=self.file, filetype="pdf")
        self.constants = BrokerPackageTemplate

    async def __extract_by_type(self):
        data = {}
        page = self.doc[0]
        page_text = page.get_text()
        if self.constants.VALID_BROKER_PACKAGE_TEMPLATE in page_text:
            if self.constants.VALID_TYPE_2 in page_text:
                type2 = Template2Extractor(uuid=self.uuid, doc=self.doc)
                data = await type2.extract()
            else:
                type1 = Template1Extractor(uuid=self.uuid, doc=self.doc)
                data = await type1.extract()
        else:
            logger.warning(f'Request ID: [{self.uuid}] ')
            raise InvalidPDFStructureTypeException(self.uuid)
        return data

    async def extract(self):
        data = {"broker_package": None}
        data['broker_package'] = await self.__extract_by_type()
        print(f'Request ID: [{self.uuid}] Response: {data}')
        return data
