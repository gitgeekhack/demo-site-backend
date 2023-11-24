import io

from app.constant import PromiseToProvideTemplate
from app.service.api.v1.promise_to_provide import extract_v1

file_name = 'app/data/temp/test_data/VER_PTP_CHRISTINA AVALOS.pdf'  # has date format yyyy-mm-dd and dd-mm-yyyy
file_name2 = 'app/data/temp/test_data/VER_PTP_Sheree Williams PTP.pdf'  # missing promise to provide date
file_name3 = 'app/data/temp/test_data/VER_PTP_Betty Maloy PTP.pdf'  # has date format dd.mm.yyyy
file_name4 = 'app/data/temp/test_data/VER_PTP_Blanca Mendez.pdf'  # has date format yyyy/mm/dd and dd/mm/yyyy


async def test__get_applied_coverage_effective_date():
    f = open(file_name, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.PTPDataPointExtractorV1(uuid='89c5de1c-4d25-11ec-8623-d1e221452fcd', file=file)
    response = "2021-09-01"
    x = await obj._PTPDataPointExtractorV1__get_applied_coverage_effective_date()
    assert x == response


async def test__get_promise_to_provide_by_date():
    f = open(file_name, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.PTPDataPointExtractorV1(uuid='89c5de1c-4d25-11ec-8623-d1e221452fcd', file=file)
    response = "2021-10-01"
    x = await obj._PTPDataPointExtractorV1__get_promise_to_provide_by_date()
    assert x == response


async def test__get_agreement_date():
    f = open(file_name, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.PTPDataPointExtractorV1(uuid='89c5de1c-4d25-11ec-8623-d1e221452fcd', file=file)
    response = ['2021-09-01', '2021-09-01', '2021-09-01']
    x = await obj._PTPDataPointExtractorV1__get_agreement_date()
    assert x == response


async def test__get_promise_to_provide_by_date_missing():
    f = open(file_name2, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.PTPDataPointExtractorV1(uuid='89c5de1c-4d25-11ec-8623-d1e221452fcd', file=file)
    x = await obj._PTPDataPointExtractorV1__get_promise_to_provide_by_date()
    assert not x


async def test__get_promise_to_provide_by_date_diff_format():
    f = open(file_name3, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.PTPDataPointExtractorV1(uuid='89c5de1c-4d25-11ec-8623-d1e221452fcd', file=file)
    response = '2021-08-12'
    x = await obj._PTPDataPointExtractorV1__get_promise_to_provide_by_date()
    assert x == response


async def test__get_promise_to_provide_by_date_diff_format1():
    f = open(file_name4, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.PTPDataPointExtractorV1(uuid='89c5de1c-4d25-11ec-8623-d1e221452fcd', file=file)
    response = '2021-07-18'
    x = await obj._PTPDataPointExtractorV1__get_promise_to_provide_by_date()
    assert x == response


async def test__get_promise_to_provide_by_date_diff_format2():
    f = open(file_name4, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.PTPDataPointExtractorV1(uuid='89c5de1c-4d25-11ec-8623-d1e221452fcd', file=file)
    response = {PromiseToProvideTemplate.ResponseKey.AGREED_BY_SIGN: {'is_signed': True},
                PromiseToProvideTemplate.ResponseKey.ACKNOWLEDGMENT_SIGN: {'is_signed': True}}
    x = await obj._PTPDataPointExtractorV1__get_signature()
    assert x == response
