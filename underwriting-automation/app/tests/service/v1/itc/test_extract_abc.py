from app.service.api.v1.itc.extractor_v1 import extract_abc
import fitz

from app.constant import ITCDocumentTemplate

uuid = '89c5de1c-4d25-11ec-8623-d1e221452fcd'
doc = fitz.open('app/data/temp/test_data/ITC_Wendy Olivares.pdf', filetype="pdf")
doc_text = ''
for page in doc:
    doc_text = doc_text + page.get_textpage().extractText()
doc_text = doc_text.replace('\n', ' ')


async def test_get_insured_and_agent_info_valid():
    insured_info = {"name": "Wendy Banesa Olivares",
                    "address": {"city": "PERRIS", "state": "California", "zip": "92570",
                                "street": "1355 S Perris Blvd Apt 164"}}
    agent_info = {'address': {'city': 'SAN BERNARDINO', 'state': 'California', 'zip': '92408'},
                  'name': 'Call Center II', 'producer_code': '0038197'}
    obj = extract_abc.ITCExtractABC(uuid=uuid, doc=doc)
    x = await obj._get_insured_and_agent_info()
    assert x == (insured_info, agent_info)


async def test_get_insured_and_agent_info_valid_only_name():
    insured_info = {'address': None,
                    'name': 'Wendy Banesa Olivares'}
    agent_info = None

    obj = extract_abc.ITCExtractABC(uuid=uuid, doc=doc)
    obj.doc_text = 'Name Wendy Banesa Olivares  Address 1355'
    obj.indexof = {'Name': 0, 'Address': 28}
    x = await obj._get_insured_and_agent_info()
    assert x == (insured_info, agent_info)


async def test_get_insured_and_agent_info_valid_address_only_street():
    insured_info = {"name": None,
                    "address": {"city": None, "state": None, "zip": None, "street": "290 W ORANGE SHOW RD STE100"}}
    agent_info = None
    obj = extract_abc.ITCExtractABC(uuid=uuid, doc=doc)
    obj.doc_text = 'Address 290 W ORANGE SHOW RD STE100 City, State ZIP PERRIS'
    obj.indexof = {'Address': 0, 'City, State ZIP': 36}
    x = await obj._get_insured_and_agent_info()
    assert x == (insured_info, agent_info)


async def test_get_insured_and_agent_info_valid_no_match():
    insured_info = None
    agent_info = None
    obj = extract_abc.ITCExtractABC(uuid=uuid, doc=doc)
    obj.doc_text = 'Producer Code 0038197 17856707         Company'
    obj.indexof = {'Company': 39, 'Producer Code': 0}
    x = await obj._get_insured_and_agent_info()
    assert x == (insured_info, agent_info)


async def test__split_city_state_zip_valid():
    response = {'city': 'SAN BERNARDINO', 'state': 'California', 'zip': '92407'}
    obj = extract_abc.ITCExtractABC(uuid=uuid, doc=doc)
    x = await obj._ITCExtractABC__split_city_state_zip('SAN BERNARDINO, California 92407')
    assert x == response


async def test__split_city_state_zip_invalid():
    response = {'city': None, 'state': None, 'zip': None}
    obj = extract_abc.ITCExtractABC(uuid=uuid, doc=doc)
    x = await obj._ITCExtractABC__split_city_state_zip('addsdssdsd')
    assert x == response


async def test_get_company_info_valid():
    response = {'name': "Kemper Auto - Veronica's", 'policy_term': 'Annual'}
    obj = extract_abc.ITCExtractABC(uuid=uuid, doc=doc)
    x = await obj._get_company_info()
    assert x == response


async def test_get_company_info_valid_no_policy_term():
    response = {'name': "Kemper Auto - Veronica's", 'policy_term': None}

    obj = extract_abc.ITCExtractABC(uuid=uuid, doc=doc)
    obj.doc_text = ' Company Kemper Auto - Veronica\'s Quote Date/Time 7/11/2021 05:29 PM Rates E�ective 6/15/2021 Policy E�ective 7/11/2021'
    obj.indexof = {'Company': 1, 'Quote Date/Time': 34}
    x = await obj._get_company_info()
    assert x == response


async def test_get_company_info_valid_no_name():
    response = {'name': None, 'policy_term': 'Annual'}

    obj = extract_abc.ITCExtractABC(uuid=uuid, doc=doc)
    obj.doc_text = ' Policy Term Annual Policy Tier \xa0 Quote By OP 6 Lead Source '
    obj.indexof = {'Policy Term': 1, 'Policy Tier': 20}
    x = await obj._get_company_info()
    assert x == response


async def test_get_vehicle_driver_id():
    response = ([1], [2, 1])

    obj = extract_abc.ITCExtractABC(uuid=uuid, doc=doc)
    obj.doc_text = '\xa0 \xa0 Veh 1/ \xa0 \xa0 \xa0 \xa0 Drv 2 Drv 1 \xa0 \xa0 ITC Transaction ID ae21a6c45dc4'
    obj.indexof = {'Veh': 4, 'Drv': 19, 'ITC Transaction ID': 35}
    x = await obj._ITCExtractABC__get_vehicle_driver_id()
    assert x == response


async def test_get_vehicle_driver_id_same_driver_number():
    response = ([1, 2], [2, 1])
    obj = extract_abc.ITCExtractABC(uuid=uuid, doc=doc)
    obj.doc_text = '\xa0 \xa0 Veh 1/  Veh 2/ \xa0 \xa0 \xa0 \xa0 Drv 2 Drv 1 Drv 1\xa0 \xa0 ITC Transaction ID ae21a6c45dc4'
    obj.indexof = {'Veh': 4, 'Drv': 27, 'ITC Transaction ID': 48}
    x = await obj._ITCExtractABC__get_vehicle_driver_id()
    assert x == response


