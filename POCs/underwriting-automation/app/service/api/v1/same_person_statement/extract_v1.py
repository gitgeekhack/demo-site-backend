import asyncio

import fitz

from app import logger
from app.business_rule_exception import InvalidPDFStructureTypeException
from app.constant import SamePersonTemplate
from app.service.api.v1.signature.validate_signature_v1 import ValidateSignatureV1
from app.service.helper.file_downloader import get_file_stream
from app.service.helper.pdf_helper import PDFHelper


class SPSDataPointExtractorV1:
    def __init__(self, uuid, document_url):
        self.uuid = uuid
        self.document_url = document_url
        self.signature_validator = ValidateSignatureV1()
        self.pdf_helper = None

    async def __get_signature(self):
        signature = None
        try:
            metadata = self.pdf_helper.metadata
            section = tuple(filter(lambda x: x[0] == SamePersonTemplate.SIGNATURE_SEARCH_KEY, metadata))
            if section:
                x0, y0, x1, y1 = SamePersonTemplate.SIGNATURE_PADDING
                bbox = await self.pdf_helper.apply_bbox_padding(section[0][-1], section[0][1], x0_pad=x0, y0_pad=y0,
                                                                x1_pad=x1, y1_pad=y1)
                page_signatures = await self.pdf_helper.get_images_by_page(page_no=section[0][-1])
                is_signed = await self.signature_validator.validate(self.pdf_helper.converted_doc, bbox,
                                                                    page_signatures,
                                                                    self.pdf_helper.converted_doc[section[0][-1]])
                signature = {'is_signed': is_signed}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            signature = None
        return signature

    async def extract(self):
        data = {"same_person": None}
        file = await get_file_stream(self.uuid, self.document_url)
        doc = fitz.open(stream=file, filetype="pdf")
        self.pdf_helper = PDFHelper(doc)
        check_list = [SamePersonTemplate.CHECK_VALID_DOCUMENT_KEY, SamePersonTemplate.CHECK_VALID_DOCUMENT_KEY.strip()]
        object_extraction_coroutines = [self.pdf_helper.find_page_by_text(text) for text in check_list]
        meta_data = await asyncio.gather(*object_extraction_coroutines)
        if [i for i in meta_data if i]:
            same_person = await self.__get_signature()
            data['same_person'] = {'signature': same_person}
        else:
            logger.warning(f'Request ID: [{self.uuid}] ')
            raise InvalidPDFStructureTypeException(self.document_url)
        print(f'Request ID: [{self.uuid}] Response: {data}')

        return data
