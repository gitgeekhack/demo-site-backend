import io
from app.service.api.v1.non_owners_letter import extract_v1
from app.constant import NonOwnersLetter, InsuranceCompany

uuid = '89c5de1c-4d25-11ec-8623-d1e221452fcd'
valid_file = 'app/data/temp/test_data/NON OWNERS LETTER.pdf'


async def test_get_data():
    f = open(valid_file, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.NOLDataPointExtractorV1(uuid=uuid, file=file)
    response = ['JOSELES GONZALEZ MOLINA', 'ALLIANCE UNITED', 'MIL6053575']
    x = await obj._NOLDataPointExtractorV1__get_data()
    assert x == response


async def test_check_token_set_ratio_valid():
    f = open(valid_file, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.NOLDataPointExtractorV1(uuid=uuid, file=file)
    response = True
    x = await obj._NOLDataPointExtractorV1__check_token_set_ratio('ALLIANCE', 'ALLIANCE UNITED')
    assert x == response


async def test_check_token_set_ratio_invalid():
    f = open(valid_file, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.NOLDataPointExtractorV1(uuid=uuid, file=file)
    x = await obj._NOLDataPointExtractorV1__check_token_set_ratio('INFINITY INS', 'ALLIANCE UNITED')
    assert not x


async def test_get_company_name_valid():
    f = open(valid_file, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.NOLDataPointExtractorV1(uuid=uuid, file=file)
    data = ['JOSELES GONZALEZ MOLINA', 'ALLIANCE', 'MIL6053575']
    response = InsuranceCompany.ALLIANCE_UNITED.value, 'ALLIANCE'
    x = await obj._NOLDataPointExtractorV1__get_company_name(data)
    assert x == response


async def test_get_company_name_invalid():
    f = open(valid_file, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.NOLDataPointExtractorV1(uuid=uuid, file=file)
    data = ['JOSELES GONZALEZ MOLINA', 'INFINITY INS', 'MIL6053575']
    response = None, None
    x = await obj._NOLDataPointExtractorV1__get_company_name(data)
    assert x == response


async def test_get_insured_name_valid1():
    f = open(valid_file, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.NOLDataPointExtractorV1(uuid=uuid, file=file)
    data = ['JOSELES GONZALEZ MOLINA', 'MIL6053575']
    response = 'JOSELES GONZALEZ MOLINA'
    x = await obj._NOLDataPointExtractorV1__get_insured_name(data)
    assert x == response


async def test_get_insured_name_valid2():
    f = open(valid_file, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.NOLDataPointExtractorV1(uuid=uuid, file=file)
    data = ['JOSELES GONZALEZ MOLINA', 'INFINITY INS', 'MIL6053575']
    response = 'JOSELES GONZALEZ MOLINA'
    x = await obj._NOLDataPointExtractorV1__get_insured_name(data)
    assert x == response


async def test_check_contains_letter_and_number_valid1():
    f = open(valid_file, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.NOLDataPointExtractorV1(uuid=uuid, file=file)
    data = '104601365191001'
    response = True
    x = await obj._NOLDataPointExtractorV1__check_contains_letter_and_number(data)
    assert x == response


async def test_check_contains_letter_and_number_valid2():
    f = open(valid_file, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.NOLDataPointExtractorV1(uuid=uuid, file=file)
    data = 'MIL4970798'
    response = True
    x = await obj._NOLDataPointExtractorV1__check_contains_letter_and_number(data)
    assert x == response


async def test_check_contains_letter_and_number_invalid():
    f = open(valid_file, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.NOLDataPointExtractorV1(uuid=uuid, file=file)
    data = 'INFINITY INS'
    x = await obj._NOLDataPointExtractorV1__check_contains_letter_and_number(data)
    assert not x


async def test_get_policy_number_valid1():
    f = open(valid_file, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.NOLDataPointExtractorV1(uuid=uuid, file=file)
    data = ['JOSELES GONZALEZ MOLINA', 'MIL6053575']
    response = 'MIL6053575'
    x = await obj._NOLDataPointExtractorV1__get_policy_number(data)
    assert x == response


async def test_get_policy_number_valid2():
    f = open(valid_file, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.NOLDataPointExtractorV1(uuid=uuid, file=file)
    data = ['JOSELES GONZALEZ MOLINA', '104601365191001']
    response = '104601365191001'
    x = await obj._NOLDataPointExtractorV1__get_policy_number(data)
    assert x == response


async def test_get_info():
    f = open(valid_file, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.NOLDataPointExtractorV1(uuid=uuid, file=file)
    data = ['JOSELES GONZALEZ MOLINA', 'INFINITY INS', 'MIL6053575']
    response = 'JOSELES GONZALEZ MOLINA', None, 'MIL6053575'
    x = await obj._NOLDataPointExtractorV1__get_info(data)
    assert x == response


async def test_get_signature_valid():
    f = open(valid_file, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.NOLDataPointExtractorV1(uuid=uuid, file=file)
    response = {'is_signed': True}
    x = await obj._NOLDataPointExtractorV1__get_signature()
    assert x == response
