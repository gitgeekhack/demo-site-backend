from app.constant import SRC_ITC, SRC_DRIVING_LICENSE, TRG_BROKER_PACKAGE, TRG_CRM_RECEIPT, TRG_INS_APP, TRG_ITC, \
    TRG_PUL, TRG_MVR, SRC_INSURANCE_APPLICATION, SRC_MVR, TRG_AUL, TRG_VR, TRG_REGISTRATION, TRG_NOL
from app.service.api.v1.insurance_application.verifier_v1.alliance_united import driver_information
from app.service.helper.serializer_helper import deserialize

uuid = '89c5de1c-4d25-11ec-8623-d1e221452fcd'
valid_data = {'mvr': [
    {'name': 'OLIVARES, WENDY BANESA', 'gender': 'female', 'date_of_birth': '1991-10-29', 'status': 'valid',
     'license_number': 'F1567382', 'number_of_violations': 0}], 'pleasure_use_letter':
    {'company_name': 'ALLIANCE UNITED', 'customer_name': 'WENDY BANESA OLIVARES', 'policy_number': 'MIL4972376',
     'vehicles': [{'year': 2010, 'make': 'TOYT', 'model': 'VENZA', 'vin': '4T3ZA3BB1AU023479'}],
     'signature': {'is_signed': True}}, 'insurance_application': {
    'insured_information': {'name': 'WENDY BANESA OLIVARES',
                            'address': {'street': '1355 S PERRIS BLVD APT 164', 'state': 'CA', 'zip': '92570-2578',
                                        'city': 'PERRIS'}},
    'broker_information': {'name': "Veronica's Auto Insurance Services - Orange S",
                           'address': {'city': 'SAN BERNARDINO'}},
    'policy_information': {'policy_number': 'MIL4972376', 'receipt_date': '2021-07-13', 'net_amount': 96.89,
                           'insurance_type': 'Auto Insurance', 'policy_term': 'Monthly',
                           'policy_start_date': '2021-07-13', 'policy_end_date': '2021-08-13'}, 'driver_information': {
        'drivers': [
            {'id': 1, 'name': 'WENDY BANESA OLIVARES', 'date_of_birth': '1991-10-29', 'relationship': 'Named Insured',
             'gender': 'female', 'marital_status': 'Single', 'status': 'Rated', 'license_number': 'F1567382',
             'license_state': 'CA', 'driving_experience_in_years': 13, 'driving_experience_in_months': 156,
             'sr_filing': False}]}, 'vehicle_information': {'vehicles': [
        {'id': 1, 'year': 2010, 'make': 'TOYT', 'model': 'VENZA', 'trim': None, 'vehicle_use': 'Pleasure',
         'vin': '4T3ZA3BB1AU023479'}]},
    'coverage_information': {'bi_amount_each_person': 15000, 'bi_amount_each_accident': 30000,
                             'pd_amount_each_accident': 5000, 'uninsured_bi_amount_each_person': None,
                             'uninsured_bi_amount_each_accident': None, 'uninsured_pd_amount_each_accident': None,
                             'vehicles': [{'id': 1, 'comprehensive_deductible': 1000, 'collision_deductible': 1000}]},
    'signatures': {'third_party_designation': {'is_signed': True, 'is_dated': True},
                   'disclosure_of_all_household_members': {'is_signed': True, 'is_dated': True},
                   'rejection_of_bi_coverage': {'is_signed': True, 'is_dated': True},
                   'rejection_of_pd_coverage': {'is_signed': True, 'is_dated': True},
                   'vehicle_condition_certification': {'is_signed': True, 'is_dated': True},
                   'acknowledgements_by_applicant': {'is_signed': True, 'is_dated': True},
                   'acknowledgement_of_programs_offered': {'is_signed': True, 'is_dated': True},
                   'named_driver_exclusion': None, 'no_fault_accident_declaration': None,
                   'not_insurance_contract': {'is_signed': True, 'is_dated': True}, 'consumer_disclosure': None,
                   'non_owned_vehicle_coverage_endorsement': None, 'cancellation_request': None}},
    'broker_package': {"signed_date": "2021-09-23", "broker_fee": 432.49, "insured_name": "Olivares banesa wendy"},
    'crm_receipt':
        {'payment_date': '2021-07-13', 'reference_number': 'Receipt 1782-5122', 'name': 'Olivares, Wendy Banesa',
         'address': {'street': '1355 S Perris Blvd Apt 164', 'city': 'PERRIS', 'state': 'CA', 'zip': '92570'},
         'payment_notes': {'card_last_4_digit': 7181, 'notes': None}, 'payment_method': 'Credit/Debit Card',
         'vr_fee_amount': None, 'nb_eft_to_company_amount': 96.89, 'broker_fee_amount': 160.0,
         'policy_number': 'MIL4972376', 'line_of_business': 'Personal Auto', 'amount_paid': 256.89,
         'amount_left_to_pay': 0.0}, 'itc': {'insured_information': {'name': 'Wendy Banesa Olivares',
                                                                       'address': {'city': 'PERRIS',
                                                                                   'state': 'California',
                                                                                   'zip': '92570',
                                                                                   'street': '1355 S Perris Blvd Apt 164'}},
                                               'agent_information': {'name': 'Call Center II',
                                                                     'address': {'city': 'SAN BERNARDINO',
                                                                                 'state': 'California', 'zip': '92408'},
                                                                     'producer_code': '0038197'},
                                               'insurance_company': {'name': "Kemper Auto - Veronica's",
                                                                     'policy_term': 'Annual'},
                                               'driver_information': {'bi_amount_each_person': 15000,
                                                                      'bi_amount_each_accident': 30000,
                                                                      'pd_amount_each_accident': 5000,
                                                                      'uninsured_bi_amount_each_person': None,
                                                                      'uninsured_bi_amount_each_accident': None,
                                                                      'uninsured_pd_amount_each_accident': None,
                                                                      'excluded_drivers': None,
                                                                      'total_number_of_violations': 0, 'drivers': [
                                                       {'id': 1, 'name': 'Wendy Olivares banesa', 'gender': 'female',
                                                        'age': 29, 'marital_status': 'Single',
                                                        'date_of_birth': '1991-10-29', 'fr_filing': None,
                                                        'number_of_violations': 0,
                                                        'attributes': {'months_foreign_license': 1,
                                                                       'months_mvr_experience_us': 164}}]},
                                               'vehicle_information': {'vehicles': [
                                                   {'id': 1, 'vin': '4T3ZA3BB1AU023479', 'make': 'TOYOTA',
                                                    'model': 'VENZA', 'year': 2010, 'annual_miles_driven': 8500,
                                                    'comprehensive_deductible': 1000, 'collision_deductible': 1000}]},
                                               'signature': {'insured_information': {'is_signed': True},
                                                             'vehicle_information': {'is_signed': True},
                                                             'eod_information': {'is_signed': False}}},
    'driving_license': [
        {'address': '4039 MAXSON RD APT 3 EL MONTE, CA 91732', 'date_of_birth': '1991-10-29', 'gender': 'female',
         'license_number': 'F1567382', 'name': 'OLIVARES WENDY BANESA'}], 'artisan_use_letter':
        {'insured_name': 'OLIVARES WENDY BANESA', 'policy_number': 'MIL4972376',
         'vehicles': [{'year': 2010, 'make': 'TOYT', 'model': 'VENZA', 'vin': '4T3ZA3BB1AU023479'}],
         'signature': {'is_signed': True}}, 'non_owners_letter':
        {"insured_name": "OLIVARES WENDY BANESA", "policy_number": "MIL4972376", "company_name": "alliance-united",
         "signature": {"is_signed": True}}, "vr": [{"owners": ["GOMEZ LOURDES DERAS", 'OLIVARES WENDY BANESA'],
                                                     "vehicle": {'year': 2010, 'make': 'TOYT', 'model': 'VENZA',
                                                                 'vin': '4T3ZA3BB1AU023479'}}], "stripe_receipt": [
        {"receipt_number": "1782-5122", "amount_paid": 256.89, "date_paid": "2021-07-13",
         "payment_method": {"card_last_4_digit": 7181}}], "eft": [
        {"insured_name": "OLIVARES WENDY BANESA", "policy_number": "MIL4972376",
         "signature": {"insured_signature": {"is_signed": True, "is_dated": True},
                       "card_holder_signature": {"is_signed": True, "is_dated": True}}}], "registration": [
        {"owners": ["OLIVARES WENDY BANESA", 'Alfonso Soto'], "is_valid": True,
         "vehicle": {'year': 2010, 'make': 'TOYT', 'vin': '4T3ZA3BB1AU023479', "history": None, "model": None}}],
    "promise_to_provide": {"signature": {"agreed_to_be": {"is_signed": True},
                                         "condition_and_acknowledgement_agreement": {"is_signed": False}},
                           "applied_coverage_effective_date": "2021-10-01",
                           "promise_to_provide_by_date": "2021-10-16",
                           "promise_to_provide_agreement_date": ["2021-10-01", "2021-10-01", "2021-10-01"]}
}


