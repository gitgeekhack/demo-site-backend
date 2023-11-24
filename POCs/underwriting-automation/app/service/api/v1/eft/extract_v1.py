import asyncio
import re
from datetime import datetime

import fitz

from app import logger
from app.business_rule_exception import InvalidPDFStructureTypeException
from app.constant import EFT, PDF, Date
from app.service.api.v1.signature.validate_signature_v1 import ValidateSignatureV1
from app.service.helper.pdf_helper import PDFHelper


class EFTDataPointExtractorV1:
    def __init__(self, uuid, file):
        self.uuid = uuid
        self.signature_validator = ValidateSignatureV1()
        self.sections = EFT.Sections
        self.response_key = EFT.ResponseKey
        self.regex = EFT.RegexCollection
        self.file = file
        self.doc = fitz.open(stream=self.file, filetype="pdf")
        self.page = self.doc[0]
        self.page_text = self.page.get_text().replace('\n', ' ')
        self.pdf_helper = PDFHelper(self.doc)

    async def __get_insured_name(self, text):
        try:
            name = re.search(self.regex.IN_BETWEEN % (self.sections.INSURED_NAME_START_KEY,
                                                      self.sections.INSURED_NAME_END_KEY), text)
            if name:
                name = name.group(1).strip()
            if self.sections.XXXX in name:
                name = re.search(self.regex.END_WITH % self.sections.XXXX, name).group(1).strip()
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            name = None
        return name

    async def __get_policy_number(self, text):
        try:
            policy_number = re.search(self.regex.IN_BETWEEN % (self.sections.POLICY_NUMBER_START_KEY,
                                                               self.sections.POLICY_NUMBER_END_KEY), text)
            if policy_number:
                policy_number = policy_number.group(1).strip()
            if self.sections.VISA in policy_number:
                policy_number = re.search(self.regex.END_WITH % self.sections.VISA, policy_number).group(1).strip()
            elif self.sections.MASTER_CARD in policy_number:
                policy_number = re.search(self.regex.END_WITH % self.sections.MASTER_CARD, policy_number).group(
                    1).strip()
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            policy_number = None
        return policy_number

    async def __validate_date_format(self, dates):
        valid_date = []
        for date in dates:
            try:
                datetime.strptime(date, Date.Format.YMD)
                valid_date.append(date)
                continue
            except Exception:
                pass
            try:
                datetime.strptime(date, Date.Format.MDY_DASH)
                valid_date.append(date)
                continue
            except Exception:
                pass
            try:
                datetime.strptime(date, Date.Format.MDY_SLASH)
                valid_date.append(date)
                continue
            except Exception:
                pass
        return valid_date

    async def _parse_date(self, text):
        dates = []
        date = re.search(Date.RegexCollection.YYYY_MM_DD, text)
        if date:
            dates.extend(x.group() for x in re.finditer(Date.RegexCollection.YYYY_MM_DD, text))
            dates = await self.__validate_date_format(dates)
            return dates

        date = re.search(Date.RegexCollection.MM_DD_YYYY, text)
        if date:
            dates.extend(x.group() for x in re.finditer(Date.RegexCollection.MM_DD_YYYY, text))
            dates = await self.__validate_date_format(dates)
            return dates

    async def __get_parsed_date_bbox(self, metadata):
        bboxes = []
        text = " ".join(i_sliced_metadata[PDF.TEXT] for i_sliced_metadata in metadata)
        dates = await self._parse_date(text)
        if dates:
            for i_metadata in metadata:
                for date in dates:
                    if date == i_metadata[PDF.TEXT] and i_metadata[PDF.BBOX] not in bboxes:
                        bboxes.append(i_metadata[PDF.BBOX])
        return bboxes

    async def __check_date(self, section_boxes, date_metadate):
        is_dated = False
        if section_boxes and date_metadate:
            date_bbox = date_metadate
            result = await self.pdf_helper.match_bbox(section_boxes, date_bbox)
            try:
                if set(result).issubset(section_boxes):
                    is_dated = True
            except TypeError as e:
                logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            except Exception as e:
                logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
                is_dated = None
        return is_dated

    async def __get_signature(self, label, index):
        signature = None
        try:
            is_dated = False
            is_signed = False
            date_bbox = None
            signature_placeholder_bboxes = await self.pdf_helper.get_bbox_by_text(label)
            date_placeholder_bboxes = await self.pdf_helper.get_bbox_by_text(self.sections.DATE)
            sign_x0, sign_y0, sign_x1, sign_y1 = self.sections.SECTION_BOX_PADDING[label]
            date_x0, date_y0, date_x1, date_y1 = self.sections.SECTION_BOX_PADDING[self.sections.DATE]

            if signature_placeholder_bboxes:
                signature_placeholder_bbox = signature_placeholder_bboxes[0][0]
                signature_placeholder_bbox = await self.pdf_helper.apply_bbox_padding(
                    page_no=self.sections.PAGE_NO,
                    bbox=signature_placeholder_bbox,
                    x0_pad=sign_x0, y0_pad=sign_y0,
                    x1_pad=sign_x1, y1_pad=sign_y1)
                page_signatures = await self.pdf_helper.get_images_by_page(page_no=self.sections.PAGE_NO)
                is_signed = await self.signature_validator.validate(doc=self.pdf_helper.converted_doc,
                                                                    section_bbox=signature_placeholder_bbox,
                                                                    images=page_signatures,
                                                                    page=self.pdf_helper.converted_doc[
                                                                        self.sections.PAGE_NO])
            else:
                return signature

            if date_placeholder_bboxes and signature_placeholder_bboxes:
                signature_placeholder_bbox = signature_placeholder_bboxes[0][0]
                date_placeholder_bbox = date_placeholder_bboxes[index][0]
                date_bboxes = await self.__get_parsed_date_bbox(self.pdf_helper.metadata)
                if len(date_bboxes): date_bbox = date_bboxes[index]
                signature_placeholder_bbox = await self.pdf_helper.apply_bbox_padding(
                    page_no=self.sections.PAGE_NO,
                    bbox=signature_placeholder_bbox,
                    x0_pad=sign_x0, y0_pad=sign_y0,
                    x1_pad=sign_x1, y1_pad=sign_y1)
                date_placeholder_bbox = await self.pdf_helper.apply_bbox_padding(
                    page_no=self.sections.PAGE_NO,
                    bbox=date_placeholder_bbox,
                    x0_pad=date_x0, y0_pad=date_y0,
                    x1_pad=date_x1, y1_pad=date_y1)
                is_dated = await self.__check_date(section_boxes=(signature_placeholder_bbox, date_placeholder_bbox),
                                                   date_metadate=date_bbox)
            signature = {'is_signed': is_signed, 'is_dated': is_dated}
        except IndexError as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            signature = None
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            signature = None
        return signature

    async def extract(self):
        data = {'eft': None}
        if self.sections.EFT_DOCUMENT in self.page_text:
            insured_name, policy_number, insured_signature, card_holder_signature = await asyncio.gather(
                self.__get_insured_name(self.page_text),
                self.__get_policy_number(self.page_text),
                self.__get_signature(label=self.sections.INSURED_SIGNATURE,
                                     index=0),
                self.__get_signature(label=self.sections.CARD_HOLDER_SIGNATURE,
                                     index=-1))
            data['eft'] = {self.response_key.INSURED_NAME: insured_name,
                           self.response_key.POLICY_NUMBER: policy_number,
                           'signature': {self.response_key.INSURED_SIGNATURE: insured_signature,
                                         self.response_key.CARD_HOLDER_SIGNATURE: card_holder_signature}}
        else:
            logger.warning(f'Request ID: [{self.uuid}] ')
            raise InvalidPDFStructureTypeException(self.uuid)
        print(f'Request ID: [{self.uuid}] Response: {data}')

        return data
