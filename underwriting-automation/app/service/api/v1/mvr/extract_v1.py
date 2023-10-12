import asyncio
import re

import fitz

from app import logger
from app.business_rule_exception import InvalidPDFStructureTypeException
from app.constant import MVRDocumentTemplate, LicenseStatus
from app.service.api.v1.signature.validate_signature_v1 import ValidateSignatureV1
from app.service.helper.cv_helper import CVHelper
from app.service.helper.parser import parse_date, parse_gender
from app.service.helper.pdf_helper import PDFHelper


class MVRDataPointExtractorV1():
    def __init__(self, uuid, file):
        self.uuid = uuid
        self.file = file
        self.doc = fitz.open(stream=self.file, filetype="pdf")
        self.pdf_helper = PDFHelper(self.doc)
        self.signature_validator = ValidateSignatureV1()
        self.cv_helper = CVHelper()

    async def __get_license_number(self, blocks):
        license_number = None
        for lines in blocks:
            text = lines[4]
            if text.startswith(MVRDocumentTemplate.LICENSE):
                license_number = text.replace(MVRDocumentTemplate.LICENSE, '').strip()
                break
        return license_number

    async def __get_license_status(self, page):
        line = page.get_textpage().extractText()
        wordlist = ['License and Permit Information', 'Miscellaneous State Data']

        license_info = line[line.index(wordlist[0]):line.index(wordlist[1])]
        license_type = re.findall(MVRDocumentTemplate.RegexCollection.LICENSE, license_info)
        status_list = re.findall(MVRDocumentTemplate.RegexCollection.STATUS, license_info)
        license_status_dict = dict(zip(license_type, status_list))
        status = None
        if MVRDocumentTemplate.LicenseType.PERSONAL in license_status_dict.keys():
            status = license_status_dict[MVRDocumentTemplate.LicenseType.PERSONAL]
        elif MVRDocumentTemplate.LicenseType.COMMERCIAL in license_status_dict.keys():
            status = license_status_dict[MVRDocumentTemplate.LicenseType.COMMERCIAL]
        if status == MVRDocumentTemplate.NONE and MVRDocumentTemplate.LicenseType.IDENTIFICATION in license_status_dict.keys():
            status = license_status_dict[MVRDocumentTemplate.LicenseType.IDENTIFICATION]
        status = status.lower()
        if not status in LicenseStatus.items():
            logger.warning(f'Request ID: [{self.uuid}] -> Invalid Status value -> {status}')
            status = None
        return status

    async def __get_personal_info(self, blocks):
        name = gender = date_of_birth = None
        for lines in blocks:
            text = lines[4]
            if isinstance(text, str):
                if text.startswith(MVRDocumentTemplate.NAME):
                    name = text
                    name = name.replace(MVRDocumentTemplate.NAME, '').strip()
                if text.startswith(MVRDocumentTemplate.SEX):
                    gender = text[:text.find(MVRDocumentTemplate.WEIGHT)].replace(MVRDocumentTemplate.SEX, '')
                    date_of_birth = text[text.find(MVRDocumentTemplate.DOB) + 4:text.find(MVRDocumentTemplate.AGE)]
                    date_of_birth = parse_date(date_of_birth.strip())
                    gender = parse_gender(gender)
        return name, gender, date_of_birth

    async def __get_driver_violations(self, doc):
        blocks = []
        for page in doc:
            blocks.extend(page.get_text('blocks'))
        number_of_violations = 0
        violation = None
        suspension = None
        for i, block in enumerate(blocks):
            if block[4].startswith(MVRDocumentTemplate.VIOLATIONS):
                violation = i
            if block[4].startswith(MVRDocumentTemplate.SUSPENSIONS):
                suspension = i
        text = ''
        for i in range(violation, suspension):
            text = text + blocks[i][4]
        text = text.replace('\n', ' ')
        date = re.search(MVRDocumentTemplate.RegexCollection.DATE_REGEX, text)
        if date:
            start = date.start()
            split_by_date = re.split(MVRDocumentTemplate.RegexCollection.DATE_REGEX, text[start:])
            violations = [x for x in split_by_date if len(x) > 2]
            number_of_violations = len(violations)
        return number_of_violations

    async def __get_signature(self):
        is_signed = False
        try:
            for i_page_no in range(len(self.doc)):
                images = await self.pdf_helper.get_images_by_page(page_no=i_page_no)
                for image in images:
                    img_data = await self.cv_helper.extract_image_from_pdf(doc=self.pdf_helper.converted_doc,
                                                                           image_list=image)
                    is_signed = {'is_signed': await self.signature_validator._is_signature(image=img_data)}
                    if is_signed: break
                if is_signed: break
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            is_signed = None
        return is_signed

    async def extract(self):
        data = {"mvr": None}
        page = self.doc[0]
        blocks = page.get_textpage().extractBLOCKS()
        if len(blocks) > MVRDocumentTemplate.Block.MINIMUM_LENGTH:
            mvr_dict = {}
            (name, gender,
             date_of_birth), status, license_number, number_of_violations, signature = await asyncio.gather(
                self.__get_personal_info(blocks),
                self.__get_license_status(page),
                self.__get_license_number(blocks),
                self.__get_driver_violations(self.doc),
                self.__get_signature()
            )
            mvr_dict = {'name': name,
                        'gender': gender,
                        'date_of_birth': date_of_birth,
                        'status': status,
                        'license_number': license_number,
                        'number_of_violations': number_of_violations,
                        'signature': signature}

            data['mvr'] = mvr_dict
        else:
            logger.warning(f'Request ID: [{self.uuid}] ')
            raise InvalidPDFStructureTypeException(self.uuid)
        logger.info(f'Request ID: [{self.uuid}] Response: {data}')

        return data
