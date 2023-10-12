import io

from app.service.api.v1.artisan_use_letter import extract_v1

uuid = '89c5de1c-4d25-11ec-8623-d1e221452fcd'
filepath = 'app/data/temp/test_data/ARTISAN USE LETTER.pdf'
bilingual_filepath = 'app/data/temp/test_data/01ArtisanBilingual(01_10_2022).pdf'


async def test_get_insured_name_valid():
    f = open(filepath, "rb")
    file = io.BytesIO(f.read())
    response = "Ramon Hernandez Rodriguez"
    obj = extract_v1.AULDataPointExtractorV1(uuid=uuid, file=file)
    obj.form_fields = await obj.pdf_helper.get_form_fields_by_page(0)
    x = await obj._AULDataPointExtractorV1__get_insured_name()
    assert x == response


async def test_get_insured_name_valid_bilingual():
    f = open(bilingual_filepath, "rb")
    file = io.BytesIO(f.read())
    response = "J GUADALUPE CASTRO-LOPEZ"
    obj = extract_v1.AULDataPointExtractorV1(uuid=uuid, file=file)
    obj.form_fields = await obj.pdf_helper.get_form_fields_by_page(0)
    x = await obj._AULDataPointExtractorV1__get_insured_name()
    assert x == response


async def test_get_policy_number_valid():
    f = open(filepath, "rb")
    file = io.BytesIO(f.read())
    response = '104601640239001'
    obj = extract_v1.AULDataPointExtractorV1(uuid=uuid, file=file)
    obj.form_fields = await obj.pdf_helper.get_form_fields_by_page(0)
    x = await obj._AULDataPointExtractorV1__get_policy_number()
    assert x == response


async def test_get_policy_number_valid_bilingual():
    f = open(bilingual_filepath, "rb")
    file = io.BytesIO(f.read())
    response = 'MIL3685635'
    obj = extract_v1.AULDataPointExtractorV1(uuid=uuid, file=file)
    obj.form_fields = await obj.pdf_helper.get_form_fields_by_page(0)
    x = await obj._AULDataPointExtractorV1__get_policy_number()
    assert x == response



async def test_get_vehicle_info_valid():
    f = open(filepath, "rb")
    file = io.BytesIO(f.read())
    response = [{'make': 'Ford', 'model': 'F250', 'vin': None, 'year': 2017}]
    obj = extract_v1.AULDataPointExtractorV1(uuid=uuid, file=file)
    obj.form_fields = await obj.pdf_helper.get_form_fields_by_page(0)
    x = await obj._AULDataPointExtractorV1__get_vehicle_info()
    assert x == response


async def test_get_vehicle_info_valid_bilingual():
    f = open(bilingual_filepath, "rb")
    file = io.BytesIO(f.read())
    response = [{'make': 'CHEV', 'model': 'EXPRESS', 'vin': None, 'year': 2007}]
    obj = extract_v1.AULDataPointExtractorV1(uuid=uuid, file=file)
    obj.form_fields = await obj.pdf_helper.get_form_fields_by_page(0)
    x = await obj._AULDataPointExtractorV1__get_vehicle_info()
    assert x == response


async def test_get_signature_valid():
    f = open(filepath, "rb")
    file = io.BytesIO(f.read())
    response = {'is_signed': False}
    obj = extract_v1.AULDataPointExtractorV1(uuid=uuid, file=file)
    obj.page_text = obj.doc[0].get_textpage().extractText()
    x = await obj._AULDataPointExtractorV1__get_signature()
    assert x == response


async def test_get_signature_invalid():
    f = open(bilingual_filepath, "rb")
    file = io.BytesIO(f.read())
    response = {'is_signed': True}
    obj = extract_v1.AULDataPointExtractorV1(uuid=uuid, file=file)
    obj.page_text = obj.doc[0].get_textpage().extractText()
    x = await obj._AULDataPointExtractorV1__get_signature()
    assert x == response
