import io

from app.service.api.v1.insurance_application.extractor_v1 import extract_abc

uuid = '89c5de1c-4d25-11ec-8623-d1e221452fcd'
valid_file_1 = 'app/data/temp/test_data/ALLIANCE_APP_Alex Zuniga.pdf'
valid_file_2 = 'app/data/temp/test_data/ALLIANCE_APP_CHRISTINA AVALOS.pdf'
page_metadata = (('Third Party Designation', (18.0, 28.7037410736084, 153.21603393554688, 40.48773956298828), 4), (
    'Please select one of the following options:', (54.0, 46.21489715576172, 221.4809112548828, 55.106895446777344), 4),
                 (
                     'I choose to designate the following person to receive an advance notice that the coverage may lapse, terminate, expire or',
                     (108.0, 66.76604461669922, 590.94921875, 75.65804290771484), 4), (
                     'cancel for nonpayment of premium:',
                     (90.0, 80.08599090576172, 230.99388122558594, 88.97798919677734),
                     4), ('Address / City / State / Zip Code',
                          (300.6000061035156, 91.21440887451172, 429.0121765136719, 100.10640716552734), 4), (
                     'Designated Person',
                     (123.83979797363281, 91.21440887451172, 200.34877014160156, 100.10640716552734),
                     4), (
                     'I decline designating one additional person to receive an advance notice that the coverage may lapse, terminate, expire or',
                     (108.0, 129.48199462890625, 593.4782104492188, 138.37399291992188), 4), (
                     'cancel for nonpayment of premium.',
                     (90.0, 143.88250732421875, 230.99388122558594, 152.77450561523438), 4), (
                     'You may change or terminate your designated person at any time by contacting your Broker.',
                     (56.0, 158.48199462890625, 423.96502685546875, 167.37399291992188), 4),
                 ('7/8/2021', (388.0, 180.5, 426.9200134277344, 194.24000549316406), 4),
                 ('Signature of Named Insured', (54.0, 196.27789306640625, 173.90695190429688, 205.1158905029297), 4),
                 ('Date', (360.0, 196.27801513671875, 379.50299072265625, 205.1160125732422), 4), (
                     'Disclosure of All Household Members, Children Away From Home, Other Drivers, Registered Owners,',
                     (17.006999969482422, 226.7039794921875, 595.2630615234375, 238.4879913330078), 4), (
                     'Individuals With An Insurable Interest, and Vehicles',
                     (17.006999969482422, 240.5028076171875, 311.3790588378906, 252.2868194580078), 4), (
                     'I have listed on this application the following individuals (whether or not they are licensed or permitted): (1) all individuals age 14 years',
                     (52.5, 257.4420166015625, 592.7425537109375, 266.3340148925781), 4), (
                     'or older who reside with me; (2) all children of mine (and/or my spouse) age 14 years or older residing away from home (either',
                     (52.5, 267.79119873046875, 592.7069091796875, 276.6831970214844), 4), (
                     'temporarily or permanently); (3) all children of mine (and/or my spouse) age 14 years or older who are away at school; and (4) all',
                     (52.5, 278.1404113769531, 592.859619140625, 287.03240966796875), 4), (
                     'individuals (irrespective of whether they are household residents, or children of mine and/or my spouse) who may drive the vehicles',
                     (52.5, 288.4896240234375, 592.7354125976562, 297.3816223144531), 4), (
                     'listed on this application on a regular basis. All information regarding these individuals is correct. I agree to notify the Company of any',
                     (52.5, 298.8388366699219, 592.6885375976562, 307.7308349609375), 4), (
                     'changes in household residents, children of mine (and/or my spouse) age 14 years or older, other drivers, and/or vehicles listed on the',
                     (52.5, 309.18804931640625, 592.6987915039062, 318.0800476074219), 4),
                 ('policy.', (52.5, 319.5372619628906, 78.0060043334961, 328.42926025390625), 4), (
                     'I acknowledge that, if I fail to notify Alliance United Insurance Company of all individuals who come within the four (4)',
                     (52.46992111206055, 333.36474609375, 592.36181640625, 342.2027587890625), 4), (
                     'categories enumerated above, and/or if I fail to notify Alliance United Insurance Company of any change in driving status for',
                     (52.46990966796875, 343.7139587402344, 592.3890380859375, 352.5519714355469), 4), (
                     'any individual who is listed on this application (or who is added to my policy in the future), such failure shall constitute (1) a',
                     (52.46990966796875, 354.06317138671875, 592.4337768554688, 362.90118408203125), 4), (
                     'violation of my obligation to keep Alliance United Insurance Company informed; and (2) a material misrepresentation that',
                     (52.46990966796875, 364.4123840332031, 592.3441162109375, 373.2503967285156), 4), (
                     'affects the risk accepted by the Company. I also acknowledge that such failure may result in (1) cancellation, rescission, or',
                     (52.46990966796875, 374.76116943359375, 592.46875, 383.59918212890625), 4), (
                     'voiding of my coverage; and/or (2) a denial of coverage for a claim.',
                     (52.46990966796875, 385.1103820800781, 338.24688720703125, 393.9483947753906), 4), (
                     'I understand that only those vehicles which are primarily garaged at my primary residence are eligible for inclusion on my policy.',
                     (52.46367263793945, 397.8269958496094, 561.4046630859375, 406.718994140625), 4), (
                     'I have also listed on this application all registered owners of, and all individuals with an insurable interest in, any vehicles listed on this',
                     (52.46990966796875, 411.32440185546875, 592.7762451171875, 420.2164001464844), 4), (
                     'application. I acknowledge that all such owners/individuals must be rated as a driver. I further acknowledge that, if they are not listed',
                     (52.46990966796875, 421.6731872558594, 592.5960693359375, 430.565185546875), 4), (
                     'and rated, such owners/individuals will be excluded from coverage under the policy. I agree to notify the Company of any changes in',
                     (52.46990966796875, 432.02197265625, 592.5963745117188, 440.9139709472656), 4), (
                     'registered owners of, and/or individuals with an insurable interest in, vehicles listed on the policy.',
                     (52.46990966796875, 442.3707580566406, 436.91387939453125, 451.26275634765625), 4), (
                     'I acknowledge that, if I fail to notify Alliance United Insurance Company of all registered owners of vehicles listed in this',
                     (52.46367263793945, 456.02008056640625, 592.3382568359375, 464.85809326171875), 4), (
                     'application (or of any changes in registered owners of vehicles listed on the policy), and/or if I fail to notify Alliance United',
                     (52.463653564453125, 466.3692932128906, 592.3206787109375, 475.2073059082031), 4), (
                     'Insurance Company of all individuals with an insurable interest in vehicles listed in this application (or of any changes in',
                     (52.463653564453125, 476.718505859375, 592.4000854492188, 485.5565185546875), 4), (
                     'individuals with an insurable interest in vehicles listed on the policy), such failure shall constitute (1) a violation of my',
                     (52.463653564453125, 487.0677185058594, 592.3726196289062, 495.9057312011719), 4), (
                     'obligation to keep Alliance United Insurance Company informed; and (2) a material misrepresentation that affects the risk',
                     (52.463653564453125, 497.41693115234375, 592.3916015625, 506.25494384765625), 4), (
                     'accepted by the Company. I also acknowledge that such failure may result in (1) cancellation, rescission, or voiding of my',
                     (52.463653564453125, 507.76568603515625, 592.3656616210938, 516.6036987304688), 4), (
                     'coverage; and/or (2) a denial of coverage for a claim.',
                     (52.463623046875, 518.1149291992188, 277.3195495605469, 526.9529418945312), 4),
                 ('7/8/2021', (382.0, 535.5, 420.9200134277344, 549.239990234375), 4),
                 ('Date', (356.25, 555.5910034179688, 375.75299072265625, 564.4290161132812), 4),
                 ('Signature of Named Insured', (51.75, 555.5910034179688, 171.65695190429688, 564.4290161132812), 4),
                 ('*124 *MIL49694', (252.0, 751.6875, 533.760498046875, 788.6257934570312), 4), (
                     'MIL4969400 - ALEX ZUNIGA BENITEZ',
                     (10.152000427246094, 760.3201293945312, 150.51197814941406, 768.22412109375), 4), (
                     'AU APP (01/19) – Copyright',
                     (10.152000427246094, 768.6002197265625, 110.1199951171875, 776.5042114257812), 4),
                 ('Page 5 of 15', (186.97900390625, 774.7201538085938, 232.30703735351562, 782.6241455078125), 4), (
                     'Alliance United Insurance Company',
                     (10.152000427246094, 777.799072265625, 137.26400756835938, 785.7030639648438), 4))
