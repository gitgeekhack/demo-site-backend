from app.service.api.v1.pleasure_use_letter import extract_v1
import fitz
from app import app
import pytest
from app.constant import PleasureUseLetterTemplate, InsuranceCompany
import io

doc = fitz.open('app/data/temp/test_data/VER_PLEASURE_LETTER_Alfonso Soto.pdf', filetype="pdf")
page = doc[0]
blocks = page.get_text().split('\n')
temp = blocks.index(PleasureUseLetterTemplate.TEMPLATE_DELIMINATOR)
text = blocks[temp + 1:]
uuid = '89c5de1c-4d25-11ec-8623-d1e221452fcd'
filepath = 'app/data/temp/test_data/VER_PLEASURE_LETTER_Alfonso Soto.pdf'
invalid_file = 'app/data/temp/test_data/BROKER_PKG_Alfonso Soto.pdf'


async def test_get_company_and_insured_name_valid():
    f = open(filepath, "rb")
    file = io.BytesIO(f.read())
    response = (InsuranceCompany.ALLIANCE_UNITED.value, "ALFONSO SOTO")
    obj = extract_v1.PULDataPointExtractorV1(uuid=uuid, file=file)
    x = await obj._PULDataPointExtractorV1__get_company_and_insured_name(text)
    assert x == response


async def test_get_company_and_insured_name_invalid():
    f = open(filepath, "rb")
    file = io.BytesIO(f.read())
    response = "ALFONSO SOTO"
    obj = extract_v1.PULDataPointExtractorV1(uuid=uuid, file=file)
    x = await obj._PULDataPointExtractorV1__get_company_and_insured_name(text)
    assert not x == response


async def test_get_policy_number_valid():
    f = open(filepath, "rb")
    file = io.BytesIO(f.read())
    response = "MIL4972270"
    obj = extract_v1.PULDataPointExtractorV1(uuid=uuid, file=file)
    x = await obj._PULDataPointExtractorV1__get_policy_number(text)
    assert x == response


async def test_get_vehicle_info_invalid():
    f = open(filepath, "rb")
    file = io.BytesIO(f.read())
    text = ['ALFONSO SOTO', 'ALLIANCE UNITED', '2008 TOYT RAV4 JTMZD33V385100497', '2017 HOND ACCORD 1HGCR2F38HA088268']
    obj = extract_v1.PULDataPointExtractorV1(uuid=uuid, file=file)
    x = await obj._PULDataPointExtractorV1__get_vehicle_info(text)
    assert not x


async def test_get_vehicle_info_valid():
    f = open(filepath, "rb")
    file = io.BytesIO(f.read())
    response = [
        {
            "year": 2008,
            "make": "TOYT",
            "model": "RAV4",
            "vin": "JTMZD33V385100497"
        },
        {
            "year": 2017,
            "make": "HOND",
            "model": "ACCORD",
            "vin": "1HGCR2F38HA088268"
        },
        {
            "year": 1996,
            "make": "MAZD",
            "model": "B2300",
            "vin": "4F4CR12A1TTM48823"
        },
        {
            "year": 2004,
            "make": "TOYT",
            "model": "SIENNA",
            "vin": None
        }
    ]
    obj = extract_v1.PULDataPointExtractorV1(uuid=uuid, file=file)
    x = await obj._PULDataPointExtractorV1__get_vehicle_info(text)
    assert x == response


async def test_get_vehicle_info_invalid():
    f = open(filepath, "rb")
    file = io.BytesIO(f.read())
    text = ['ALFONSO SOTO', 'ALLIANCE UNITED', '2008']
    obj = extract_v1.PULDataPointExtractorV1(uuid=uuid, file=file)
    x = await obj._PULDataPointExtractorV1__get_vehicle_info(text)
    assert not x


async def test_get_vehicle_info_invalid():
    f = open(filepath, "rb")
    file = io.BytesIO(f.read())
    text = ['ALFONSO SOTO', 'ALLIANCE UNITED', '2008',
            '2008 TOYT SIENNA 98938488484884899, 2088 TOYT SIENNA 98938488484884899,2098 TOYT SIENNA 98938488484884899']
    response = [{'year': 2008, 'make': 'TOYT', 'model': 'SIENNA', 'vin': '98938488484884899'},
                {'year': 2088, 'make': 'TOYT', 'model': 'SIENNA', 'vin': '98938488484884899'},
                {'year': 2098, 'make': 'TOYT', 'model': 'SIENNA', 'vin': '98938488484884899'}]
    obj = extract_v1.PULDataPointExtractorV1(uuid=uuid, file=file)
    x = await obj._PULDataPointExtractorV1__get_vehicle_info(text)
    assert x == response


async def test_get_signature_valid():
    f = open(filepath, "rb")
    file = io.BytesIO(f.read())
    response = {'is_signed': True}
    obj = extract_v1.PULDataPointExtractorV1(uuid=uuid, file=file)
    x = await obj._PULDataPointExtractorV1__get_signature()
    assert x == response


async def test_get_signature_invalid():
    f = open(invalid_file, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.PULDataPointExtractorV1(uuid=uuid, file=file)
    x = await obj._PULDataPointExtractorV1__get_signature()
    assert not x
