import os

import cv2
import numpy as np
import pytesseract
from app.constant import OCRConfig
from app.service.helper.parser import parse_title_number, parse_vin, parse_year, parse_make, parse_model, \
    parse_body_style, parse_date, parse_owner_name, parse_address, parse_lien_name, parse_odometer_reading, \
    parse_doc_type, parse_title_type

pytesseract.pytesseract.tesseract_cmd = os.getenv('Tesseract_PATH')


class CertificateOfTitleOCR():
    async def _apply_preprocessing(self, image):
        h, w, c = image.shape
        if h > 640 or w > 640:
            image = cv2.resize(image, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
        else:
            image = cv2.resize(image, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blured1 = cv2.medianBlur(image, 3)
        blured2 = cv2.medianBlur(image, 51)
        divided = np.ma.divide(blured1, blured2).data
        normed = np.uint8(255 * divided / divided.max())
        th, image = cv2.threshold(normed, 100, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        # stack = np.vstack((image, blured1, blured2, normed, image))
        # image = cv2.erode(image, np.ones((3, 3), np.uint8))
        # image = cv2.dilate(image, np.ones((2, 2), np.uint8))
        return image

    async def get_title_number(self, image):
        image = await self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.TITLE_NO, lang='eng')
        return parse_title_number(text)

    async def get_vin(self, image):
        image = await self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.VIN, lang='eng')
        return parse_vin(text)

    async def get_year(self, image):
        image = await self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.YEAR, lang='eng')
        return parse_year(text)
    
    async def get_make(self, image):
        image = await self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.MAKE, lang='eng')
        return parse_make(text)
    
    async def get_model(self, image):
        image = await self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.MODEL, lang='eng')
        return parse_model(text)
    
    async def get_body_style(self, image):
        image = await self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.BODY_STYLE, lang='eng')
        return parse_body_style(text)
    
    async def get_odometer_reading(self, image):
        image = await self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.ODOMETER, lang='eng')
        return parse_odometer_reading(text)
    
    async def get_owner_name(self, image):
        image = await self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.NAME, lang='eng')
        return parse_owner_name(text)
    
    async def get_address(self, image):
        image = await self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.ADDRESS, lang='eng')
        return parse_address(text)
    
    async def get_lien_name(self, image):
        image = await self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.NAME, lang='eng')
        return parse_lien_name(text)
    
    async def get_date(self, image):
        image = await self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.DATE, lang='eng')
        return parse_date(text)
    
    async def get_doc_type(self, image):
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.DOCUMENT_TYPE, lang='eng')
        return parse_doc_type(text)
    
    async def get_title_type(self, image):
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.TITLE_TYPE, lang='eng')
        return parse_title_type(text)
