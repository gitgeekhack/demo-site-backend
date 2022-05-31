import csv
import os

import pytesseract
import cv2

from app.common.utils import MonoState
from app.constant import OCRConfig, Parser
from app.service.helper.certificate_of_title_helper import apply_preprocessing, text_detection, noise_removal
from app.service.helper.parser import parse_title_number, parse_vin, parse_year, parse_make, parse_model, \
    parse_body_style, parse_owner_name, parse_address, parse_lien_name, parse_odometer_reading, \
    parse_doc_type, parse_title_type, parse_remarks, parse_issue_date

pytesseract.pytesseract.tesseract_cmd = os.getenv('Tesseract_PATH')


def load_us_cities():
    with open(Parser.WORLD_CITIES_LIST, newline='') as csvfile:
        reader = csv.reader(csvfile)
        us_cities = [row[0] for row in reader if row[4] == 'United States']
    return us_cities


class CertificateOfTitleOCR(MonoState):
    _internal_state = {'us_cities': load_us_cities()}

    async def get_title_number(self, image):
        image = await apply_preprocessing(image, auto_scaling=True, resize_dimension=500)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.TITLE_NO, lang='eng')
        return parse_title_number(text)

    async def get_vin(self, image):
        image = await apply_preprocessing(image, auto_scaling=True, resize_dimension=500)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.VIN, lang='eng')
        return parse_vin(text)

    async def get_year(self, image):
        image = await apply_preprocessing(image, auto_scaling=True, resize_dimension=500)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.YEAR_PSM11, lang='eng')
        year = parse_year(text)
        if not year:
            text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.YEAR_PSM6, lang='eng')
        year = parse_year(text)
        return year

    async def get_make(self, image):
        pre_image = await apply_preprocessing(image, auto_scaling=True, resize_dimension=320)
        clean_image = await noise_removal(pre_image)
        images = await text_detection(clean_image)
        text = ''
        for i_image in images:
            text = text + ' ' + pytesseract.image_to_string(i_image, config=OCRConfig.CertificateOfTitle.MAKE)
        return parse_make(text)

    async def get_model(self, image):
        pre_image = await apply_preprocessing(image, auto_scaling=True, resize_dimension=320)
        clean_image = await noise_removal(pre_image)
        images = await text_detection(clean_image)
        text = ''
        for i_image in images:
            text = text + ' ' + pytesseract.image_to_string(i_image, config=OCRConfig.CertificateOfTitle.MODEL)
        return parse_model(text)

    async def get_body_style(self, image):
        pre_image = await apply_preprocessing(image, auto_scaling=True, resize_dimension=320)
        clean_image = await noise_removal(pre_image)
        text = pytesseract.image_to_string(clean_image, config=OCRConfig.CertificateOfTitle.BODY_STYLE)
        return parse_body_style(text)

    async def get_odometer_reading(self, image):
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.ODOMETER, lang='eng')
        odometer = parse_odometer_reading(text)
        if not odometer:
            image = await apply_preprocessing(image, auto_scaling=True, resize_dimension=400)
            text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.ODOMETER, lang='eng')
            odometer = parse_odometer_reading(text)
        return odometer

    async def get_owner_name(self, image):
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.NAME, lang='eng')
        return parse_owner_name(text)

    async def get_address(self, image):
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.ADDRESS, lang='eng')
        return parse_address(text, cities=self.us_cities)

    async def get_lien_address(self, image):
        image = await apply_preprocessing(image, auto_scaling=True, resize_dimension=500)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.ADDRESS, lang='eng')
        return parse_address(text, cities=self.us_cities)

    async def get_lien_name(self, image):
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.NAME, lang='eng')
        return parse_lien_name(text)

    async def get_date(self, image):
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.DATE, lang='eng')
        date = parse_issue_date(text)
        if not date:
            image = await apply_preprocessing(image, auto_scaling=True, resize_dimension=400)
            text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.DATE, lang='eng')
            date = parse_issue_date(text)
        return date

    async def get_doc_type(self, image):
        image = await apply_preprocessing(image, auto_scaling=True, resize_dimension=500)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.DOCUMENT_TYPE, lang='eng')
        return parse_doc_type(text)

    async def get_title_type(self, image):
        image = await apply_preprocessing(image, auto_scaling=True, resize_dimension=500)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.TITLE_TYPE, lang='eng')
        return parse_title_type(text)

    async def get_remark(self, image):
        image = await apply_preprocessing(image, auto_scaling=True, resize_dimension=500)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.REMARK, lang='eng')
        return parse_remarks(text)
