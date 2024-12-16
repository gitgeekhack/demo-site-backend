import os
import uuid
import pytest

os.chdir('../../')
from app.service.car_damage_detection import damage_detect

pytest_plugins = ('pytest_asyncio',)


class TestDamageDetector:
    @pytest.mark.asyncio
    async def test_detect_with_valid_parameter(self):
        test_uuid = str(uuid.uuid4())
        extractor = damage_detect.DamageDetector(uuid=test_uuid)

        image_path = ["tests/data/image/Nissan-frontside-view.jpg",
                      "tests/data/image/Nissan-front-rightside-view.jpg"]
        result = await extractor.detect(image_path)

        assert result is not None

    @pytest.mark.asyncio
    async def test_detect_with_invalid_parameter(self):
        test_uuid = str(uuid.uuid4())
        extractor = damage_detect.DamageDetector(uuid=test_uuid)

        image_path = 12345

        try:
            await extractor.detect(image_path)
        except:
            assert True