sections = ['Third Party Designation',
            'Disclosure of All Household Members, Children Away From Home, Other Drivers, Registered Owners,']


async def test_get_section_index_valid():
    f = open(valid_file_1, "rb")
    file = io.BytesIO(f.read())
    obj = extract_abc.APPExtractABC(uuid=uuid, file=file)
    metadata = page_metadata
    section = ['Third Party Designation',
               'Disclosure of All Household Members, Children Away From Home, Other Drivers, Registered Owners,']
    section_name = 'Third Party Designation'
    response = 0, 12
    x = await obj._APPExtractABC__get_section_index(metadata, section, section_name)
    assert x == response


async def test_get_section_index_invalid():
    f = open(valid_file_1, "rb")
    file = io.BytesIO(f.read())
    obj = extract_abc.APPExtractABC(uuid=uuid, file=file)
    metadata = page_metadata
    section = ['Rejection of Uninsured/Underinsured Motorist Bodily Injury Coverage',
               'Rejection of Uninsured Motorist Property Damage Coverage']
    section_name = 'Rejection of Uninsured/Underinsured Motorist Bodily Injury Coverage'
    response = None, None
    x = await obj._APPExtractABC__get_section_index(metadata, section, section_name)
    assert x == response


async def test_get_page_sections_valid():
    f = open(valid_file_1, "rb")
    file = io.BytesIO(f.read())
    obj = extract_abc.APPExtractABC(uuid=uuid, file=file)
    metadata = page_metadata
    allowed_sections = ['Third Party Designation',
                        'Disclosure of All Household Members, Children Away From Home, Other Drivers, Registered Owners,',
                        'Rejection of Uninsured/Underinsured Motorist Bodily Injury Coverage',
                        'Rejection of Uninsured Motorist Property Damage Coverage',
                        'Statement of Vehicle Condition Certification',
                        'Acknowledgements by Applicant',
                        'Acknowledgment of Programs Offered']
    response = ['Third Party Designation',
                'Disclosure of All Household Members, Children Away From Home, Other Drivers, Registered Owners,']
    x = await obj._APPExtractABC__get_page_sections(metadata, allowed_sections)
    assert x == response