async def test__get_itc_driver_by_name_valid():
    data = await deserialize(valid_data)
    name = 'WENDY'
    obj = driver_information.DriverInformationVerifier(uuid=uuid, data=data)

    x = await obj._DriverInformationVerifier__get_itc_driver_by_name(name)
    response = None
    assert x == response


async def test__verify_driver_relationship_valid():
    data = await deserialize(valid_data)
    driver = await deserialize(valid_data['insurance_application']['driver_information']['drivers'][0])
    insured_driver = await deserialize(valid_data['insurance_application']['driver_information']['drivers'][0])
    relationship_in_application = ['Named Insured']
    obj = driver_information.DriverInformationVerifier(uuid=uuid, data=data)
    x = await obj._DriverInformationVerifier__verify_driver_relationship(driver, insured_driver,
                                                                         relationship_in_application)
    response = {'source': SRC_INSURANCE_APPLICATION, 'target': {TRG_INS_APP: True}}
    assert x == response


async def test__verify_name_true():
    data = await deserialize(valid_data)
    dl = await deserialize(valid_data['driving_license'][0])
    app = await deserialize(valid_data['insurance_application']['driver_information']['drivers'][0])
    mvr = await deserialize(valid_data['mvr'][0])
    obj = driver_information.DriverInformationVerifier(uuid=uuid, data=data)
    x = await obj._DriverInformationVerifier__verify_name(app, dl, mvr)
    response = {'source': SRC_DRIVING_LICENSE,
                'target': {TRG_BROKER_PACKAGE: True, TRG_CRM_RECEIPT: True, TRG_INS_APP: True, TRG_ITC: True,
                           TRG_MVR: True, TRG_PUL: True, TRG_AUL: True, TRG_NOL: True, TRG_REGISTRATION: True,
                           TRG_VR: True}}
    assert x == response


