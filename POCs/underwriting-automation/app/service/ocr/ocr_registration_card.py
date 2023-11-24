from datetime import datetime

import cv2
import numpy as np
import pytesseract

from app import app
from app import logger
from app.constant import OCRConfig
from app.service.helper.parser import parse_validity_date, \
    parse_vin, parse_make, parse_year, parse_history, parse_registration_name
from app.service.ocr.ocr_abc import OCRAbc

pytesseract.pytesseract.tesseract_cmd = app.config.TESSERACT_PATH


class OCRRegistrationCard(OCRAbc):
    def __init__(self, uuid):
        self.uuid = uuid

    async def get_year(self, image):
        image = await self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.Registration.YEAR, lang='eng')
        return parse_year(text)

    async def get_make(self, image):
        image = await self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.Registration.MAKE, lang='eng')
        return parse_make(text)

    async def get_model(self, image):
        image = await self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.Registration.MODEL, lang='eng')
        return text

    async def get_vin(self, image):
        image = await self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.Registration.VIN, lang='eng')
        return parse_vin(text)

    async def get_owner_names(self, image):
        image = await self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.Registration.NAME, lang='eng')
        return parse_registration_name(text)

    async def get_history(self, image):
        image = await self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.Registration.HISTORY, lang='eng')
        return parse_history(text)

    async def get_validity(self, image):
        _image = await self._apply_preprocessing(image)
        text = pytesseract.image_to_string(_image, config=OCRConfig.Registration.DATE, lang='eng')
        date = parse_validity_date(text)

        if not date:
            print(f'Request ID: [{self.uuid}] Applying Color Mask:[back]')
            _image_black = await self._apply_black_color_mask(image)
            text = pytesseract.image_to_string(_image_black, config=OCRConfig.Registration.DATE, lang='eng')
            date = parse_validity_date(text)

        if not date:
            print(f'Request ID: [{self.uuid}] Applying Color Mask:[gray]')
            _image_gray = await self._apply_gray_color_mask(image)
            text = pytesseract.image_to_string(_image_gray, config=OCRConfig.Registration.DATE, lang='eng')
            date = parse_validity_date(text)

        if not date:
            print(f'Request ID: [{self.uuid}] Applying Color Mask:[dark gray]')
            _image_dark_gray = await self._apply__dark_gray_color_mask(image)
            text = pytesseract.image_to_string(_image_dark_gray, config=OCRConfig.Registration.DATE, lang='eng')
            date = parse_validity_date(text)

        if not date:
            print(f'Request ID: [{self.uuid}] Applying Color Mask:[red]')
            _image_red = await self._apply_red_color_mask(image)
            text = pytesseract.image_to_string(_image_red, config=OCRConfig.Registration.DATE, lang='eng')
            date = parse_validity_date(text)

        if not date:
            print(f'Request ID: [{self.uuid}] Applying Color Mask:[dark red]')
            _image_dark_red = await self._apply_dark_red_color_mask(image)
            text = pytesseract.image_to_string(_image_dark_red, config=OCRConfig.Registration.DATE, lang='eng')
            date = parse_validity_date(text)

        return date > datetime.utcnow() if date else None