async def test__extract_word_list_from_key_valid():
    response = ['15000/30000']
    obj = extract_abc.ITCExtractABC(uuid=uuid, doc=doc)
    obj.indexof = {ITCDocumentTemplate.Key.LIABILITY_BI: 1322}
    x = await obj._ITCExtractABC__extract_word_list_from_key(label=ITCDocumentTemplate.Key.LIABILITY_BI, length=1)
    assert x == response


async def test__extract_word_list_from_key_valid_not_in_indexof():
    response = None
    obj = extract_abc.ITCExtractABC(uuid=uuid, doc=doc)
    obj.indexof = {ITCDocumentTemplate.Key.LIABILITY_BI: 1322}
    x = await obj._ITCExtractABC__extract_word_list_from_key(label=ITCDocumentTemplate.Key.LIABILITY_PD, length=1)
    assert x == response


async def test__get_driver_gender_valid():
    response = 'female'
    obj = extract_abc.ITCExtractABC(uuid=uuid, doc=doc)
    x = await obj._ITCExtractABC__get_driver_gender(info='F42S')
    assert x == response


async def test__get_driver_gender_invalid():
    obj = extract_abc.ITCExtractABC(uuid=uuid, doc=doc)
    x = await obj._ITCExtractABC__get_driver_gender(info='Z42S')
    assert not x


async def test__get_driver_marital_status_valid():
    response = 'Married'
    obj = extract_abc.ITCExtractABC(uuid=uuid, doc=doc)
    x = await obj._ITCExtractABC__get_driver_marital_status(info='M42M')
    assert x == response


async def test__get_driver_marital_status_invalid():
    obj = extract_abc.ITCExtractABC(uuid=uuid, doc=doc)
    x = await obj._ITCExtractABC__get_driver_marital_status(info='Z42Z')
    assert not x


async def test__get_driver_attributes_valid():
    response = (['1'], ['164'])
    obj = extract_abc.ITCExtractABC(uuid=uuid, doc=doc)
    x = await obj._ITCExtractABC__get_driver_attributes(driver_length=1)
    assert x == response


async def test__get_driver_attributes_invalid():
    response = (None, None)
    obj = extract_abc.ITCExtractABC(uuid=uuid, doc=doc)
    x = await obj._ITCExtractABC__get_driver_attributes(driver_length=0)
    assert x == response


async def test__get_driver_info_by_driver_valid():
    response = [{'id': 1, 'name': 'Wendy Olivares', 'gender': 'female', 'age': 29, 'marital_status': 'Single',
                 'date_of_birth': '1991-10-29', 'fr_filing': None, 'number_of_violations': 0,
                 'attributes': {'months_foreign_license': 1, 'months_mvr_experience_us': 164}}]
    obj = extract_abc.ITCExtractABC(uuid=uuid, doc=doc)
    x = await obj._ITCExtractABC__get_driver_info_by_driver(violations_by_driver=None)
    assert x == response


async def test_get_driver_information_valid():
    response = {"bi_amount_each_person": 15000, "bi_amount_each_accident": 30000, "pd_amount_each_accident": 5000,
                "uninsured_bi_amount_each_person": None, "uninsured_bi_amount_each_accident": None,
                "uninsured_pd_amount_each_accident": None, "excluded_drivers": None, "total_number_of_violations": 0,
                "drivers": [
                    {"id": 1, "name": "Wendy Olivares", "gender": "female", "age": 29, "marital_status": "Single",
                     "date_of_birth": "1991-10-29", "fr_filing": None, "number_of_violations": 0,
                     "attributes": {"months_foreign_license": 1, "months_mvr_experience_us": 164}}]}
    obj = extract_abc.ITCExtractABC(uuid=uuid, doc=doc)
    x = await obj._get_driver_information()
    assert x == response


async def test__get_vin_year_make_model_valid():
    response = [{'id': 1, 'year': 2010, 'make': 'TOYOTA', 'model': 'VENZA', 'vin': '4T3ZA3BB1AU023479'}]
    obj = extract_abc.ITCExtractABC(uuid=uuid, doc=doc)
    x = await obj._ITCExtractABC__get_vin_year_make_model(veh_info='1 4T3ZA3BB1AU023479 TOYOTA VENZA 2010')
    assert x == response


async def test__get_vin_year_make_model_valid_more_than_one():
    response = [{'id': 1, 'make': 'TOYOTA', 'model': 'VENZA', 'vin': '4T3ZA3BB1AU023479', 'year': 2010},
                {'id': 2, 'make': 'HONDA', 'model': 'VENZA ABC', 'vin': '123ZA3BB1AU023479', 'year': None}]
    obj = extract_abc.ITCExtractABC(uuid=uuid, doc=doc)
    veh_info = '1 4T3ZA3BB1AU023479 TOYOTA VENZA 2010 2 123ZA3BB1AU023479 HONDA VENZA ABC'
    x = await obj._ITCExtractABC__get_vin_year_make_model(veh_info=veh_info)
    assert x == response


async def test_get_vehicle_information_valid():
    response = {"vehicles": [{"id": 1, "vin": "4T3ZA3BB1AU023479", "make": "TOYOTA", "model": "VENZA", "year": 2010,
                              "annual_miles_driven": 8500, "comprehensive_deductible": 1000,
                              "collision_deductible": 1000}]}
    obj = extract_abc.ITCExtractABC(uuid=uuid, doc=doc)
    x = await obj._get_vehicle_information()
    assert x == response


async def test_get_vehicle_information_invalid():
    obj = extract_abc.ITCExtractABC(uuid=uuid, doc=doc)
    obj.indexof = {}
    x = await obj._get_vehicle_information()
    assert not x
