import asyncio
import re
import fitz

from app import logger
from app.business_rule_exception import InvalidPDFStructureTypeException
from app.constant import ArtisanUseLetterTemplate, PDF
from app.service.api.v1.signature.validate_signature_v1 import ValidateSignatureV1
from app.service.helper.pdf_helper import PDFHelper


class AULDataPointExtractorV1:
    def __init__(self, uuid, file):
        self.uuid = uuid
        self.signature_validator = ValidateSignatureV1()
        self.file = file
        self.doc = fitz.open(stream=self.file, filetype="pdf")
        self.pdf_helper = PDFHelper(self.doc)
        self.section = ArtisanUseLetterTemplate.Sections
        self.response_key = ArtisanUseLetterTemplate.ResponseKey
        self.padding = ArtisanUseLetterTemplate.Sections.SECTION_BOX_PADDING
        self.indexof = {x: self.pdf_helper.metadata.index(y) for x in self.section.TITLES for y in
                        self.pdf_helper.metadata if y[PDF.TEXT].strip().startswith(x)}

    async def __get_insured_name(self):
        insured_name = None
        if self.section.CUSTOMER_NAME in self.form_fields:
            insured_name = self.form_fields[self.section.CUSTOMER_NAME].strip()
        elif self.section.CUSTOMER_NAME_BI_LINGUAL in self.indexof:
            insured_name = self.pdf_helper.metadata[self.indexof[self.section.CUSTOMER_NAME_BI_LINGUAL] - 1][
                PDF.TEXT].strip()
        return insured_name

    async def __get_policy_number(self):
        policy_number = None
        if self.section.POLICY_NUMBER in self.form_fields:
            policy_number = self.form_fields[self.section.POLICY_NUMBER].strip()
        elif self.section.POLICY_NUMBER in self.indexof:
            policy_number = self.pdf_helper.metadata[self.indexof[self.section.POLICY_NUMBER] - 1][PDF.TEXT].strip()
        return policy_number

    async def __get_vehicles(self, text):
        information = []
        vehicles = None
        text = text.split(',')
        for x in text:
            match = re.match(ArtisanUseLetterTemplate.RegexCollection.VEHICLE_INFORMATION, x.strip())
            if match:
                x = match.group()
                information.append(x)
        if information:
            vehicles = []
            vehicle_info = [x for x in information if len(x.split()) > 2]
            for x in vehicle_info:
                info = x.split()
                vin = info[-1].strip() if len(info[-1]) == 17 else None
                info.remove(vin) if vin else None
                model_info = info[2:]
                model = ' '.join(map(str, model_info)).strip()
                vehicles.append({'year': int(info[0]),
                                 'make': info[1].strip(),
                                 'model': model,
                                 'vin': vin})
        return vehicles

    async def __get_vehicle_info(self):
        vehicles = None
        vehicle_info = None
        if self.section.VEHICLE in self.form_fields:
            vehicle_info = self.form_fields[self.section.VEHICLE]
        elif self.section.VEHICLE_BI_LINGUAL in self.indexof:
            vehicle_info = self.pdf_helper.metadata[self.indexof[self.section.VEHICLE_BI_LINGUAL] - 2][PDF.TEXT]
        if vehicle_info:
            vehicles = await self.__get_vehicles(vehicle_info)
        return vehicles

    async def __get_signature(self):
        try:
            signature = None
            if self.section.SIGNATURE in self.page_text or self.section.SIGNATURE_BI_LINGUAL in self.page_text:
                text_bbox = tuple(filter(lambda x: self.section.SIGNATURE in x[PDF.TEXT].strip() or
                                                   self.section.SIGNATURE_BI_LINGUAL in x[PDF.TEXT].strip(),
                                         self.pdf_helper.metadata))
                bboxes = tuple(x[1:] for x in text_bbox)
                signature_placeholder_bbox = bboxes[0][0]
                x0, y0, x1, y1 = self.padding[self.section.SIGNATURE] if self.section.SIGNATURE in text_bbox \
                    else self.padding[self.section.SIGNATURE_BI_LINGUAL]

                if signature_placeholder_bbox:
                    bbox = await self.pdf_helper.apply_bbox_padding(page_no=0, bbox=signature_placeholder_bbox,
                                                                    x0_pad=x0, y0_pad=y0, x1_pad=x1, y1_pad=y1)
                    page_signatures = await self.pdf_helper.get_images_by_page(page_no=0)
                    is_signed = await self.signature_validator.validate(doc=self.pdf_helper.converted_doc,
                                                                        section_bbox=bbox,
                                                                        images=page_signatures,
                                                                        page=self.pdf_helper.converted_doc[0])
                    signature = {'is_signed': is_signed}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            signature = None
        return signature

    async def extract(self):
        data = {self.response_key.ARTISAN_USE_LETTER: None}
        self.page_text = self.doc[0].get_textpage().extractText()
        self.form_fields = await self.pdf_helper.get_form_fields_by_page(0)
        if self.section.VALID_DOCUMENT_KEY in self.page_text or self.section.VALID_DOCUMENT_KEY_BI_LINGUAL in self.page_text:
            insured_name, policy_number, vehicles, signature = await asyncio.gather(self.__get_insured_name(),
                                                                                    self.__get_policy_number(),
                                                                                    self.__get_vehicle_info(),
                                                                                    self.__get_signature())
            data[self.response_key.ARTISAN_USE_LETTER] = {self.response_key.INSURED_NAME: insured_name,
                                                          self.response_key.POLICY_NUMBER: policy_number,
                                                          self.response_key.VEHICLES: vehicles,
                                                          self.response_key.SIGNATURES: signature}
        else:
            logger.warning(f'Request ID: [{self.uuid}] ')
            raise InvalidPDFStructureTypeException(self.uuid)
        logger.info(f'Request ID: [{self.uuid}] Response: {data}')
        return data
