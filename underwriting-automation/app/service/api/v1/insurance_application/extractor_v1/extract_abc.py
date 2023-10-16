import abc
import re
from datetime import datetime

import fitz
from mergedeep import merge

from app import logger
from app.constant import APPDocumentTemplate
from app.constant import PDF, Date
from app.service.api.v1.signature.validate_signature_v1 import ValidateSignatureV1
from app.service.helper.cv_helper import CVHelper
from app.service.helper.pdf_helper import PDFHelper


class APPExtractABC():
    __metaclass__ = abc.ABCMeta

    def __init__(self, uuid, file):
        self.uuid = uuid
        self.file = file
        self.doc = fitz.open(stream=self.file, filetype="pdf")
        self.pdf_helper = PDFHelper(self.doc)
        self.signature_validator = ValidateSignatureV1()
        self.cv_helper = CVHelper()
        self.constants = APPDocumentTemplate.AllianceUnited

    @abc.abstractmethod
    async def __check_blocks(self, *args, **kwargs):
        """Required method"""

    @abc.abstractmethod
    async def __check_blocks_for_multiple_occurrence(self, *args, **kwargs):
        """Required method"""

    @abc.abstractmethod
    async def __get_insured_info(self, *args, **kwargs):
        """Required method"""

    @abc.abstractmethod
    async def __get_broker_info(self, *args, **kwargs):
        """Required method"""

    @abc.abstractmethod
    async def __get_policy_info(self, *args, **kwargs):
        """Required method"""

    @abc.abstractmethod
    async def __get_driver_info(self, *args, **kwargs):
        """Required method"""

    @abc.abstractmethod
    async def __get_vehicle_info(self, *args, **kwargs):
        """Required method"""

    @abc.abstractmethod
    async def __get_coverage_info(self, *args, **kwargs):
        """Required method"""

    @abc.abstractmethod
    async def extract(self, *args, **kwargs):
        """Required method"""

    @abc.abstractmethod
    async def __get_signatures(self):
        """Required method"""

    async def _get_placeholder_bbox(self, sections, metadata, doc, target):
        data = []
        pages = {}
        bboxes = {}
        previous_section = None
        if target == self.constants.Label.SIGNATURE:
            labels = self.constants.Key.SignatureVerification.SIGNATURE_LABELS
        elif target == self.constants.Label.DATE:
            labels = self.constants.Key.SignatureVerification.DATE_LABELS
        else:
            return bboxes
        data.extend(sections)
        data.extend(labels)
        _metadata = tuple(filter(lambda x: x[PDF.TEXT] in data and x[PDF.PAGE_NUMBER] in range(
            self.constants.Key.SignatureVerification.SIGN_VERIFICATION_STARTING_PAGE_NO, doc.page_count),
                                 metadata))
        for i_metadata in _metadata:
            if i_metadata[PDF.TEXT] in sections:
                previous_section = i_metadata[PDF.TEXT]
                pages[previous_section] = {'page_no': i_metadata[PDF.PAGE_NUMBER]}
            if previous_section and i_metadata[PDF.TEXT] in labels:
                bboxes[previous_section] = {target: {'bbox': i_metadata[PDF.BBOX]}}
                previous_section = None
        bboxes = merge(bboxes, pages)
        return bboxes

    async def __get_section_index(self, metadata, section, section_name):
        starting_index = None
        ending_index = None
        if len(section) - 1 == section.index(section_name):
            boundary_section = section[-1]
        else:
            boundary_section = section[(section.index(section_name)) + 1]
        for index, value in enumerate(metadata):
            if value[PDF.TEXT] == section_name: starting_index = index
            if value[PDF.TEXT] == boundary_section: ending_index = index
        return starting_index, ending_index

    async def __get_page_sections(self, metadata, allowed_sections):
        return [i_metadata[PDF.TEXT] for i_metadata in metadata if i_metadata[PDF.TEXT] in allowed_sections]

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

    @abc.abstractmethod
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

    async def _get_date_bbox(self, page_no, section_name, index=0):
        bbox = None
        page_metadata = await self.pdf_helper.get_attributes_by_page(page_no=page_no)
        sections = await self.__get_page_sections(metadata=page_metadata,
                                                  allowed_sections=self.constants.Key.SignatureVerification.ALLOWED_SECTIONS)
        starting_index, ending_index = await self.__get_section_index(page_metadata, sections, section_name)
        if starting_index == ending_index:
            sliced_metadata = page_metadata[starting_index:]
        else:
            sliced_metadata = page_metadata[starting_index:ending_index]
        bboxes = await self.__get_parsed_date_bbox(metadata=sliced_metadata)
        if len(bboxes):
            try:
                bbox = bboxes[index]
            except IndexError as e:
                logger.error(f'Request ID: [{self.uuid}] -> {e}')
        return bbox
