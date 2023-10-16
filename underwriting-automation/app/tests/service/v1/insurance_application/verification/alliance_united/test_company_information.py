from app.constant import SRC_INSURANCE_APPLICATION, TRG_PUL, TRG_NOL
from app.service.api.v1.insurance_application.verifier_v1.alliance_united import company_information
from app.service.helper.serializer_helper import deserialize

uuid = '89c5de1c-4d25-11ec-8623-d1e221452fcd'
dl_address = '4039 MAXSON RD APT 3 EL MONTE, CA 91732'
valid_data = {'mvr': [
    {'name': 'SIERRACHAVARRIA, EDDY GABRIEL', 'gender': 'male', 'date_of_birth': '1976-06-14', 'status': 'valid',
     'license_number': 'F8595056', 'number_of_violations': 0},
    {'name': 'MOLINAMUNOZ, PAOLA ELIZABETH', 'gender': 'female', 'date_of_birth': '1978-10-05', 'status': 'valid',
     'license_number': 'F8577498', 'number_of_violations': 0}], 'pleasure_use_letter':
    {'company_name': 'ALLIANCE UNITED', 'customer_name': 'EDDY GABRIEL SIERRACHAVARRIA', 'policy_number': 'MIL4972574',
     'vehicles': [{'year': 2005, 'make': 'FORD', 'model': 'RANGER', 'vin': '1FTYR10D45PA79138'},
                  {'year': 2005, 'make': 'MAZD', 'model': 'MAZDA6I', 'vin': '1YVHP80C355M69899'}],
     'signature': {'is_signed': True}}, 'insurance_application': {'insured_information': {
    'name': 'EDDY GABRIEL SIERRACHAVARRIA',
    'address': {'street': '4774 RANDOLPH ST', 'state': 'CA', 'zip': '90201-1355', 'city': 'BELL'}},
    'broker_information': {
        'name': "Veronica's Auto Insurance Services - Orange S",
        'address': {'city': 'SAN BERNARDINO'}},
    'policy_information': {
        'policy_number': 'MIL4972574',
        'receipt_date': '2021-07-13',
        'net_amount': 340.92,
        'insurance_type': 'Auto Insurance',
        'policy_term': 'Annual',
        'policy_start_date': '2021-07-13',
        'policy_end_date': '2022-01-13'},
    'driver_information': {'drivers': [{'id': 1,
                                        'name': 'EDDY GABRIEL SIERRACHAVARRIA',
                                        'date_of_birth': '1976-06-14',
                                        'relationship': 'Named Insured',
                                        'gender': 'Male',
                                        'marital_status': 'Single',
                                        'status': 'Rated',
                                        'license_number': 'F8595056',
                                        'license_state': 'CA',
                                        'driving_experience_in_years': 29,
                                        'driving_experience_in_months': 348,
                                        'sr_filing': False},
                                       {'id': 2,
                                        'name': 'PAOLA ELIZABETH MOLINAMUNOZ',
                                        'date_of_birth': '1978-10-05',
                                        'relationship': 'Significant Other',
                                        'gender': 'female',
                                        'marital_status': 'Single',
                                        'status': 'Rated',
                                        'license_number': 'F8577498',
                                        'license_state': 'CA',
                                        'driving_experience_in_years': 26,
                                        'driving_experience_in_months': 312,
                                        'sr_filing': False},
                                       {'id': 3,
                                        'name': 'GABRIEL EDUARDO SIERRA',
                                        'date_of_birth': '1998-09-19',
                                        'relationship': 'Son',
                                        'gender': 'Male',
                                        'marital_status': 'Single',
                                        'status': 'Excluded',
                                        'license_number': None,
                                        'license_state': 'CA',
                                        'driving_experience_in_years': None,
                                        'driving_experience_in_months': None,
                                        'sr_filing': False}]},
    'vehicle_information': {'vehicles': [
        {'id': 1, 'year': 2005, 'make': 'FORD',
         'model': 'RANGER', 'trim': None,
         'vehicle_use': 'Pleasure',
         'vin': '1FTYR10D45PA79138'},
        {'id': 2, 'year': 2005, 'make': 'MAZD',
         'model': 'MAZDA6I', 'trim': None,
         'vehicle_use': 'Pleasure',
         'vin': '1YVHP80C355M69899'}]},
    'coverage_information': {
        'bi_amount_each_person': 15000,
        'bi_amount_each_accident': 30000,
        'pd_amount_each_accident': 10000,
        'uninsured_bi_amount_each_person': None,
        'uninsured_bi_amount_each_accident': None,
        'uninsured_pd_amount_each_accident': None,
        'vehicles': None}, 'signatures': {
        'third_party_designation': {'is_signed': True, 'is_dated': True},
        'disclosure_of_all_household_members': {'is_signed': True, 'is_dated': True},
        'rejection_of_bi_coverage': {'is_signed': True, 'is_dated': True},
        'rejection_of_pd_coverage': {'is_signed': True, 'is_dated': True}, 'vehicle_condition_certification': None,
        'acknowledgements_by_applicant': {'is_signed': True, 'is_dated': True},
        'acknowledgement_of_programs_offered': {'is_signed': True, 'is_dated': True},
        'named_driver_exclusion': {'is_signed': True, 'is_dated': True}, 'no_fault_accident_declaration': None,
        'not_insurance_contract': {'is_signed': True, 'is_dated': True}, 'consumer_disclosure': None,
        'non_owned_vehicle_coverage_endorsement': None, 'cancellation_request': None}}, 'crm_receipt': [
    {'payment_date': '2021-07-13', 'reference_number': 'Receipt 1421-7551', 'name': 'SIERRA CHAVARRIA, EDDY',
     'address': {'street': '4774 RANDOLPH ST', 'city': 'BELL', 'state': 'CA', 'zip': '90201'},
     'payment_notes': {'card_last_4_digit': 5754, 'notes': None}, 'payment_method': 'Credit/Debit Card',
     'vr_fee_amount': None, 'nb_eft_to_company_amount': 340.92, 'broker_fee_amount': 120.0,
     'policy_number': 'MIL4972574', 'line_of_business': 'Personal Auto', 'amount_paid': 460.92,
     'amount_left_to_pay': 0.0}], 'itc': {'insured_information': {'name': 'EDDY SIERRA CHAVARRIA',
                                                                  'address': {'city': 'BELL', 'state': 'California',
                                                                              'zip': '90201',
                                                                              'street': '4774 RANDOLPH ST'}},
                                          'agent_information': {'name': 'Call Center II',
                                                                'address': {'city': 'SAN BERNARDINO',
                                                                            'state': 'California', 'zip': '92408'},
                                                                'producer_code': '0038197'},
                                          'insurance_company': {'name': "Kemper Auto - Veronica's",
                                                                'policy_term': 'Annual'},
                                          'driver_information': {'bi_amount_each_person': 15000,
                                                                 'bi_amount_each_accident': 30000,
                                                                 'pd_amount_each_accident': 10000,
                                                                 'uninsured_bi_amount_each_person': None,
                                                                 'uninsured_bi_amount_each_accident': None,
                                                                 'uninsured_pd_amount_each_accident': None,
                                                                 'excluded_drivers': None,
                                                                 'total_number_of_violations': 0, 'drivers': [
                                                  {'id': 2, 'name': None, 'gender': 'female', 'age': 42,
                                                   'marital_status': 'Single', 'date_of_birth': '1978-10-05',
                                                   'fr_filing': None, 'number_of_violations': 0,
                                                   'attributes': {'months_foreign_license': 1,
                                                                  'months_mvr_experience_us': 348}},
                                                  {'id': 1, 'name': None, 'gender': 'Male', 'age': 45,
                                                   'marital_status': 'Single', 'date_of_birth': '1976-06-14',
                                                   'fr_filing': None, 'number_of_violations': 0,
                                                   'attributes': {'months_foreign_license': 1,
                                                                  'months_mvr_experience_us': 321}}]},
                                          'vehicle_information': {'vehicles': [
                                              {'id': 1, 'vin': '1FTYR10D45PA79138', 'make': 'FORD', 'model': 'RANGER',
                                               'year': 2005, 'annual_miles_driven': 3500,
                                               'comprehensive_deductible': None, 'collision_deductible': None},
                                              {'id': 2, 'vin': '1YVHP80C355M69899', 'make': 'MAZDA',
                                               'model': 'MAZDA6I', 'year': 2005, 'annual_miles_driven': 3500,
                                               'comprehensive_deductible': None, 'collision_deductible': None}]},
                                          'signature': {'insured_information': {'is_signed': True},
                                                        'vehicle_information': {'is_signed': True},
                                                        'eod_information': {'is_signed': False}}},
    'driving_license': [
        {'address': '4774 RANDOLPH ST BELL, CA 90201', 'date_of_birth': None, 'expiry_date': '2024-06-14',
         'license_number': 'F8595056', 'name': 'SIERRA CHAVARRIA EDDY'},
        {'address': '4774 RANDOLPH ST BELL, CA 90201', 'date_of_birth': '4978-10-08', 'expiry_date': None,
         'license_number': 'F8577498', 'name': 'PAOLA ELIABETH'}],
    'artisan_use_letter':
        {'insured_name': 'OLIVARES WENDY BANESA', 'policy_number': 'MIL4972376',
         'vehicles': [{'year': 2010, 'make': 'TOYT', 'model': 'VENZA', 'vin': '4T3ZA3BB1AU023479'}],
         'signature': {'is_signed': True}}, 'non_owners_letter':
        {"insured_name": "OLIVARES WENDY BANESA", "policy_number": "MIL4972376", "company_name": "alliance-united",
         "signature": {"is_signed": True}}, "vr": [{"owners": ["GOMEZ LOURDES DERAS"],
                                                    "vehicle": {'year': 2010, 'make': 'TOYT', 'model': 'VENZA',
                                                                'vin': '4T3ZA3BB1AU023479'}}], "stripe_receipt": [
        {"receipt_number": "1782-5122", "amount_paid": 256.89, "date_paid": "2021-07-13",
         "payment_method": {"card_last_4_digit": 7181}}], "eft":
        {"insured_name": "OLIVARES WENDY BANESA", "policy_number": "MIL4972376",
         "signature": {"insured_signature": {"is_signed": True, "is_dated": True},
                       "card_holder_signature": {"is_signed": True, "is_dated": True}}}, "registration": [
        {"owners": ["OLIVARES WENDY BANESA"], "is_valid": True,
         "vehicle": {'year': 2010, 'make': 'TOYT', 'vin': '4T3ZA3BB1AU023479', "history": None, "model": None}}],
    'broker_package': {"signed_date": "2021-09-23", "broker_fee": 432.49, "insured_name": "urza flores luis"},
    "promise_to_provide": {"signature": {"agreed_to_be": {"is_signed": True},
                                         "condition_and_acknowledgement_agreement": {"is_signed": False}},
                           "applied_coverage_effective_date": "2021-10-01",
                           "promise_to_provide_by_date": "2021-10-16",
                           "promise_to_provide_agreement_date": ["2021-10-01", "2021-10-01", "2021-10-01"]}
}


