import asyncio
import re

import fitz
from dateutil.parser import parse

from app import logger
from app.business_rule_exception import InvalidPDFStructureTypeException
from app.constant import PromiseToProvideTemplate, PDF
from app.service.api.v1.signature.validate_signature_v1 import ValidateSignatureV1
from app.service.helper.pdf_helper import PDFHelper


class PTPDataPointExtractorV1:
    def __init__(self, uuid, file):
        self.uuid = uuid
        self.signature_validator = ValidateSignatureV1()
        self.constants = PromiseToProvideTemplate
        self.file = file
        self.doc = fitz.open(stream=self.file, filetype="pdf")
        self.pdf_helper = PDFHelper(self.doc)
        self.indexof = {x: self.pdf_helper.metadata.index(y) for x in self.constants.Sections.TITLES for y in
                        self.pdf_helper.metadata if y[0].startswith(x)}

    async def __get_acknowledgement_signature(self):
        condition_and_acknowledgement_agreement = None
        try:
            section = tuple(
                filter(lambda x: self.constants.Sections.ACKNOWLEDGMENT_INITIALS_KEY in x[PDF.TEXT],
                       self.pdf_helper.metadata))
            if section:
                section = section[0]
                x0, y0, x1, y1 = self.constants.Sections.SECTION_BOX_PADDING[
                    self.constants.Sections.ACKNOWLEDGMENT_INITIALS_KEY]
                bbox = await self.pdf_helper.apply_bbox_padding(page_no=section[PDF.PAGE_NUMBER],
                                                                bbox=(section[PDF.BBOX]),
                                                                x0_pad=x0, y0_pad=y0, x1_pad=x1, y1_pad=y1)
                signatures = await self.pdf_helper.get_images_by_page(page_no=section[PDF.PAGE_NUMBER])
                is_signed = await self.signature_validator.validate(self.pdf_helper.converted_doc, bbox, signatures,
                                                                    self.pdf_helper.converted_doc[
                                                                        section[PDF.PAGE_NUMBER]])
                condition_and_acknowledgement_agreement = {'is_signed': is_signed}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
            condition_and_acknowledgement_agreement = None
        return condition_and_acknowledgement_agreement

    async def __get_agreed_to_by_signature(self):
        agreed_to_by = None
        try:
            section = tuple(
                filter(lambda x: self.constants.Sections.AGREED_BY_KEY in x[PDF.TEXT], self.pdf_helper.metadata))
            if section:
                section = section[0]
                x0, y0, x1, y1 = self.constants.Sections.SECTION_BOX_PADDING[self.constants.Sections.AGREED_BY_KEY]
                bbox = await self.pdf_helper.apply_bbox_padding(page_no=section[PDF.PAGE_NUMBER],
                                                                bbox=(section[PDF.BBOX]),
                                                                x0_pad=x0, y0_pad=y0, x1_pad=x1, y1_pad=y1)
                signatures = await self.pdf_helper.get_images_by_page(page_no=section[PDF.PAGE_NUMBER])
                is_signed = await self.signature_validator.validate(self.pdf_helper.converted_doc, bbox, signatures,
                                                                    self.pdf_helper.converted_doc[
                                                                        section[PDF.PAGE_NUMBER]])

                agreed_to_by = {'is_signed': is_signed}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
            agreed_to_by = None
        return agreed_to_by

    async def __get_signature(self):
        try:
            agreed_to_be, condition_and_acknowledgement = await asyncio.gather(self.__get_agreed_to_by_signature(),
                                                                               self.__get_acknowledgement_signature())
            signatures = {self.constants.ResponseKey.AGREED_BY_SIGN: agreed_to_be,
                          self.constants.ResponseKey.ACKNOWLEDGMENT_SIGN: condition_and_acknowledgement}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            signatures = None
        return signatures

    async def __parse_date(self, text):
        try:
            date = str(parse(text).date())
        except ValueError:
            date = None
        return date

    async def __get_applied_coverage_effective_date(self):
        try:
            date_text = self.pdf_helper.metadata[:self.indexof[self.constants.Sections.APPLIED_COVERAGE_KEY]]
            match = re.findall(self.constants.RegexCollection.DATE, ' '.join(map(str, date_text)))
            date = await self.__parse_date(match[0]) if len(match) > 0 else None
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            date = None
        return date

    async def __get_promise_to_provide_by_date(self):
        try:
            date_text = self.pdf_helper.metadata[
                        self.indexof[self.constants.Sections.APPLIED_COVERAGE_KEY]:self.indexof[
                            self.constants.Sections.PROMISE_TO_PROVIDE_KEY]]
            match = re.findall(self.constants.RegexCollection.DATE, ' '.join(map(str, date_text)))
            date = await self.__parse_date(match[0]) if len(match) > 0 else None
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            date = None
        return date

    async def __get_agreement_date(self):
        try:
            date_text = self.pdf_helper.metadata[
                        self.indexof[self.constants.Sections.PROMISE_TO_PROVIDE_KEY]:]
            match = re.findall(self.constants.RegexCollection.DATE, ' '.join(map(str, date_text)))
            date = [await self.__parse_date(x) if len(match) > 0 else None for x in match] if len(match) > 0 else None
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            date = None
        return date

    async def extract(self):
        data = {"promise_to_provide": None}
        if [i for i in self.pdf_helper.metadata if self.constants.Sections.CHECK_VALID_DOCUMENT_KEY in i[PDF.TEXT]]:
            signatures, applied_coverage_date, ptp_by_date, ptp_agreement_date = await asyncio.gather(
                self.__get_signature(),
                self.__get_applied_coverage_effective_date(),
                self.__get_promise_to_provide_by_date(),
                self.__get_agreement_date())

            data['promise_to_provide'] = {self.constants.ResponseKey.SIGNATURES: signatures,
                                          self.constants.ResponseKey.APPLIED_COVERAGE_DATE: applied_coverage_date,
                                          self.constants.ResponseKey.PTP_BY_DATE: ptp_by_date,
                                          self.constants.ResponseKey.PTP_AGREEMENT_DATE: ptp_agreement_date}
        else:
            logger.warning(f'Request ID: [{self.uuid}] ')
            raise InvalidPDFStructureTypeException(self.uuid)
        print(f'Request ID: [{self.uuid}] Response: {data}')

        return data
