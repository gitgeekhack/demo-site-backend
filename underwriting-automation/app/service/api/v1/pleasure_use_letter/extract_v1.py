import asyncio
import re

import fitz
from fuzzywuzzy import fuzz

from app import logger
from app.business_rule_exception import InvalidPDFStructureTypeException
from app.constant import PleasureUseLetterTemplate, InsuranceCompany
from app.service.api.v1.signature.validate_signature_v1 import ValidateSignatureV1
from app.service.helper.pdf_helper import PDFHelper


class PULDataPointExtractorV1():
    def __init__(self, uuid, file):
        self.uuid = uuid
        self.file = file
        self.doc = fitz.open(stream=self.file, filetype="pdf")
        self.pdf_helper = PDFHelper(self.doc)
        self.signature_validator = ValidateSignatureV1()

    async def __check_token_set_ratio(self, x, y):
        if x and y:
            if fuzz.token_set_ratio(x, y) == 100:
                return True
            return False
        return None

    async def __get_company(self, name):
        extracted_name = company_name = None
        for x in InsuranceCompany.items():
            for y in name:
                if await self.__check_token_set_ratio(x, y):
                    company_name, extracted_name = InsuranceCompany.ALLIANCE_UNITED.value, y
        return company_name, extracted_name

    async def __get_company_and_insured_name(self, text):
        company_name = insured_name = None
        if text:
            name = [x for x in text if x != '' and all(chr.isalpha() or chr.isspace() for chr in x)]
            company_name, extracted_name = await self.__get_company(name)
            if extracted_name:
                name.remove(extracted_name)
            if len(name) == 1:
                insured_name = name[0]
        return company_name, insured_name

    async def __get_policy_number(self, text):
        for x in text:
            if len(x.split()) == 1 and x.isalnum():
                return x
        return None

    async def __get_vehicle_info(self, text):
        information = []
        vehicles = None
        for x in text:
            if ',' in x:
                y = x.split(',')
                text.remove(x)
                text.extend(y)
        for x in text:
            match = re.match(PleasureUseLetterTemplate.RegexCollection.VEHICLE_INFORMATION, x.strip())
            if match:
                x = match.group()
                information.append(x)
        if information:
            vehicles = []
            vehicle_info = [x for x in information if len(x.split()) > 2]
            for x in vehicle_info:
                info = x.split()
                vin = info[-1] if len(info[-1]) == 17 else None
                info.remove(vin) if vin else None
                model_info = info[2:]
                model = ' '.join(map(str, model_info))
                vehicles.append({'year': int(info[0]),
                                 'make': info[1],
                                 'model': model,
                                 'vin': vin})
        return vehicles

    async def __get_signature(self):
        signature = None
        try:
            page_number = await self.pdf_helper.find_page_by_text(PleasureUseLetterTemplate.PLEASURE_USE_LETTER)
            page_number = page_number[0]
            bboxes = await self.pdf_helper.get_bbox_by_text(text=PleasureUseLetterTemplate.INSURED_SIGNATURE,
                                                            page_no=page_number)
            if bboxes:
                signature_placeholder_bbox = bboxes[0][0]
                x0, y0, x1, y1 = PleasureUseLetterTemplate.PADDING
                bbox = await self.pdf_helper.apply_bbox_padding(page_no=page_number, bbox=signature_placeholder_bbox,
                                                                x0_pad=x0, y0_pad=y0, x1_pad=x1, y1_pad=y1)
                page_signatures = await self.pdf_helper.get_images_by_page(page_no=page_number)
                is_signed = await self.signature_validator.validate(doc=self.pdf_helper.converted_doc,
                                                                    section_bbox=bbox,
                                                                    images=page_signatures,
                                                                    page=self.pdf_helper.converted_doc[page_number])
                signature = {'is_signed': is_signed}
        except IndexError as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            signature = None
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            signature = None
        return signature

    async def extract(self):
        data = {"pleasure_use_letter": None}
        page = self.doc[0]
        blocks = page.get_text().split('\n')
        if await self.pdf_helper.find_page_by_text(PleasureUseLetterTemplate.PLEASURE_USE_LETTER):
            temp = blocks.index(PleasureUseLetterTemplate.TEMPLATE_DELIMINATOR)
            text = blocks[temp + 1:]
            (company_name, insured_name), policy_number, vehicles, signature = await asyncio.gather(
                self.__get_company_and_insured_name(text), self.__get_policy_number(text),
                self.__get_vehicle_info(text),
                self.__get_signature())

            pleasure_use_letter = {'company_name': company_name, 'customer_name': insured_name,
                                   'policy_number': policy_number, 'vehicles': vehicles,
                                   'signature': signature}
            data['pleasure_use_letter'] = pleasure_use_letter
        else:
            logger.warning(f'Request ID: [{self.uuid}] ')
            raise InvalidPDFStructureTypeException(self.uuid)
        logger.info(f'Request ID: [{self.uuid}] Response: {data}')

        return data