async def test__verify_company_name_valid():
    data = await deserialize(valid_data)
    obj = company_information.CompanyInformationVerifier(uuid=uuid, data=data)
    x = await obj.verify_company_name()
    response = {'source': SRC_INSURANCE_APPLICATION, 'target': {TRG_PUL: True,
                                                                TRG_NOL: True}}
    assert x == response


async def test__verify_company_name_invalid():
    data = await deserialize(valid_data)
    obj = company_information.CompanyInformationVerifier(uuid=uuid, data=data)
    obj.pleasure_use_letter.company_name = None
    obj.non_owners_letter.company_name = None
    x = await obj.verify_company_name()
    response = {'source': SRC_INSURANCE_APPLICATION, 'target': {TRG_PUL: None,
                                                                TRG_NOL: None}}
    assert x == response


async def test__verify_company_name_false():
    data = await deserialize(valid_data)
    obj = company_information.CompanyInformationVerifier(uuid=uuid, data=data)
    obj.pleasure_use_letter.company_name = 'Kemper'
    obj.non_owners_letter.company_name = 'Kemper'
    x = await obj.verify_company_name()
    response = {'source': SRC_INSURANCE_APPLICATION, 'target': {TRG_PUL: False,
                                                                TRG_NOL: False}}
    assert x == response
