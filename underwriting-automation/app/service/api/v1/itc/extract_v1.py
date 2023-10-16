import fitz

from app import logger
from app.business_rule_exception import InvalidPDFStructureTypeException
from app.service.api.v1.itc.extractor_v1 import Type1Extractor, Type2Extractor, Type3Extractor, Type4Extractor


class ITCDataPointExtractorV1():
    def __init__(self, uuid, file):
        self.uuid = uuid
        self.file = file
        self.doc = fitz.open(stream=self.file, filetype="pdf")

    async def __extract_by_type(self, doc):
        data = {}
        try:
            page = doc[0]
            blocks = page.get_text("dict")['blocks']
            length_blocks = len(blocks)
            if 5 < length_blocks < 9:
                type1 = Type1Extractor(uuid=self.uuid, doc=doc)
                data = await type1.extract()
            elif length_blocks == 17:
                type2 = Type2Extractor(uuid=self.uuid, doc=doc)
                data = await type2.extract()
            elif length_blocks >= 40:
                type3 = Type3Extractor(uuid=self.uuid, doc=doc)
                data = await type3.extract()
            elif 11 <= length_blocks < 25:
                type4 = Type4Extractor(uuid=self.uuid, doc=doc)
                data = await type4.extract()
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            raise InvalidPDFStructureTypeException(self.uuid)
        return data

    async def extract(self):
        data = {"itc": None}
        data['itc'] = await self.__extract_by_type(self.doc)
        logger.info(f'Request ID: [{self.uuid}] Response: {data}')

        return data