async def test__verify_name_false():
    data = await deserialize(valid_data)
    dl = await deserialize(valid_data['driving_license'][0])
    app = await deserialize(valid_data['insurance_application']['driver_information']['drivers'][0])
    mvr = await deserialize(valid_data['mvr'][0])
    obj = driver_information.DriverInformationVerifier(uuid=uuid, data=data)

    app.name = 'ABC'
    obj.crm_receipt.name = 'ABC'
    obj.pleasure_use_letter.customer_name = 'ABC'
    obj.broker_package.insured_name = 'ABC'
    mvr.name = 'ABC'
    obj.itc.driver_information.drivers[0].name = 'ABC'
    obj.artisan_use_letter.insured_name = 'ABC'
    obj.non_owners_letter.insured_name = 'ABC'
    obj.registrations[0].owners = ['ABC', 'BCD']
    obj.vrs[0].owners = ['ABC', 'BCD']
    x = await obj._DriverInformationVerifier__verify_name(app, dl, mvr)
    response = {'source': SRC_DRIVING_LICENSE,
                'target': {TRG_BROKER_PACKAGE: False, TRG_CRM_RECEIPT: False, TRG_INS_APP: False, TRG_ITC: None,
                           TRG_MVR: False, TRG_PUL: False, TRG_AUL: False, TRG_NOL: False, TRG_REGISTRATION: False,
                           TRG_VR: False}}
    assert x == response


