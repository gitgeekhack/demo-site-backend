import fitz
from fuzzywuzzy import fuzz

from app import logger
from app.business_rule_exception import InvalidPDFStructureTypeException
from app.constant import NonOwnersLetter, PDF, InsuranceCompany
from app.service.api.v1.signature.validate_signature_v1 import ValidateSignatureV1
from app.service.helper.pdf_helper import PDFHelper


class NOLDataPointExtractorV1:
    def __init__(self, uuid, file):
        self.uuid = uuid
        self.signature_validator = ValidateSignatureV1()
        self.file = file
        self.doc = fitz.open(stream=self.file, filetype="pdf")
        self.section = NonOwnersLetter.Sections
        self.response_key = NonOwnersLetter.ResponseKey
        self.pdf_helper = PDFHelper(self.doc)
        self.page = self.doc[self.section.PAGE_NO]
        self.page_text = self.page.get_text().replace('\n', ' ')

    async def __get_data(self):
        _data = []
        data = [x[PDF.TEXT].replace('_', '') for x in self.pdf_helper.metadata]
        index = data.index(self.section.VALID_KEY)
        data = data[:index] if index else _data
        data = [x for x in data if x not in self.section.ALLOWED_KEY]
        return data

    async def __check_token_set_ratio(self, x, y):
        if x and y:
            if fuzz.token_set_ratio(x, y) == self.section.SORT_SIMILARITY_RATIO:
                return True
            return False
        return None

    async def __get_company_name(self, data):
        extracted_name = company_name = None
        for x in InsuranceCompany.items():
            for y in data:
                if await self.__check_token_set_ratio(x, y):
                    company_name, extracted_name = InsuranceCompany.ALLIANCE_UNITED.value, y
        return company_name, extracted_name

    async def __get_insured_name(self, data):
        name = None
        for i_data in data:
            _data = i_data.replace(' ', '')
            if _data.isalpha():
                return i_data
        return name

    async def __check_contains_letter_and_number(self, data):
        return data.isalnum() and not data.isalpha()

    async def __get_policy_number(self, data):
        number = None
        for i_data in data:
            _data = ''.join(filter(str.isalnum, i_data))
            if await self.__check_contains_letter_and_number(_data):
                return i_data
        return number

    async def __get_info(self, data):
        company_name, extracted_name = await self.__get_company_name(data)
        if extracted_name:
            data.remove(extracted_name)
        insured_name = await self.__get_insured_name(data)
        policy_number = await self.__get_policy_number(data)
        return insured_name, company_name, policy_number

    async def __get_signature(self):
        signature = None
        try:
            signature_placeholder = await self.pdf_helper.get_bbox_by_text(self.section.SIGNATURE_SEARCH_KEY,
                                                                           page_no=self.section.PAGE_NO)
            if signature_placeholder:
                x0, y0, x1, y1 = signature_placeholder[0][0]
                x1 = x1 // 1.55
                bbox = (x0, y0, x1, y1)
                sign_x0, sign_y0, sign_x1, sign_y1 = self.section.PADDING
                bbox = await self.pdf_helper.apply_bbox_padding(page_no=self.section.PAGE_NO,
                                                                bbox=bbox,
                                                                x0_pad=sign_x0, y0_pad=sign_y0,
                                                                x1_pad=sign_x1, y1_pad=sign_y1)
                signatures = await self.pdf_helper.get_images_by_page(page_no=self.section.PAGE_NO)
                is_signed = await self.signature_validator.validate(self.pdf_helper.converted_doc,
                                                                    bbox, signatures,
                                                                    self.pdf_helper.converted_doc[self.section.PAGE_NO])
                signature = {'is_signed': is_signed}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
            signature = None
        return signature

    async def extract(self):
        data = {self.response_key.NON_OWNERS_LETTER: None}
        if self.section.VALID_KEY in self.page_text:
            metadata = await self.__get_data()
            insured_name, company_name, policy_number = await self.__get_info(metadata)
            signature = await self.__get_signature()
            data[self.response_key.NON_OWNERS_LETTER] = {self.response_key.INSURED_NAME: insured_name,
                                                         self.response_key.POLICY_NUMBER: policy_number,
                                                         self.response_key.COMPANY_NAME: company_name,
                                                         self.response_key.SIGNATURE: signature}
        else:
            logger.warning(f'Request ID: [{self.uuid}] ')
            raise InvalidPDFStructureTypeException(self.uuid)
        print(f'Request ID: [{self.uuid}] Response: {data}')

        return data
