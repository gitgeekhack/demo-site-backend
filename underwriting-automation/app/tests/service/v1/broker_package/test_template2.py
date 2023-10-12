import fitz

from app.constant import BrokerPackageTemplate
from app.service.api.v1.broker_package import extract_v1

uuid = '89c5de1c-4d25-11ec-8623-d1e221452fcd'
doc = fitz.open('app/data/temp/test_data/BROKER_PKG_Wendy Olivares.pdf', filetype="pdf")
page_text = ''
for page in doc:
    page_text = page_text + page.get_text()
page_text = page_text.replace('\n', ' ').replace('_', ' ')
Response = BrokerPackageTemplate.ResponseKey


async def test_get_signed_date_valid():
    obj = extract_v1.Template2Extractor(uuid=uuid, doc=doc)
    x = await obj._Template2Extractor__get_signed_date()
    assert x == "2021-07-13"


async def test_get_signed_date_valid_date():
    obj = extract_v1.Template2Extractor(uuid=uuid, doc=doc)
    obj.page_text = "BROKER FEE AGREEMENT As of this 2nd day of January, 2021 the undersigned (“Client”) "
    x = await obj._Template2Extractor__get_signed_date()
    assert x == '2021-01-02'


async def test_get_broker_fee_valid():
    response = 1023.23
    obj = extract_v1.Template2Extractor(uuid=uuid, doc=doc)
    obj.page_text = "broker fee is $ 1023.23 "
    x = await obj._Template2Extractor__get_broker_fee()
    assert x == response


async def test_get_broker_fee_invalid():
    obj = extract_v1.Template2Extractor(uuid=uuid, doc=doc)
    obj.page_text = "BROKER FEE AGREEMENT As of this 2nd day of January, 2021 the undersigned (“Client”) "
    x = await obj._Template2Extractor__get_broker_fee()
    assert not x


async def test_get_signed_date_invalid():
    obj = extract_v1.Template2Extractor(uuid=uuid, doc=doc)
    obj.page_text = "broker fee is $"
    x = await obj._Template2Extractor__get_broker_fee()
    assert not x


async def test_get_insured_name_valid():
    obj = extract_v1.Template2Extractor(uuid=uuid, doc=doc)
    obj.page_text = "Full Client's Name XYZ ABC Broker Full Name"
    x = await obj._Template2Extractor__get_insured_name()
    assert x == "XYZ ABC"


async def test_get_insured_name_valid_example():
    obj = extract_v1.Template2Extractor(uuid=uuid, doc=doc)
    x = await obj._Template2Extractor__get_insured_name()
    assert x == 'WENDY BANESA OLIVARES'


async def test_get_signature_valid():
    obj = extract_v1.Template2Extractor(uuid=uuid, doc=doc)
    x = await obj._Template2Extractor__get_signatures()
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
        Response.TEXT_MESSAGING_CONSENT_AGREEMENT: {"is_signed": True},
        Response.BROKER_FEE_AGREEMENT: {
            Response.CLIENT_SIGNATURE: {"is_signed": True},
            Response.CONDITION_AND_ACKNOWLEDGMENT_AGREEMENT: {"is_signed": True},
            Response.CLIENT_INITIALS: {"is_signed": True}}}
    assert x == response
