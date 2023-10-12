import asyncio
import re

import cv2
import numpy as np
from dateutil import parser

from app import logger, app
from app.constant import BrokerPackageTemplate, ExceptionMessage
from app.service.api.v1.broker_package.extractor_v1.extract_abc import BrokerPackageExtractABC
from app.service.helper.cv_helper import CVHelper

CHECK_BOX_TEMPLATE = cv2.imread(app.config.CHECK_BOX_TEMPLATE_PATH, 0)


class Template2Extractor(BrokerPackageExtractABC):

    def __init__(self, uuid, doc):
        super().__init__(uuid, doc)
        self.constants = BrokerPackageTemplate.Type2
        self.cv_helper = CVHelper()
        self.page_text = ''
        for page in self.doc:
            self.page_text = self.page_text + page.get_text()
        self.page_text = self.page_text.replace('\n', ' ').replace('_', ' ')

    async def __get_signed_date(self):
        match = re.search(self.constants.RegexCollection.SIGNED_DATE, self.page_text)
        try:
            if match:
                date = match.group(1)
                date = parser.parse(date.replace('day', ''))
                signed_date = date.date().isoformat()
            else:
                signed_date = None
                logger.warning(ExceptionMessage.UNABLE_TO_EXTRACT_DATAPOINT.format(self.uuid, 'signed_date'))
        except (AttributeError, ValueError):
            signed_date = None
            logger.warning(ExceptionMessage.UNABLE_TO_EXTRACT_DATAPOINT.format(self.uuid, 'signed_date'))

        return signed_date

    async def __get_broker_fee(self):
        match = re.search(self.constants.RegexCollection.BROKER_FEE, self.page_text)
        if match:
            broker_fee = float(match.group(1).strip())
        else:
            broker_fee = None
            logger.warning(ExceptionMessage.UNABLE_TO_EXTRACT_DATAPOINT.format(self.uuid, 'broker_fee'))
        return broker_fee

    async def __get_insured_name(self):
        match = re.search(self.constants.RegexCollection.INSURED_NAME, self.page_text)
        if match:
            insured_name = match.group(1).strip()
        else:
            insured_name = None
            logger.warning(ExceptionMessage.UNABLE_TO_EXTRACT_DATAPOINT.format(self.uuid, 'insured_name'))
        return insured_name

    async def __get_image_for_labels(self, section, prev_section, blocks):
        start = prev_section[1]
        end = section[1]
        prev_images = None
        if not prev_section[-1] == section[-1]:
            blocks = self.doc[prev_section[-1]].get_text('dict')['blocks']
            prev_images = list(
                filter(lambda x: x['image'] if start < x['number'] < len(blocks) and x['type'] == 1 else None, blocks))
            blocks = self.doc[section[-1]].get_text('dict')['blocks']
            start = 0
        images = list(filter(
            lambda x: x['image'] if start < x['number'] < end and x['type'] == 1 else None,
            blocks))
        if prev_images:
            images.extend(prev_images)
        return images

    async def __get_signature_checks(self):
        validation = {x: None for x in self.constants.SECTION_LABELS}
        meta_data = []
        for page in self.doc:
            blocks = page.get_text('dict')['blocks']
            temp = tuple([(x['lines'][0]['spans'][0]['text'], x['number'], page.number,) for x in blocks if
                          x['type'] == 0 and x['lines'][0]['spans'][0]['text'] in self.constants.SECTION_LABELS])
            meta_data.extend(temp)
        meta_data = tuple(meta_data)
        prev_section = None
        for section in meta_data:
            flags = []
            if section[0] == self.constants.I_AGREE and prev_section:
                blocks = self.doc[section[-1]].get_text('dict')['blocks']
                images = await self.__get_image_for_labels(section, prev_section, blocks)
                for image in images:
                    np_array = np.asarray(bytearray(image['image']), dtype=np.uint8)
                    input_image = cv2.imdecode(np_array, cv2.IMREAD_UNCHANGED)
                    flags.append(await self.cv_helper.match_template(template=CHECK_BOX_TEMPLATE,
                                                                     image=input_image))
                    validation[prev_section[0]] = {'is_signed': any(flags)}
            prev_section = section
        return validation

    async def __get_signatures(self):
        validation = await self.__get_signature_checks()
        signatures = {self.response_key.DISCLOSURES: {self.response_key.COVERAGES: validation[self.constants.COVERAGES],
                                                      self.response_key.DRIVING_RECORD: validation[
                                                          self.constants.DRIVING_RECORD],
                                                      'exclusion': {
                                                          self.response_key.EXCLUSION_UNINSURED_BI: validation[
                                                              self.constants.EXCLUSION_UNINSURED_BI],
                                                          self.response_key.EXCLUSION_COMP_COLL_COVERAGE: validation[
                                                              self.constants.EXCLUSION_COMP_COLL_COVERAGE],
                                                          self.response_key.EXCLUSION_BUSINESS_USE: validation[
                                                              self.constants.EXCLUSION_BUSINESS_USE],
                                                          self.response_key.EXCLUSION_NAMED_DRIVER_LIMITATION:
                                                              validation[
                                                                  self.constants.EXCLUSION_NAMED_DRIVER_LIMITATION]
                                                      }},
                      self.response_key.STANDARD_BROKER_FEE_DISCLOSURE_FORM: validation[
                          self.constants.STANDARD_BROKER_FEE_DISCLOSURE_FORM],
                      self.response_key.TEXT_MESSAGING_CONSENT_AGREEMENT: validation[
                          self.constants.TEXT_MESSAGING_CONSENT_AGREEMENT],
                      self.response_key.BROKER_FEE_AGREEMENT: {
                          self.response_key.CLIENT_INITIALS: validation[self.constants.BROKER_FEE_AGREEMENT],
                          self.response_key.CONDITION_AND_ACKNOWLEDGMENT_AGREEMENT: validation[
                              self.constants.CONDITION_AND_ACKNOWLEDGMENT_AGREEMENT],
                          self.response_key.CLIENT_SIGNATURE: {'is_signed': True}
                      }
                      }
        return signatures

    async def extract(self):

        date, broker_fee, insured_name, signature = await asyncio.gather(self.__get_signed_date(),
                                                                         self.__get_broker_fee(),
                                                                         self.__get_insured_name(),
                                                                         self.__get_signatures()
                                                                         )
        data = {'signed_date': date, 'broker_fee': broker_fee, 'insured_name': insured_name,
                'signature': signature}
        logger.info(f'Request ID: [{self.uuid}] Response: {data}')
        return data
