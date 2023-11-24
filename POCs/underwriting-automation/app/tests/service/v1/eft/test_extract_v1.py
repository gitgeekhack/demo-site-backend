import io

from app.service.api.v1.eft import extract_v1
from app.constant import EFT

uuid = '89c5de1c-4d25-11ec-8623-d1e221452fcd'
valid_file = 'app/data/temp/test_data/EFT-MIL6051942.pdf'
invalid_file = 'app/data/temp/test_data/EFT-MIL6058313.pdf'
valid_text = 'AUTHORIZATION FOR INSURED’S ELECTRONIC FUNDS TRANSFER Card Holder\'s Signature Date Insured\'s Name: ' \
             'Credit Card Number: GABRIEL ANTHONY GONZALEZ XXXX - XXXX - XXXX - 7739 Card Holder\'s Name: GABRIEL ' \
             'GONZALEZ I hereby authorize Alliance United Insurance Services, LLC (hereafter known as Company) to ' \
             'initiate deductions from or apply charges to my account identified above for any and all amounts due ' \
             'including but not limited to payments of premium and fees on the insurance policy referenced above by ' \
             'Company, and any renewals thereafter, and to initiate credit entries to my account in order to correct ' \
             'any erroneous deductions or provide a refund of premium. I authorize the financial institution named ' \
             'above as the depository, to accept and post entries to my account. I understand that this authorization ' \
             'allows Company to adjust the monthly deductions or charges to reflect any premium changes and policy ' \
             'renewals. This authorization will remain in effect until I provide notice to the Company of its ' \
             'termination in such time and in such manner as to afford the Company a reasonable opportunity to act in ' \
             'order to reflect on the next renewal. Policy  Number: MIL6051942 Visa Credit Card Type: Insured\'s ' \
             'Signature Date 10/2025 Expiration Date: To ensure the security of our insureds data this document is to ' \
             'be maintained by the broker and will not be submitted to Alliance United for processing or review. ' \
             'Accordingly the Broker will be held responsible for any unverifiable or challenged activity. *124 ' \
             '*MIL60519 MIL6051942 - GABRIEL ANTHONY GONZALEZ AU APP (01/19) – Copyright Alliance United Insurance ' \
             'Company Page 11 of 12 2022-01-11 T11:50:24-08:00 2022-01-11 T11:50:53-08:00 '

invalid_text = 'AUTHORIZATION FOR INSURED’S ELECTRONIC FUNDS TRANSFER Card Holder\'s Signature Date Insured\'s Name: ' \
               'Credit Card Number: XXXX - XXXX - XXXX - 7739 Card Holder\'s Name: GABRIEL ' \
               'GONZALEZ I hereby authorize Alliance United Insurance Services, LLC (hereafter known as Company) to ' \
               'initiate deductions from or apply charges to my account identified above for any and all amounts due ' \
               'including but not limited to payments of premium and fees on the insurance policy referenced above by ' \
               'Company, and any renewals thereafter, and to initiate credit entries to my account in order to correct ' \
               'any erroneous deductions or provide a refund of premium. I authorize the financial institution named ' \
               'above as the depository, to accept and post entries to my account. I understand that this authorization ' \
               'allows Company to adjust the monthly deductions or charges to reflect any premium changes and policy ' \
               'renewals. This authorization will remain in effect until I provide notice to the Company of its ' \
               'termination in such time and in such manner as to afford the Company a reasonable opportunity to act in ' \
               'order to reflect on the next renewal. Policy  Number: Visa Credit Card Type: Insured\'s ' \
               'Signature Date 10/2025 Expiration Date: To ensure the security of our insureds data this document is to ' \
               'be maintained by the broker and will not be submitted to Alliance United for processing or review. ' \
               'Accordingly the Broker will be held responsible for any unverifiable or challenged activity. *124 ' \
               '*MIL60519 MIL6051942 - GABRIEL ANTHONY GONZALEZ AU APP (01/19) – Copyright Alliance United Insurance ' \
               'Company Page 11 of 12 2022-01-11 T11:50:24-08:00 2022-01-11 T11:50:53-08:00 '


async def test_get_insured_name_valid():
    f = open(valid_file, "rb")
    file = io.BytesIO(f.read())
    response = 'GABRIEL ANTHONY GONZALEZ'
    obj = extract_v1.EFTDataPointExtractorV1(uuid=uuid, file=file)
    x = await obj._EFTDataPointExtractorV1__get_insured_name(text=valid_text)
    assert x == response


async def test_get_insured_name_invalid():
    f = open(valid_file, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.EFTDataPointExtractorV1(uuid=uuid, file=file)
    x = await obj._EFTDataPointExtractorV1__get_insured_name(text=invalid_text)
    assert not x


async def test_get_policy_number_valid():
    f = open(valid_file, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.EFTDataPointExtractorV1(uuid=uuid, file=file)
    x = await obj._EFTDataPointExtractorV1__get_policy_number(text=valid_text)
    response = 'MIL6051942'
    assert x == response
    
    
async def test_get_policy_number_invalid():
    f = open(valid_file, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.EFTDataPointExtractorV1(uuid=uuid, file=file)
    x = await obj._EFTDataPointExtractorV1__get_policy_number(text=invalid_text)
    assert not x


async def test_get_signature_valid():
    f = open(valid_file, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.EFTDataPointExtractorV1(uuid=uuid, file=file)
    label = EFT.Sections.INSURED_SIGNATURE
    index = 0
    response = {'is_signed': True, 'is_dated': True}
    x = await obj._EFTDataPointExtractorV1__get_signature(label, index)
    assert x == response


async def test_get_signature_invalid():
    f = open(invalid_file, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.EFTDataPointExtractorV1(uuid=uuid, file=file)
    label = EFT.Sections.INSURED_SIGNATURE
    index = 0
    response = {'is_signed': False, 'is_dated': True}
    x = await obj._EFTDataPointExtractorV1__get_signature(label, index)
    assert x == response
