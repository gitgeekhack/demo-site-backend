import os
import pytest
os.chdir('../../')
import cv2
import numpy as np
from app.service.helper import cv_helper

pytest_plugins = ('pytest_asyncio',)


class TestCVHelper:
    @pytest.mark.asyncio
    async def test_get_object_with_valid_parameter(self):
        extractor = cv_helper.CVHelper()
        image_path = 'tests/data/image/minnesota_license.jpg'
        image = cv2.imread(image_path)
        coordinates = np.array([244.12, 193.16, 463.87, 242.86], dtype=np.float32)
        label = 'license_number'
        result = await extractor.get_object(image, coordinates, label)
        assert result is not None

    @pytest.mark.asyncio
    async def test_get_object_with_invalid_parameter(self):
        extractor = cv_helper.CVHelper()
        pdf_path = 'tests/data/pdf/Sample1.pdf'
        coordinates = np.array([244.12, 193.16, 463.87, 242.86], dtype=np.float32)
        label = 'license_number'
        try:
            await extractor.get_object(pdf_path, coordinates, label)
        except AttributeError:
            assert True

    @pytest.mark.asyncio
    async def test_calculate_iou_with_valid_parameter(self):
        extractor = cv_helper.CVHelper()
        x = np.array([241.88, 237.17, 445, 269.46], dtype=np.float32)
        y = np.array([288.89, 293.36, 465.92, 343.05], dtype=np.float32)
        result = await extractor.calculate_iou(x, y)
        assert result is not None

    @pytest.mark.asyncio
    async def test_calculate_iou_with_invalid_parameter(self):
        extractor = cv_helper.CVHelper()
        x = np.array([241.88, 237.17, 445, 269.46, "string value"], dtype=object)
        y = np.array([288.89, 293.36, 465.92, 343.05, "string value"], dtype=object)
        try:
            await extractor.calculate_iou(x, y)
        except:
            assert True

    @pytest.mark.asyncio
    async def test_find_skew_score_with_valid_parameter(self):
        extractor = cv_helper.CVHelper()
        arr = np.array([
            [0, 0, 255, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 255, 255, 0],
            [255, 0, 0, 0, 255],
            [255, 0, 0, 0, 0]
        ], dtype=np.uint8)
        angle = -45
        result = await extractor._find_skew_score(arr, angle)
        assert result is not None

    @pytest.mark.asyncio
    async def test_find_skew_score_with_invalid_parameter(self):
        extractor = cv_helper.CVHelper()
        arr = np.array([
            [0, 0, 255, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 255, 255, 0],
            [255, 0, 0, 0, 255],
            [255, 0, 0, 0, 0],
            "invalid input"
        ], dtype=object)
        angle = -45
        try:
            await extractor._find_skew_score(arr, angle)
        except:
            assert True

    @pytest.mark.asyncio
    async def test_calculate_skew_angle_with_valid_parameter(self):
        extractor = cv_helper.CVHelper()
        image_path = 'tests/data/image/calculate_skew_angle.jpg'
        image = cv2.imread(image_path)
        result = await extractor._calculate_skew_angel(image)
        assert result is not None

    @pytest.mark.asyncio
    async def test_calculate_skew_angle_with_invalid_parameter(self):
        extractor = cv_helper.CVHelper()
        txt_path = 'tests/data/text/sample.txt'
        try:
            await extractor._calculate_skew_angel(txt_path)
        except:
            assert True

    @pytest.mark.asyncio
    async def test_fix_skew_with_valid_parameter(self):
        extractor = cv_helper.CVHelper()
        image_path = 'tests/data/image/minnesota_license.jpg'
        image = cv2.imread(image_path)
        skew_angle = 0
        result = await extractor.fix_skew(image, skew_angle)
        assert result is not None

    @pytest.mark.asyncio
    async def test_fix_skew_with_invalid_parameter(self):
        extractor = cv_helper.CVHelper()
        txt_path = 'tests/data/text/sample.txt'
        skew_angle = 0
        try:
            await extractor.fix_skew(txt_path, skew_angle)
        except AttributeError:
            assert True

    @pytest.mark.asyncio
    async def test_automatic_enhancement_with_valid_parameter(self):
        extractor = cv_helper.CVHelper()
        img_path = 'tests/data/image/minnesota_license.jpg'
        image = cv2.imread(img_path)
        result = await extractor.automatic_enhancement(image)
        assert result is not None

    @pytest.mark.asyncio
    async def test_automatic_enhancement_with_invalid_parameter(self):
        extractor = cv_helper.CVHelper()
        pdf_path = 'tests/data/pdf/Sample1.pdf'
        try:
            await extractor.automatic_enhancement(pdf_path)
        except:
            assert True
