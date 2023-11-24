import fitz

from app import app
from app.constant import BrokerPackageTemplate
from app.service.api.v1.broker_package import extract_v1


doc = fitz.open('app/data/temp/test_data/BROKER_PKG_Luis Urzua.pdf', filetype="pdf")
page = doc[2]
blocks = page.get_textpage().extractText().split()
document = 'app/data/temp/test_data/BROKER_PKG_Luis Urzua.pdf'
uuid = '89c5de1c-4d25-11ec-8623-d1e221452fcd'

invalid_doc = fitz.open('app/data/temp/test_data/BROKER_PKG_Alfonso Soto.pdf', filetype="pdf")
invalid_document = 'app/data/temp/test_data/BROKER_PKG_Alfonso Soto.pdf'
Response = BrokerPackageTemplate.ResponseKey

async def test_get_signed_date_valid():
    response = '2021-09-23'
    obj = extract_v1.Template1Extractor(uuid=uuid, doc=doc)
    x = await obj._Template1Extractor__get_signed_date(blocks)
    assert x == response


async def test_get_signed_date_valid_spanish_date():
    blocks[755] = 'enero'
    obj = extract_v1.Template1Extractor(uuid=uuid, doc=doc)
    x = await obj._Template1Extractor__get_signed_date(blocks)
    assert x == '2021-01-23'


async def test_get_signed_date_valid_month_in_text():
    response = '2021-01-23'
    blocks[755] = 'January'
    obj = extract_v1.Template1Extractor(uuid=uuid, doc=doc)
    x = await obj._Template1Extractor__get_signed_date(blocks)
    assert x == response


async def test_get_broker_fee_valid():
    response = 432.49
    obj = extract_v1.Template1Extractor(uuid=uuid, doc=doc)
    x = await obj._Template1Extractor__get_broker_fee(blocks)
    assert x == response


async def test_get_insured_name_valid():
    response = "urza flores luis"
    obj = extract_v1.Template1Extractor(uuid=uuid, doc=doc)
    x = await obj._Template1Extractor__get_insured_name(page)
    assert x == response


async def test_get_signed_date_invalid():
    response = 'Alfonso Soto'
    obj = extract_v1.Template1Extractor(uuid=uuid, doc=doc)
    x = await obj._Template1Extractor__get_signed_date(blocks)
    assert not x == response


async def test_get_broker_fee_invalid():
    response = "432.49"
    obj = extract_v1.Template1Extractor(uuid=uuid, doc=doc)
    x = await obj._Template1Extractor__get_broker_fee(blocks)
    assert not x == response


async def test_get_insured_name_invalid():
    response = 234.33

    obj = extract_v1.Template1Extractor(uuid=uuid, doc=doc)
    x = await obj._Template1Extractor__get_insured_name(page)
    assert not x == response


async def test_get_signature_valid():
    obj = extract_v1.Template1Extractor(uuid=uuid, doc=doc)
    x = await obj._Template1Extractor__get_signature()
    response = {Response.DISCLOSURES: {
        Response.COVERAGES: {"is_signed": True},
        Response.DRIVING_RECORD: {"is_signed": True},
        "exclusion": {
            Response.EXCLUSION_UNINSURED_BI: {"is_signed": True},
            Response.EXCLUSION_COMP_COLL_COVERAGE: {"is_signed": True},
            Response.EXCLUSION_BUSINESS_USE: {"is_signed": True},
            Response.EXCLUSION_NAMED_DRIVER_LIMITATION: {"is_signed": True}
        }},
        Response.STANDARD_BROKER_FEE_DISCLOSURE_FORM: {"is_signed": True},
        Response.TEXT_MESSAGING_CONSENT_AGREEMENT: {"is_signed": False},
        Response.BROKER_FEE_AGREEMENT: {
            Response.CLIENT_SIGNATURE: {"is_signed": True},
            Response.CONDITION_AND_ACKNOWLEDGMENT_AGREEMENT: {"is_signed": True},
            Response.CLIENT_INITIALS: {"is_signed": True}}}
    return x == response


async def test_get_signature_invalid():
    obj = extract_v1.Template1Extractor(uuid=uuid, doc=invalid_doc)
    x = await obj._Template1Extractor__get_signature()
    return not x