async def test_get_page_sections_invalid():
    f = open(valid_file_1, "rb")
    file = io.BytesIO(f.read())
    obj = extract_abc.APPExtractABC(uuid=uuid, file=file)
    metadata = page_metadata
    allowed_sections = ['Rejection of Uninsured/Underinsured Motorist Bodily Injury Coverage',
                        'Rejection of Uninsured Motorist Property Damage Coverage',
                        'Statement of Vehicle Condition Certification',
                        'Acknowledgements by Applicant',
                        'Acknowledgment of Programs Offered']
    x = await obj._APPExtractABC__get_page_sections(metadata, allowed_sections)
    assert not x


async def test_get_date_bbox_valid():
    f = open(valid_file_2, "rb")
    file = io.BytesIO(f.read())
    obj = extract_abc.APPExtractABC(uuid=uuid, file=file)
    page_no = 4
    section_name = 'Third Party Designation'
    index = 0
    response = (150.25, 170.39999389648438, 191.1619873046875, 181.39199829101562)
    x = await obj._get_date_bbox(page_no, section_name, index)
    assert x == response


async def test_get_date_bbox_invalid():
    f = open(valid_file_2, "rb")
    file = io.BytesIO(f.read())
    obj = extract_abc.APPExtractABC(uuid=uuid, file=file)
    page_no = 4
    section_name = 'Third Party Designation'
    index = 2
    x = await obj._get_date_bbox(page_no, section_name, index)
    assert not x


