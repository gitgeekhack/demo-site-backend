import asyncio

from app import logger
from app.business_rule_exception import InvalidPDFStructureTypeException
from app.constant import BrokerPackageTemplate, ExceptionMessage, PDF
from app.service.api.v1.broker_package.extractor_v1.extract_abc import BrokerPackageExtractABC
from app.service.helper.parser import parse_date


class Template1Extractor(BrokerPackageExtractABC):

    def __init__(self, uuid, doc):
        super().__init__(uuid, doc)
        self.constants = BrokerPackageTemplate.Type1

    async def __get_signed_date(self, blocks):
        try:
            date = '{}/{}/{}'
            day = int(blocks[self.constants.Block.SIGNED_DAY])
            month = await self.is_valid_month(blocks[self.constants.Block.SIGNED_MONTH].lower())
            year = int(blocks[self.constants.Block.SIGNED_YEAR].replace(',', ''))
            date = date.format(month, day, year)
            date = parse_date(date)
        except (IndexError, ValueError):
            date = None
            logger.warning(ExceptionMessage.UNABLE_TO_EXTRACT_DATAPOINT.format(self.uuid, 'signed_date'))
        return date

    async def __get_broker_fee(self, blocks):
        try:
            broker_fee = float(blocks[self.constants.Block.BROKER_FEE])
        except (IndexError, ValueError):
            broker_fee = None
            logger.warning(ExceptionMessage.UNABLE_TO_EXTRACT_DATAPOINT.format(self.uuid, 'broker_fee'))
        return broker_fee

    async def __get_insured_name(self, page):
        try:
            blocks = page.get_text().split('\n')
            text = blocks[self.constants.Block.NAME_LOWER_BOUND:]
            name = None
            if text:
                name = [x for x in text if not x.isnumeric() and len(x.split()) >= 2]
            insured_name = name[0] if name else None
        except (IndexError, ValueError):
            insured_name = None
            logger.warning(ExceptionMessage.UNABLE_TO_EXTRACT_DATAPOINT.format(self.uuid, 'insured_name'))
        return insured_name

    async def __get_section_bbox(self):
        page_metadata = tuple(filter(lambda x: x[PDF.TEXT] in self.constants.SECTION_LABELS, self.pdf_helper.metadata))
        return page_metadata

    async def __check_disclosures_and_disclosure_form_signature(self):
        meta_data = await self.__get_section_bbox()
        sections = tuple(filter(lambda x: x[-1] in [0, 1], meta_data))
        prev_section = None
        (x0, y0, x1, y1) = self.constants.SECTION_BOX_PADDING['disclosure']
        validation = {x: None for x in self.constants.SECTION_LABELS}
        for section in sections:
            if section[PDF.TEXT] == self.constants.INITIALS and prev_section:
                bbox = await self.pdf_helper.apply_bbox_padding(page_no=section[-1], bbox=(section[PDF.BBOX]),
                                                                x0_pad=x0, y0_pad=y0, x1_pad=x1, y1_pad=y1)
                signatures = await self.pdf_helper.get_images_by_page(page_no=section[-1])
                is_signed = await self.signature_validator.validate(self.pdf_helper.converted_doc, bbox,
                                                                    signatures,
                                                                    self.pdf_helper.converted_doc[section[-1]])
                validation[prev_section[0]] = {'is_signed': is_signed}
            prev_section = section
        disclosures = {self.response_key.COVERAGES: validation[self.constants.COVERAGES],
                       self.response_key.DRIVING_RECORD: validation[self.constants.DRIVING_RECORD],
                       'exclusion': {
                           self.response_key.EXCLUSION_UNINSURED_BI: validation[
                               self.constants.EXCLUSION_UNINSURED_BI],
                           self.response_key.EXCLUSION_COMP_COLL_COVERAGE: validation[
                               self.constants.EXCLUSION_COMP_COLL_COVERAGE],
                           self.response_key.EXCLUSION_BUSINESS_USE: validation[
                               self.constants.EXCLUSION_BUSINESS_USE],
                           self.response_key.EXCLUSION_NAMED_DRIVER_LIMITATION: validation[
                               self.constants.EXCLUSION_NAMED_DRIVER_LIMITATION]
                       }}
        disclosure_form = validation[self.constants.DISCLOSURE_FORM]
        return disclosures, disclosure_form

    async def __check_broker_package_agreement_signature(self):
        broker_fee_agreement = None
        response_key_mapping = {self.constants.CLIENT_INITIALS: self.response_key.CLIENT_INITIALS,
                                self.constants.CONDITION_AND_ACKNOWLEDGMENT_AGREEMENT: self.response_key.CONDITION_AND_ACKNOWLEDGMENT_AGREEMENT,
                                self.constants.CLIENT_SIGNATURE: self.response_key.CLIENT_SIGNATURE
                                }
        meta_data = await self.__get_section_bbox()
        sections = tuple(filter(lambda x: x[PDF.TEXT] in response_key_mapping, meta_data))
        if sections:
            broker_fee_agreement = {response_key_mapping[x]: None for x in response_key_mapping}
            for section in sections:
                x0, y0, x1, y1 = self.constants.SECTION_BOX_PADDING[section[PDF.TEXT]]
                is_signed = None
                broker_fee_agreement[response_key_mapping[section[PDF.TEXT]]] = None
                if section:
                    bbox = await self.pdf_helper.apply_bbox_padding(page_no=section[PDF.PAGE_NUMBER],
                                                                    bbox=(section[PDF.BBOX]),
                                                                    x0_pad=x0, y0_pad=y0, x1_pad=x1, y1_pad=y1)
                    signatures = await self.pdf_helper.get_images_by_page(page_no=section[PDF.PAGE_NUMBER])
                    is_signed = await self.signature_validator.validate(self.pdf_helper.converted_doc, bbox,
                                                                        signatures,
                                                                        self.pdf_helper.converted_doc[
                                                                            section[PDF.PAGE_NUMBER]])
                broker_fee_agreement[response_key_mapping[section[PDF.TEXT]]] = {'is_signed': is_signed}
        else:
            logger.warning(
                ExceptionMessage.UNABLE_TO_EXTRACT_DATAPOINT.format(self.uuid, 'broker fee agreement signatures'))
            broker_fee_agreement = None
        return broker_fee_agreement

    async def __check_text_messaging_consent_agreement_signature(self):
        text_messaging_consent_agreement = None
        section = None
        try:
            meta_data = await self.__get_section_bbox()
            section = tuple(filter(lambda x: x[PDF.TEXT] == self.constants.MESSAGING_CONSENT_SIGNATURE, meta_data))[0]
            if section:
                x0, y0, x1, y1 = self.constants.SECTION_BOX_PADDING[self.constants.MESSAGING_CONSENT_SIGNATURE]
                bbox = await self.pdf_helper.apply_bbox_padding(page_no=section[PDF.PAGE_NUMBER],
                                                                bbox=(section[PDF.BBOX]),
                                                                x0_pad=x0, y0_pad=y0, x1_pad=x1, y1_pad=y1)
                signatures = await self.pdf_helper.get_images_by_page(page_no=section[PDF.PAGE_NUMBER])
                is_signed = await self.signature_validator.validate(self.pdf_helper.converted_doc, bbox, signatures,
                                                                    self.pdf_helper.converted_doc[
                                                                        section[PDF.PAGE_NUMBER]])
                text_messaging_consent_agreement = {'is_signed': is_signed}
            else:
                logger.warning(
                    ExceptionMessage.UNABLE_TO_EXTRACT_DATAPOINT.format(self.uuid,
                                                                        'text messaging consent agreement signature'))
                text_messaging_consent_agreement = None
        except IndexError:
            logger.warning(
                ExceptionMessage.UNABLE_TO_EXTRACT_DATAPOINT.format(self.uuid,
                                                                    'text messaging consent agreement signature'))
            text_messaging_consent_agreement = None
        return text_messaging_consent_agreement

    async def __get_signature(self):
        (disclosures, disclosure_form), broker_fee_agreement, text_messaging_consent_agreement = await asyncio.gather(
            self.__check_disclosures_and_disclosure_form_signature(),
            self.__check_broker_package_agreement_signature(),
            self.__check_text_messaging_consent_agreement_signature()
        )
        signatures = {self.response_key.DISCLOSURES: disclosures,
                      self.response_key.STANDARD_BROKER_FEE_DISCLOSURE_FORM: disclosure_form,
                      self.response_key.BROKER_FEE_AGREEMENT: broker_fee_agreement,
                      self.response_key.TEXT_MESSAGING_CONSENT_AGREEMENT: text_messaging_consent_agreement}
        return signatures

    async def extract(self):
        page = self.doc[2]
        blocks = page.get_textpage().extractText().split()
        date, broker_fee, insured_name, signatures = await asyncio.gather(self.__get_signed_date(blocks),
                                                                          self.__get_broker_fee(blocks),
                                                                          self.__get_insured_name(page),
                                                                          self.__get_signature())
        data = {'signed_date': date, 'broker_fee': broker_fee, 'insured_name': insured_name,
                'signature': signatures}
        logger.info(f'Request ID: [{self.uuid}] Response: {data}')
        return data
