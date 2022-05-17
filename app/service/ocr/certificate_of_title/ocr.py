import csv
import os

import cv2
import numpy as np
import pytesseract

from app.business_rule_exception import MissingRequiredParameter
from app.common.utils import MonoState
from app.constant import OCRConfig, Parser
from app.service.helper.parser import parse_title_number, parse_vin, parse_year, parse_make, parse_model, \
    parse_body_style, parse_date, parse_owner_name, parse_address, parse_lien_name, parse_odometer_reading, \
    parse_doc_type, parse_title_type, parse_remarks

pytesseract.pytesseract.tesseract_cmd = os.getenv('Tesseract_PATH')


def load_us_cities():
    with open(Parser.WORLD_CITIES_LIST, newline='') as csvfile:
        reader = csv.reader(csvfile)
        us_cities = [row[0] for row in reader if row[4] == 'United States']
    return us_cities


class CertificateOfTitleOCR(MonoState):
    _internal_state = {'us_cities': load_us_cities()}

    async def image_resize(self, image, width=None, height=None, interpolation=cv2.INTER_AREA):
        dim = None
        (h, w) = image.shape[:2]
        if width is None:
            r = height / float(h)
            dim = (int(w * r), height)
        else:
            r = width / float(w)
            dim = (width, int(h * r))
        resized = cv2.resize(image, dim, interpolation=interpolation)
        return resized

    async def auto_scale_image(self, image, resize_dimension=500):
        h, w, c = image.shape
        if resize_dimension:
            if w > h:
                image = await self.image_resize(image, width=resize_dimension, height=None, interpolation=cv2.INTER_CUBIC)
            else:
                image = await self.image_resize(image, width=None, height=resize_dimension, interpolation=cv2.INTER_CUBIC)
        return image

    async def _apply_preprocessing(self, image, auto_scaling=False, resize_dimension=None):
        if auto_scaling and resize_dimension:
            image = await self.auto_scale_image(image, resize_dimension=resize_dimension)
        if auto_scaling and not resize_dimension or not auto_scaling and resize_dimension:
            raise MissingRequiredParameter(message='Missing Required input Parameter for Image auto scaling')
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blured1 = cv2.medianBlur(image, 3)
        blured2 = cv2.medianBlur(image, 51)
        divided = np.ma.divide(blured1, blured2).data
        normed = np.uint8(255 * divided / divided.max())
        th, image = cv2.threshold(normed, 100, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        stack = np.vstack((image, blured1, blured2, normed, image))
        image = cv2.erode(image, np.ones((3, 3), np.uint8))
        image = cv2.dilate(image, np.ones((3, 3), np.uint8))
        return image

    async def get_title_number(self, image):
        image = await self._apply_preprocessing(image, auto_scaling=True, resize_dimension=500)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.TITLE_NO, lang='eng')
        return parse_title_number(text)

    async def get_vin(self, image):
        image = await self._apply_preprocessing(image, auto_scaling=True, resize_dimension=500)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.VIN, lang='eng')
        return parse_vin(text)

    async def get_year(self, image):
        image = await self._apply_preprocessing(image, auto_scaling=True, resize_dimension=500)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.YEAR_PSM11, lang='eng')
        year = parse_year(text)
        if not year:
            text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.YEAR_PSM6, lang='eng')
        year = parse_year(text)
        return year
    
    async def get_make(self, image):
        image = await self._apply_preprocessing(image, auto_scaling=True, resize_dimension=320)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.MAKE, lang='eng')
        return parse_make(text)
    
    async def get_model(self, image):
        image = await self._apply_preprocessing(image, auto_scaling=True, resize_dimension=360)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.MODEL, lang='eng')
        return parse_model(text)
    
    async def get_body_style(self, image):
        image = await self._apply_preprocessing(image, auto_scaling=True, resize_dimension=400)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.BODY_STYLE, lang='eng')
        return parse_body_style(text)
    
    async def get_odometer_reading(self, image):
        image = await self._apply_preprocessing(image, auto_scaling=True, resize_dimension=400)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.ODOMETER, lang='eng')
        return parse_odometer_reading(text)
    
    async def get_owner_name(self, image):
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.NAME, lang='eng')
        return parse_owner_name(text)
    
    async def get_address(self, image):
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.ADDRESS, lang='eng')
        return parse_address(text, cities=self.us_cities)
    
    async def get_lien_name(self, image):
        image = await self._apply_preprocessing(image, auto_scaling=True, resize_dimension=500)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.NAME, lang='eng')
        return parse_lien_name(text)
    
    async def get_date(self, image):
        image = await self._apply_preprocessing(image, auto_scaling=True, resize_dimension=500)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.DATE, lang='eng')
        return parse_date(text)
    
    async def get_doc_type(self, image):
        image = await self._apply_preprocessing(image, auto_scaling=True, resize_dimension=500)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.DOCUMENT_TYPE, lang='eng')
        return parse_doc_type(text)
    
    async def get_title_type(self, image):
        image = await self._apply_preprocessing(image, auto_scaling=True, resize_dimension=500)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.TITLE_TYPE, lang='eng')
        return parse_title_type(text)

    async def get_remark(self, image):
        image = await self._apply_preprocessing(image, auto_scaling=True, resize_dimension=500)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.REMARK, lang='eng')
        return parse_remarks(text)