async def test__verify_name_source_none():
    data = await deserialize(valid_data)
    dl = await deserialize(valid_data['driving_license'][0])
    app = await deserialize(valid_data['insurance_application']['driver_information']['drivers'][0])
    mvr = await deserialize(valid_data['mvr'][0])
    obj = driver_information.DriverInformationVerifier(uuid=uuid, data=data)
    dl.name = None
    x = await obj._DriverInformationVerifier__verify_name(app, dl, mvr)
    response = None
    assert x == response


async def test__verify_name_target_none():
    data = await deserialize(valid_data)
    dl = await deserialize(valid_data['driving_license'][0])
    app = await deserialize(valid_data['insurance_application']['driver_information']['drivers'][0])
    mvr = await deserialize(valid_data['mvr'][0])
    obj = driver_information.DriverInformationVerifier(uuid=uuid, data=data)
    app.name = None
    obj.crm_receipt.name = None
    obj.pleasure_use_letter.customer_name = None
    obj.broker_package.insured_name = None
    mvr.name = None
    obj.itc.driver_information.drivers[0].name = None
    obj.artisan_use_letter.insured_name = None
    obj.non_owners_letter.insured_name = None
    obj.registrations[0].owners = None
    obj.vrs[0].owners = None
    x = await obj._DriverInformationVerifier__verify_name(app, dl, mvr)
    response = {'source': SRC_DRIVING_LICENSE,
                'target': {TRG_BROKER_PACKAGE: None, TRG_CRM_RECEIPT: None, TRG_INS_APP: None, TRG_ITC: None,
                           TRG_MVR: None, TRG_PUL: None, TRG_AUL: None, TRG_NOL: None, TRG_REGISTRATION: None,
                           TRG_VR: None}}
    assert x == response


async def test__verify_dob_valid():
    data = await deserialize(valid_data)
    dl = await deserialize(valid_data['driving_license'][0])
    mvr = await deserialize(valid_data['mvr'][0])
    app = await deserialize(valid_data['insurance_application']['driver_information']['drivers'][0])
    obj = driver_information.DriverInformationVerifier(uuid=uuid, data=data)
    x = await obj._DriverInformationVerifier__verify_dob(app, dl, mvr)
    response = {'source': SRC_DRIVING_LICENSE, 'target': {TRG_INS_APP: True, TRG_ITC: True, TRG_MVR: True}}
    assert x == response


async def test__verify_license_number_valid():
    data = await deserialize(valid_data)
    dl = await deserialize(valid_data['driving_license'][0])
    mvr = await deserialize(valid_data['driving_license'][0])

    app = await deserialize(valid_data['insurance_application']['driver_information']['drivers'][0])
    obj = driver_information.DriverInformationVerifier(uuid=uuid, data=data)
    x = await obj._DriverInformationVerifier__verify_license_number(app, dl, mvr)
    response = {'source': SRC_DRIVING_LICENSE, 'target': {TRG_INS_APP: True, TRG_MVR: True}}
    assert x == response


async def test__verify_marital_status_valid():
    data = await deserialize(valid_data)
    itc = await deserialize(valid_data['itc']['driver_information']['drivers'][0])
    app = await deserialize(valid_data['insurance_application']['driver_information']['drivers'][0])
    itc.marital_status = 'Single'
    app.marital_status = 'Single'
    obj = driver_information.DriverInformationVerifier(uuid=uuid, data=data)
    x = await obj._DriverInformationVerifier__verify_marital_status(app, itc)
    response = {'source': SRC_INSURANCE_APPLICATION, 'target': {SRC_ITC: True}}
    assert x == response


