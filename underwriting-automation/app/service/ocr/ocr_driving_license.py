import pytesseract

from app import app
from app import logger
from app.constant import OCRConfig
from app.service.helper.parser import parse_date, parse_name, parse_address, parse_license_number, parse_gender_dl
from app.service.ocr.ocr_abc import OCRAbc

pytesseract.pytesseract.tesseract_cmd = app.config.TESSERACT_PATH


class OCRDrivingLicense(OCRAbc):
    def __init__(self, uuid):
        self.uuid = uuid

    async def get_address(self, image):
        image = await self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.DrivingLicense.ADDRESS, lang='eng')
        return parse_address(text)

    async def get_name(self, image):
        image = await self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.DrivingLicense.NAME, lang='eng')
        return parse_name(text)

    async def get_date(self, image):
        _image = await self._apply_preprocessing(image)
        text = pytesseract.image_to_string(_image, config=OCRConfig.DrivingLicense.DATE, lang='eng')
        date = parse_date(text)

        if not date:
            logger.info(f'Request ID: [{self.uuid}] Applying Color Mask:[black]')
            _image_black = await self._apply_black_color_mask(image)
            text = pytesseract.image_to_string(_image_black, config=OCRConfig.DrivingLicense.DATE, lang='eng')
            date = parse_date(text)

        if not date:
            logger.info(f'Request ID: [{self.uuid}] Applying Color Mask:[gray]')
            _image_gray = await self._apply_gray_color_mask(image)
            text = pytesseract.image_to_string(_image_gray, config=OCRConfig.DrivingLicense.DATE, lang='eng')
            date = parse_date(text)

        if not date:
            logger.info(f'Request ID: [{self.uuid}] Applying Color Mask:[dark gray]')
            _image_dark_gray = await self._apply__dark_gray_color_mask(image)
            text = pytesseract.image_to_string(_image_dark_gray, config=OCRConfig.DrivingLicense.DATE, lang='eng')
            date = parse_date(text)

        if not date:
            logger.info(f'Request ID: [{self.uuid}] Applying Color Mask:[red]')
            _image_red = await self._apply_red_color_mask(image)
            text = pytesseract.image_to_string(_image_red, config=OCRConfig.DrivingLicense.DATE, lang='eng')
            date = parse_date(text)

        if not date:
            logger.info(f'Request ID: [{self.uuid}] Applying Color Mask:[dark red]')
            _image_dark_red = await self._apply_dark_red_color_mask(image)
            text = pytesseract.image_to_string(_image_dark_red, config=OCRConfig.DrivingLicense.DATE, lang='eng')
            date = parse_date(text)

        return date

    async def get_license(self, image):
        image = await self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.DrivingLicense.LICENSE_NO, lang='eng')
        return parse_license_number(text)

    async def get_gender(self, image):
        image = await self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.DrivingLicense.GENDER, lang='eng')
        return parse_gender_dl(text)
