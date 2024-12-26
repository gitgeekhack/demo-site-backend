import os
import uuid
import pytest

os.chdir('../../')
from app.service.certificate_of_title import extract
from app.common import utils

pytest_plugins = ('pytest_asyncio',)


class TestCOTDataPointExtractorV1:
    @pytest.mark.asyncio
    async def test_is_black_and_white_with_black_and_white_image(self):
        test_logger = utils.get_logger()
        test_uuid = str(uuid.uuid4())
        extractor = extract.COTDataPointExtractorV1(uuid=test_uuid)

        image_path = 'tests/data/image/idaho_bw.jpg'

        result = await extractor.is_black_and_white(test_logger, image_path)
        assert result is not None

    @pytest.mark.asyncio
    async def test_is_black_and_white_with_colourful_image(self):
        test_logger = utils.get_logger()
        test_uuid = str(uuid.uuid4())
        extractor = extract.COTDataPointExtractorV1(uuid=test_uuid)

        image_path = 'tests/data/image/idaho.jpg'

        result = await extractor.is_black_and_white(test_logger, image_path)
        assert result is not None

    @pytest.mark.asyncio
    async def test_is_black_and_white_with_invalid_parameter(self):
        test_logger = utils.get_logger()
        test_uuid = str(uuid.uuid4())
        extractor = extract.COTDataPointExtractorV1(uuid=test_uuid)

        pdf_path = 'tests/data/xyz/sample1.jpg'

        try:
            await extractor.is_black_and_white(test_logger, pdf_path)
        except FileNotFoundError:
            assert True

    @pytest.mark.asyncio
    async def test_convert_str_to_json_with_valid_parameter(self):
        test_uuid = str(uuid.uuid4())
        extractor = extract.COTDataPointExtractorV1(uuid=test_uuid)

        text = ' Here is the extracted data from the given text filled in the provided JSON format:\n\n{\n  "lienholders": [\n    {\n      "lienholderName": "IVY FUNDING COMPANY LLC",  \n      "lienholderAddress": {\n        "Street": "2741 S 14TH ST",\n        "City": "ABILENE",\n        "State": "TX",\n        "Zipcode": "79605"\n      },\n      "LienDate": "03/17/2023"      \n    },\n    {\n      "lienholderName": "TITLEMAX OF TEXAS INC DBA TITLEMAX",\n      "lienholderAddress": {\n        "Street": "2741 S 14TH ST", \n        "City": "ABILENE",\n        "State": "TX",\n        "Zipcode": "79605"  \n      },\n      "LienDate": "03/17/2023"\n    }\n  ],\n  "TitleNo": "",\n  "Vin": "WDDZF4JB2HA171793",\n  "Year": "2017",\n  "Make": "MERZ",\n  "Model": "E30",\n  "BodyStyle": "4D",\n  "OdometerReading": "107691",\n  "IssueDate": "04/13/2023",\n  "Owners":"DANIELLE MARIE HENDERSON",\n  "OwnerNameList": [\n    "DANIELLE MARIE HENDERSON"\n  ], \n  "OwnerAddress": {\n    "Street": "1074 FM 126",\n    "City": "MERKEL",\n    "State": "TX", \n    "Zipcode": "79536"\n  },\n  "DocumentType": "",\n  "TitleType": "",\n  "OdometerBrand": "ACTUAL",\n  "LicensePlate": "",\n  "TitledState": "Texas"\n}'

        result = await extractor._COTDataPointExtractorV1__convert_str_to_json(text)

        assert result is not None

    @pytest.mark.asyncio
    async def test_convert_str_to_json_with_invalid_parameter(self):
        test_uuid = str(uuid.uuid4())
        extractor = extract.COTDataPointExtractorV1(uuid=test_uuid)

        text = 12345

        try:
            await extractor._COTDataPointExtractorV1__convert_str_to_json(text)
        except AttributeError:
            assert True

    @pytest.mark.asyncio
    async def test_parse_date_of_dd_mm_yy_format(self):
        test_uuid = str(uuid.uuid4())
        extractor = extract.COTDataPointExtractorV1(uuid=test_uuid)
        date = "13/04/2023"
        result = await extractor._COTDataPointExtractorV1__parse_date(date)
        assert result == "04-13-2023"

    @pytest.mark.asyncio
    async def test_parse_date_of_mm_dd_yy_format(self):
        test_uuid = str(uuid.uuid4())
        extractor = extract.COTDataPointExtractorV1(uuid=test_uuid)
        date = "04/13/2023"
        result = await extractor._COTDataPointExtractorV1__parse_date(date)
        assert result == "04-13-2023"

    @pytest.mark.asyncio
    async def test_parse_date_of_int_format(self):
        test_uuid = str(uuid.uuid4())
        extractor = extract.COTDataPointExtractorV1(uuid=test_uuid)
        date = 16082001
        try:
            await extractor._COTDataPointExtractorV1__parse_date(date)
        except TypeError:
            assert True

    @pytest.mark.asyncio
    async def test_get_ownership_type_with_or_and_format(self):
        test_uuid = str(uuid.uuid4())
        extractor = extract.COTDataPointExtractorV1(uuid=test_uuid)
        owners = 'John Doe or Jane Doe and Jack Smith'
        owners_name_list = ['John Doe', 'Jane Doe', 'Jack Smith']
        result = extractor._COTDataPointExtractorV1__get_ownership_type(owners, owners_name_list)
        assert result == "Joint Tenancy With Right Of Survivorship"

    @pytest.mark.asyncio
    async def test_get_ownership_type_with_or_format(self):
        test_uuid = str(uuid.uuid4())
        extractor = extract.COTDataPointExtractorV1(uuid=test_uuid)
        owners = 'John Doe or Jane Doe'
        owners_name_list = ['John Doe', 'Jane Doe']
        result = extractor._COTDataPointExtractorV1__get_ownership_type(owners, owners_name_list)
        assert result == "Joint Tenancy"

    @pytest.mark.asyncio
    async def test_get_ownership_type_without_or_and_format(self):
        test_uuid = str(uuid.uuid4())
        extractor = extract.COTDataPointExtractorV1(uuid=test_uuid)
        owners = 'John Doe, Jane Doe'
        owners_name_list = ['John Doe', 'Jane Doe']
        result = extractor._COTDataPointExtractorV1__get_ownership_type(owners, owners_name_list)
        assert result == "Tenancy In Common"

    @pytest.mark.asyncio
    async def test_get_ownership_type_with_single_string_format(self):
        test_uuid = str(uuid.uuid4())
        extractor = extract.COTDataPointExtractorV1(uuid=test_uuid)
        owners = 'John Doe'
        owners_name_list = ['John Doe']
        result = extractor._COTDataPointExtractorV1__get_ownership_type(owners, owners_name_list)
        assert result == "Sole tenancy"

    @pytest.mark.asyncio
    async def test_get_ownership_type_with_invalid_parameter(self):
        test_uuid = str(uuid.uuid4())
        extractor = extract.COTDataPointExtractorV1(uuid=test_uuid)
        owners = 1234
        owners_name_list = 'John Doe'
        try:
            extractor._COTDataPointExtractorV1__get_ownership_type(owners, owners_name_list)
        except AttributeError:
            assert True
