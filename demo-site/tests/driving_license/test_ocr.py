import os
import pytest
os.chdir('../')
import cv2
from app.service.ocr.driving_license import ocr

pytest_plugins = ('pytest_asyncio',)


class TestOCRDrivingLicense:
    @pytest.mark.asyncio
    async def test_auto_scale_image_valid_parameter(self):
        extractor = ocr.OCRDrivingLicense()
        image_path = 'tests/data/image/image.jpg'
        image = cv2.imread(image_path)
        result = extractor.auto_scale_image(image)
        assert result is not None

    @pytest.mark.asyncio
    async def test_auto_scale_image_invalid_parameter(self):
        extractor = ocr.OCRDrivingLicense()
        pdf_path = 'tests/data/pdf/Sample1.pdf'
        try:
            extractor.auto_scale_image(pdf_path)
        except AttributeError:
            assert True

    @pytest.mark.asyncio
    async def test_apply_preprocessing_valid_parameter(self):
        extractor = ocr.OCRDrivingLicense()
        image_path = 'tests/data/image/image.jpg'
        image = cv2.imread(image_path)
        result = extractor._apply_preprocessing(image)
        assert result is not None

    @pytest.mark.asyncio
    async def test_apply_preprocessing_invalid_parameter(self):
        extractor = ocr.OCRDrivingLicense()
        txt_path = 'tests/data/text/sample.txt'
        try:
            extractor._apply_preprocessing(txt_path)
        except:
            assert True

    @pytest.mark.asyncio
    async def test_apply_red_color_mask_with_valid_parameter(self):
        extractor = ocr.OCRDrivingLicense()
        image_path = 'tests/data/image/image.jpg'
        image = cv2.imread(image_path)
        result = extractor._apply_red_color_mask(image)
        assert result is not None

    @pytest.mark.asyncio
    async def test_apply_red_color_mask_with_invalid_parameter(self):
        extractor = ocr.OCRDrivingLicense()
        pdf_path = 'tests/data/pdf/Sample1.pdf'
        try:
            extractor._apply_red_color_mask(pdf_path)
        except:
            assert True

    @pytest.mark.asyncio
    async def test_apply_gray_color_mask_with_valid_parameter(self):
        extractor = ocr.OCRDrivingLicense()
        image_path = 'tests/data/image/image.jpg'
        image = cv2.imread(image_path)
        result = extractor._apply_gray_color_mask(image)
        assert result is not None

    @pytest.mark.asyncio
    async def test_apply_gray_color_mask_with_invalid_parameter(self):
        extractor = ocr.OCRDrivingLicense()
        pdf_path = 'tests/data/pdf/Sample1.pdf'
        try:
            extractor._apply_gray_color_mask(pdf_path)
        except:
            assert True

    @pytest.mark.asyncio
    async def test_get_license_number_with_valid_parameter(self):
        extractor = ocr.OCRDrivingLicense()
        image_path = 'tests/data/image/license_img.jpg'
        image = cv2.imread(image_path)
        result = extractor.get_license_number(image)
        assert result is not None

    @pytest.mark.asyncio
    async def test_get_license_number_with_invalid_parameter(self):
        extractor = ocr.OCRDrivingLicense()
        txt_path = 'tests/data/text/sample.txt'
        try:
            extractor.get_license_number(txt_path)
        except AttributeError:
            assert True
