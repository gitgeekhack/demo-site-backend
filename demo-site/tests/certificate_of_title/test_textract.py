import os
import pytest

os.chdir('../../')
from app.service.helper import textract

pytest_plugins = ('pytest_asyncio',)


class TestTextractHelper:
    @pytest.mark.asyncio
    async def test_get_textract_response_with_valid_parameter(self):
        extractor = textract.TextractHelper()
        image_path = 'tests/data/image/alabama_front.jpg'
        result = extractor.get_textract_response(image_path)
        assert result is not None

    @pytest.mark.asyncio
    async def test_get_textract_response_with_invalid_parameter(self):
        extractor = textract.TextractHelper()
        image_path = 'tests/data/pdf/Sample1.pdf'
        try:
            extractor.get_textract_response(image_path)
        except:
            assert True
