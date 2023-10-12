import io

from app.service.api.v1.mvr import extract_v1

valid_file = 'app/data/temp/test_data/MVR_Sheree Williams 1.pdf'
invalid_file = 'app/data/temp/test_data/MVR_SAMUEL SIORDIA.pdf'
uuid = '89c5de1c-4d25-11ec-8623-d1e221452fcd'


async def test_get_signature_valid():
    f = open(valid_file, "rb")
    file = io.BytesIO(f.read())
    response = {'is_signed': True}
    obj = extract_v1.MVRDataPointExtractorV1(uuid=uuid, file=file)
    x = await obj._MVRDataPointExtractorV1__get_signature()
    assert x == response


async def test_get_signature_invalid():
    f = open(invalid_file, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.MVRDataPointExtractorV1(uuid=uuid, file=file)
    x = await obj._MVRDataPointExtractorV1__get_signature()
    assert not x
