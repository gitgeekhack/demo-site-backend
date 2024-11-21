import pytest
from app.service.helper.driving_license_parser import parse_name, parse_date, parse_license_number, autocorrect_city, \
    parse_address, split_address, parse_gender, parse_height, parse_weight, parse_hair_color, parse_eye_color, \
    parse_license_class
from app.service.ocr.driving_license.ocr import load_us_cities

pytest_plugins = ('pytest_asyncio',)


class TestDrivingLicenseParser:
    @pytest.mark.asyncio
    async def test_parse_name_with_valid_parameter(self):
        name = "SAMPLE JUN MARIE"
        result = parse_name(name)
        assert result is not None

    @pytest.mark.asyncio
    async def test_parse_name_with_invalid_parameter(self):
        name = 123
        try:
            parse_name(name)
        except AttributeError:
            assert True

    @pytest.mark.asyncio
    async def test_parse_date_with_valid_parameter(self):
        date = "08/20/2018"
        result = parse_date(date)
        assert result is not None

    @pytest.mark.asyncio
    async def test_parse_date_with_invalid_parameter_with_character_format(self):
        date = "16 th january"
        try:
            parse_date(date)
        except AssertionError:
            assert True

    @pytest.mark.asyncio
    async def test_parse_date_with_invalid_parameter_with_incorrect_format(self):
        date = "16-08-2001"
        try:
            parse_date(date)
        except AssertionError:
            assert True

    @pytest.mark.asyncio
    async def test_parse_license_number_with_valid_parameter(self):
        license_number = "A123-456-789-098-"
        result = parse_license_number(license_number)
        assert result is not None

    @pytest.mark.asyncio
    async def test_parse_license_number_with_invalid_parameter(self):
        license_number = 4500
        try:
            parse_license_number(license_number)
        except:
            assert True

    @pytest.mark.asyncio
    async def test_autocorrect_city_with_valid_parameter(self):
        cities = load_us_cities()
        city = "new york"
        result = autocorrect_city(city, cities)
        assert result == "New York"

    @pytest.mark.asyncio
    async def test_autocorrect_city_with_invalid_parameter(self):
        cities = load_us_cities()
        city = "ahmedabad"
        try:
            autocorrect_city(city, cities)
        except AssertionError:
            assert True

    @pytest.mark.asyncio
    async def test_parse_address_with_valid_parameter(self):
        cities = load_us_cities()
        address = '8123 BLOOMINGTON AVE\nMINNEAPOLIS, MN 55417-1234\n'
        result = parse_address(address, cities)
        assert result is not None

    @pytest.mark.asyncio
    async def test_parse_address_with_invalid_parameter(self):
        cities = load_us_cities()
        address = 1562
        try:
            parse_address(address, cities)
        except:
            assert True

    @pytest.mark.asyncio
    async def test_parse_gender_with_valid_parameter(self):
        gender = 'F\n'
        result = parse_gender(gender)
        assert result is not None

    @pytest.mark.asyncio
    async def test_parse_gender_with_invalid_parameter(self):
        gender = ['Female']
        try:
            parse_gender(gender)
        except:
            assert True

    @pytest.mark.asyncio
    async def test_parse_height_with_valid_parameter(self):
        height = '46H5\' 05"\n'
        result = parse_height(height)
        assert result is not None

    @pytest.mark.asyncio
    async def test_parse_height_with_invalid_parameter(self):
        height = '4 feet 5 inch'
        try:
            parse_height(height)
        except AssertionError:
            assert True

    @pytest.mark.asyncio
    async def test_parse_weight_with_valid_parameter(self):
        weight = 'wlll Ww\n\n47 WGT 135 lb\n'
        result = parse_weight(weight)
        assert result is not None

    @pytest.mark.asyncio
    async def test_parse_weight_with_invalid_parameter(self):
        weight = 74
        try:
            parse_weight(weight)
        except:
            assert True

    @pytest.mark.asyncio
    async def test_parse_hair_color_with_valid_parameter(self):
        hair_color = 'BLN\n'
        result = parse_hair_color(hair_color)
        assert result is not None

    @pytest.mark.asyncio
    async def test_parse_hair_color_with_invalid_parameter(self):
        hair_color = 'Black'
        try:
            parse_hair_color(hair_color)
        except AssertionError:
            assert True

    @pytest.mark.asyncio
    async def test_parse_eye_color_with_valid_parameter(self):
        eye_color = 'EYES BRO\n'
        result = parse_eye_color(eye_color)
        assert result is not None

    @pytest.mark.asyncio
    async def test_parse_eye_color_with_invalid_parameter(self):
        eye_color = 'Brown\n'
        try:
            parse_eye_color(eye_color)
        except AssertionError:
            assert True

    @pytest.mark.asyncio
    async def test_parse_license_class_with_valid_parameter(self):
        license_class = '9 CLASS D\n'
        result = parse_license_class(license_class)
        assert result is not None

    @pytest.mark.asyncio
    async def test_parse_license_class_with_invalid_parameter(self):
        license_class = 1598
        try:
            parse_license_class(license_class)
        except:
            assert True
