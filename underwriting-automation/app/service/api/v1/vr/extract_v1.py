import asyncio
import re

import fitz

from app import logger
from app.business_rule_exception import InvalidPDFStructureTypeException
from app.constant import VRDocumentTemplate
from app.service.helper import parser


class VRDataPointExtractorV1():
    def __init__(self, uuid, file):
        self.uuid = uuid
        self.file = file
        self.doc = fitz.open(stream=self.file, filetype="pdf")
        self.doc_text = ''
        for page in self.doc:
            self.doc_text = self.doc_text + page.get_text()
        self.doc_text = self.doc_text.replace('\n', ' ')
        self.indexof = {x: re.search(x, self.doc_text).start() for x in VRDocumentTemplate.TITLES if
                        x in self.doc_text}

    async def __get_substring_by_words(self, start, end):
        value = None
        end = end if end else -1
        if start and self.indexof[start] < self.indexof[end]:
            value = self.doc_text[self.indexof[start]:self.indexof[end]].replace(start, '').strip()
            value = int(value) if value and value.isdigit() else value
        return value

    async def __extract_vehicle_info(self):
        vehicle = None
        try:
            vin = await self.__get_substring_by_words(VRDocumentTemplate.VIN, VRDocumentTemplate.PLATE)
            make = await self.__get_substring_by_words(VRDocumentTemplate.MAKE, VRDocumentTemplate.STYLE)
            year = await self.__get_substring_by_words(VRDocumentTemplate.YEAR, VRDocumentTemplate.MODEL)
            if vin and make and year:
                vehicle = {'vin': vin, 'model': None, 'make': make, 'year': year}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
            vehicle = None
        return vehicle

    async def __extract_owners_name(self):
        owners_name = None
        try:
            extracted_name = await self.__get_substring_by_words(VRDocumentTemplate.REG_OWNER,
                                                                 VRDocumentTemplate.LEGAL_OWNER)
            if extracted_name:
                owners_name = []
                match = re.search(VRDocumentTemplate.RegexCollection.LEASED_VEH_OWNER, extracted_name)
                names = match.group(1) if match else extracted_name
                names = parser.parse_multiple_names(names)
                for extracted_name in names:
                    owners_name.append(extracted_name.strip())
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
        return owners_name

    async def extract(self):
        data = {"vr": None}
        if VRDocumentTemplate.CHECK_VALID_DOCUMENT in self.doc_text:
            vehicle_info, owner_name = await asyncio.gather(self.__extract_vehicle_info(), self.__extract_owners_name())
            data['vr'] = {'owners': owner_name if owner_name else None, 'vehicle': vehicle_info}
        else:
            logger.warning(f'Request ID: [{self.uuid}] ')
            raise InvalidPDFStructureTypeException(self.uuid)
        logger.info(f'Request ID: [{self.uuid}] Response: {data}')

        return data