async def test_get_placeholder_bbox_valid():
    f = open(valid_file_2, "rb")
    file = io.BytesIO(f.read())
    obj = extract_abc.APPExtractABC(uuid=uuid, file=file)
    sections = ['Third Party Designation',
                'Disclosure of All Household Members, Children Away From Home, Other Drivers, Registered Owners,',
                'Rejection of Uninsured/Underinsured Motorist Bodily Injury Coverage',
                'Rejection of Uninsured Motorist Property Damage Coverage',
                'Statement of Vehicle Condition Certification',
                'Acknowledgements by Applicant',
                'Acknowledgment of Programs Offered']
    metadata = obj.pdf_helper.metadata
    doc = obj.doc
    target = 'signature'
    response = {'Third Party Designation': {
        'signature': {'bbox': (54.0, 193.5150146484375, 173.90699768066406, 205.90802001953125)}, 'page_no': 4},
        'Disclosure of All Household Members, Children Away From Home, Other Drivers, Registered Owners,': {
            'signature': {'bbox': (51.75, 552.8276977539062, 171.65699768066406, 565.220703125)}, 'page_no': 4},
        'Statement of Vehicle Condition Certification': {
            'signature': {'bbox': (54.0, 165.63836669921875, 173.90699768066406, 178.0313720703125)},
            'page_no': 5}, 'Acknowledgements by Applicant': {
            'signature': {'bbox': (54.0, 281.114990234375, 173.90699768066406, 293.50799560546875)}, 'page_no': 7},
        'Acknowledgment of Programs Offered': {
            'signature': {'bbox': (54.0, 580.3289794921875, 146.41197204589844, 592.7219848632812)},
            'page_no': 8}}
    x = await obj._get_placeholder_bbox(sections, metadata, doc, target)
    assert x == response


async def test_get_placeholder_bbox_invalid():
    f = open(valid_file_2, "rb")
    file = io.BytesIO(f.read())
    obj = extract_abc.APPExtractABC(uuid=uuid, file=file)
    sections = []
    metadata = obj.pdf_helper.metadata
    doc = obj.doc
    target = 'signature'
    x = await obj._get_placeholder_bbox(sections, metadata, doc, target)
    assert not x


async def test_validate_date_format_valid():
    f = open(valid_file_1, "rb")
    file = io.BytesIO(f.read())
    obj = extract_abc.APPExtractABC(uuid=uuid, file=file)
    dates = ['7/8/2021', '2021-8-7', '7-8-2021']
    response = ['7/8/2021', '2021-8-7', '7-8-2021']
    x = await obj._APPExtractABC__validate_date_format(dates)
    assert x == response


async def test_validate_date_format_invalid():
    f = open(valid_file_1, "rb")
    file = io.BytesIO(f.read())
    obj = extract_abc.APPExtractABC(uuid=uuid, file=file)
    dates = ['2021/03/02', '07/08', '2021-03']
    x = await obj._APPExtractABC__validate_date_format(dates)
    assert not x


async def test_validate_date_format_valid1():
    f = open(valid_file_1, "rb")
    file = io.BytesIO(f.read())
    obj = extract_abc.APPExtractABC(uuid=uuid, file=file)
    dates = ['2021/03/02', '07/08/2020', '2021-03']
    response = ['07/08/2020']
    x = await obj._APPExtractABC__validate_date_format(dates)
    assert x == response


async def test_parse_date_valid():
    f = open(valid_file_2, "rb")
    file = io.BytesIO(f.read())
    obj = extract_abc.APPExtractABC(uuid=uuid, file=file)
    text = 'Third Party Designation Please select one of the following options: I choose to designate the following ' \
           'person to receive an advance notice that the coverage may lapse, terminate, expire or cancel for nonpayment' \
           ' of premium: Address / City / State / Zip Code Designated Person I decline designating one additional person' \
           ' to receive an advance notice that the coverage may lapse, terminate, expire or cancel for nonpayment of ' \
           'premium. You may change or terminate your designated person at any time by contacting your Broker. ' \
           '2021-09-01 T17:12:05-07:00 Date Signature of Named Insured'
    response = ['2021-09-01']
    x = await obj._parse_date(text)
    assert x == response


async def test_parse_date_invalid():
    f = open(valid_file_2, "rb")
    file = io.BytesIO(f.read())
    obj = extract_abc.APPExtractABC(uuid=uuid, file=file)
    text = 'Third Party Designation Please select one of the following options: I choose to designate the following ' \
           'person to receive an advance notice that the coverage may lapse, terminate, expire or cancel for nonpayment' \
           ' of premium: Address / City / State / Zip Code Designated Person I decline designating one additional person' \
           ' to receive an advance notice that the coverage may lapse, terminate, expire or cancel for nonpayment of ' \
           'premium. You may change or terminate your designated person at any time by contacting your Broker. ' \
           'Date Signature of Named Insured'
    x = await obj._parse_date(text)
    assert not x