async def test__verify_number_of_violation_valid():
    data = await deserialize(valid_data)
    itc = await deserialize(valid_data['itc']['driver_information']['drivers'][0])
    mvr = await deserialize(valid_data['mvr'][0])
    itc.number_of_violations = 1
    mvr.number_of_violations = 1
    obj = driver_information.DriverInformationVerifier(uuid=uuid, data=data)
    x = await obj._DriverInformationVerifier__verify_number_of_violation(mvr, itc)
    response = {'source': SRC_MVR, 'target': {TRG_ITC: True}}
    assert x == response


async def test__verify_driving_experience_valid():
    data = await deserialize(valid_data)
    itc = await deserialize(valid_data['itc']['driver_information']['drivers'][0])
    app = await deserialize(valid_data['insurance_application']['driver_information']['drivers'][0])
    itc.marital_status = 100
    app.marital_status = 111
    obj = driver_information.DriverInformationVerifier(uuid=uuid, data=data)
    x = await obj._DriverInformationVerifier__verify_driving_experience(app, itc)
    response = {'source': SRC_ITC, 'target': {SRC_INSURANCE_APPLICATION: True}}
    assert x == response


async def test__verify_sr_filing_valid():
    data = await deserialize(valid_data)
    itc = await deserialize(valid_data['itc']['driver_information']['drivers'][0])
    app = await deserialize(valid_data['insurance_application']['driver_information']['drivers'][0])
    itc.fr_filing = None
    app.sr_filing = True
    obj = driver_information.DriverInformationVerifier(uuid=uuid, data=data)
    x = await obj._DriverInformationVerifier__verify_sr_filing(app, itc)
    response = {'source': SRC_ITC, 'target': {TRG_ITC: None}}
    assert x == response


async def test__verify_status_valid():
    data = await deserialize(valid_data)

    app = await deserialize(valid_data['insurance_application']['driver_information']['drivers'][0])
    obj = driver_information.DriverInformationVerifier(uuid=uuid, data=data)
    x = await obj._DriverInformationVerifier__verify_status(app)
    response = {'source': SRC_ITC, 'target': {TRG_INS_APP: False}}
    assert x == response


async def test__verify_driver_info_valid():
    data = await deserialize(valid_data)
    obj = driver_information.DriverInformationVerifier(uuid=uuid, data=data)
    x = await obj._DriverInformationVerifier__verify_driver_info()
    response = [
        {'date_of_birth': {'source': SRC_DRIVING_LICENSE, 'target': {TRG_INS_APP: True, TRG_ITC: True, TRG_MVR: True}},
         'gender': {'source': SRC_DRIVING_LICENSE, 'target': {TRG_INS_APP: True, TRG_ITC: True, TRG_MVR: True}},
         'license_number': {'source': SRC_DRIVING_LICENSE, 'target': {TRG_INS_APP: True, TRG_MVR: True}},
         'driving_experience': {'source': 'itc', 'target': {'insurance-application': True}}, 'id': 1,
         'marital_status': {'source': 'insurance-application', 'target': {'itc': True}},
         'name': {'source': SRC_DRIVING_LICENSE,
                  'target': {TRG_BROKER_PACKAGE: True, TRG_CRM_RECEIPT: True, TRG_INS_APP: True, TRG_ITC: True,
                             TRG_MVR: True, TRG_PUL: True, TRG_AUL: True, TRG_NOL: True, TRG_REGISTRATION: True,
                             TRG_VR: True}}, 'number_of_violation': None,
         'relationship': {'source': SRC_INSURANCE_APPLICATION, 'target': {TRG_INS_APP: True}}, 'sr_filing': None,
         'status': {'source': SRC_ITC, 'target': {TRG_INS_APP: False}}}]
    assert x == response
