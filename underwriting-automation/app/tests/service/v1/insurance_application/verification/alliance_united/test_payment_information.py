from app.constant import TRG_BROKER_PACKAGE, TRG_CRM_RECEIPT, SRC_INSURANCE_APPLICATION, SRC_CRM_RECEIPT, \
    SRC_STRIPE_RECEIPT
from app.service.api.v1.insurance_application.verifier_v1.alliance_united import payment_information
from app.service.helper.serializer_helper import deserialize

uuid = '89c5de1c-4d25-11ec-8623-d1e221452fcd'
dl_address = '4039 MAXSON RD APT 3 EL MONTE, CA 91732'
valid_data = {'broker_package': {'signed_date': '2021-09-04', 'broker_fee': 190.6, 'insured_name': None,
                                  'signatures': {'disclosures': {'coverages': {'is_signed': True},
                                                                 'disclosure_of_driving_record': {'is_signed': True},
                                                                 'exclusion': {
                                                                     'uninsured_bi_or_pd_coverage': {'is_signed': True},
                                                                     'comprehensive_and_collision_coverage': {
                                                                         'is_signed': True},
                                                                     'business_or_commercial_use': {'is_signed': True},
                                                                     'named_drivers_limitation': {'is_signed': True}}},
                                                 'standard_broker_fee_disclosure': {'is_signed': True},
                                                 'broker_fee_agreement': {'client_initials': {'is_signed': True},
                                                                          'condition_and_acknowledgement_agreement': {
                                                                              'is_signed': True},
                                                                          'client_signature': {'is_signed': True}},
                                                 'text_messaging_consent_agreement': {'is_signed': True}}}, 'mvr': [
    {'name': 'MORREO, DENNIS', 'gender': 'male', 'date_of_birth': '1990-02-02', 'status': 'valid',
     'license_number': 'E2675148', 'number_of_violations': 0}], 'pleasure_use_letter': [
    {'company_name': 'ALLIANCE UNITED', 'customer_name': 'RONALD PEREZ', 'policy_number': 'MIL4835965',
     'vehicles': [{'year': 1994, 'make': 'TOYT', 'model': '1/2', 'vin': None}], 'signature': {'is_signed': True}}],
              'insurance_application': {'insured_information': {'name': 'DENNIS MORREO',
                                                                 'address': {'street': '63832 LANDON LN', 'state': 'CA',
                                                                             'zip': '92274-9253', 'city': 'THERMAL'}},
                                         'broker_information': {'name': "Veronica's Auto Insurance Services - Indio",
                                                                'address': {'city': 'SAN BERNARDINO'}},
                                         'policy_information': {'policy_number': 'MIL6006980',
                                                                'receipt_date': '2021-09-04', 'net_amount': 310.4,
                                                                'insurance_type': 'Auto Insurance',
                                                                'policy_term': 'Annual',
                                                                'policy_start_date': '2021-09-04',
                                                                'policy_end_date': '2022-03-04'},
                                         'driver_information': {'drivers': [
                                             {'id': 1, 'name': 'DENNIS MORREO', 'date_of_birth': '1990-02-02',
                                              'relationship': 'Named Insured', 'gender': 'Male',
                                              'marital_status': 'Married', 'status': 'Rated',
                                              'license_number': 'E2675148', 'license_state': 'CA',
                                              'driving_experience_in_years': 15, 'driving_experience_in_months': 180,
                                              'sr_filing': False},
                                             {'id': 2, 'name': 'BETTY EVANS BONNER', 'date_of_birth': '1995-08-16',
                                              'relationship': 'Spouse', 'gender': 'female', 'marital_status': 'Married',
                                              'status': 'Rated', 'license_number': 'F7620758', 'license_state': 'CA',
                                              'driving_experience_in_years': 10, 'driving_experience_in_months': 120,
                                              'sr_filing': True}]}, 'vehicle_information': {'vehicles': [
                      {'id': 1, 'year': 2000, 'make': 'JEEP', 'model': 'GRAND', 'trim': 'CHEROKEE',
                       'vehicle_use': 'Pleasure', 'vin': '1J4G248S2YC344388'}]},
                                         'coverage_information': {'bi_amount_each_person': 15000,
                                                                  'bi_amount_each_accident': 30000,
                                                                  'pd_amount_each_accident': 10000,
                                                                  'uninsured_bi_amount_each_person': None,
                                                                  'uninsured_bi_amount_each_accident': None,
                                                                  'uninsured_pd_amount_each_accident': None,
                                                                  'vehicles': None}, 'signatures': {
                      'third_party_designation': {'is_signed': True, 'is_dated': True},
                      'disclosure_of_all_household_members': {'is_signed': True, 'is_dated': True},
                      'rejection_of_bi_coverage': {'is_signed': True, 'is_dated': True},
                      'rejection_of_pd_coverage': {'is_signed': True, 'is_dated': True},
                      'vehicle_condition_certification': None,
                      'acknowledgements_by_applicant': {'is_signed': True, 'is_dated': True},
                      'acknowledgement_of_programs_offered': {'is_signed': True, 'is_dated': True},
                      'named_driver_exclusion': None, 'no_fault_accident_declaration': None,
                      'not_insurance_contract': {'is_signed': True, 'is_dated': True}, 'consumer_disclosure': None,
                      'non_owned_vehicle_coverage_endorsement': None, 'cancellation_request': None}}, 'crm_receipt':
        {'payment_date': '2021-09-04', 'reference_number': '1782-5122', 'name': 'MORREO, DENNIS',
         'address': {'street': '29001 Merris St', 'city': 'Highland', 'state': 'CA', 'zip': '92346-4411'},
         'payment_notes': {"card_last_4_digit": 7181, "notes": "NB"}, 'payment_method': 'Cash', 'vr_fee_amount': None,
         'nb_eft_to_company_amount': 310.39, 'broker_fee_amount': 190.6, 'policy_number': 'MIL6006980',
         'line_of_business': 'Personal Auto', 'amount_paid': 501.0, 'amount_left_to_pay': 0.0}, 'itc': {
        'insured_information': {'name': 'DENNIS MORREO',
                                'address': {'city': 'THERMAL', 'state': 'California', 'zip': '92274',
                                            'street': '63832 LANDON LN'}},
        'agent_information': {'name': "Veronica's Insurance",
                              'address': {'city': 'Indio', 'state': 'California', 'zip': '92201'},
                              'producer_code': '09016'},
        'insurance_company': {'name': "Kemper Auto - Veronica's", 'policy_term': 'Semi-Annual'},
        'driver_information': {'bi_amount_each_person': 15000, 'bi_amount_each_accident': 30000,
                               'pd_amount_each_accident': 10000, 'uninsured_bi_amount_each_person': None,
                               'uninsured_bi_amount_each_accident': None, 'uninsured_pd_amount_each_accident': None,
                               'excluded_drivers': [{'name': 'JAMES A HERNANDEZ', 'date_of_birth': '1990-02-19'}],
                               'total_number_of_violations': 0, 'drivers': [
                {'id': 2, 'name': None, 'gender': 'female', 'age': 26, 'marital_status': 'Married',
                 'date_of_birth': '1995-08-16', 'fr_filing': None, 'number_of_violations': 0,
                 'attributes': {'months_foreign_license': 0, 'months_mvr_experience_us': 187}},
                {'id': 1, 'name': None, 'gender': 'Male', 'age': 31, 'marital_status': 'Married',
                 'date_of_birth': '1990-02-02', 'fr_filing': None, 'number_of_violations': 0,
                 'attributes': {'months_foreign_license': 0, 'months_mvr_experience_us': 120}}]},
        'vehicle_information': {'vehicles': [
            {'id': 1, 'vin': '1J4G248S2YC344388', 'make': 'JEEP', 'model': 'GRAND CHEROKEE LARED', 'year': 2000,
             'annual_miles_driven': 8500, 'comprehensive_deductible': None, 'collision_deductible': None}]},
        'signature': {'insured_information': {'is_signed': True}, 'vehicle_information': {'is_signed': True},
                      'eod_information': {'is_signed': True}}}, 'driving_license': [
        {'address': None, 'date_of_birth': None, 'expiry_date': None, 'license_number': 'E2675148',
         'name': 'MORREO DENNIS'},
        {'address': None, 'date_of_birth': '4995-08-16', 'expiry_date': '2028-08-16', 'license_number': 'F7620758',
         'name': 'BONNER BETTY EVANS'}], 'artisan_use_letter': [
        {'insured_name': 'OLIVARES WENDY BANESA', 'policy_number': 'MIL4972376',
         'vehicles': [{'year': 2010, 'make': 'TOYT', 'model': 'VENZA', 'vin': '4T3ZA3BB1AU023479'}],
         'signature': {'is_signed': True}}], 'non_owners_letter': [
        {"insured_name": "OLIVARES WENDY BANESA", "policy_number": "MIL4972376", "company_name": "alliance-united",
         "signature": {"is_signed": True}}], "vr": [{"owners": ["GOMEZ LOURDES DERAS"],
                                                     "vehicle": {'year': 2010, 'make': 'TOYT', 'model': 'VENZA',
                                                                 'vin': '4T3ZA3BB1AU023479'}}], "stripe_receipt":
        {"receipt_number": "1782-5122", "amount_paid": 501.0, "payment_date": "2021-09-04",
         "payment_notes": {"card_last_4_digit": 7181}}, "eft":
        {"insured_name": "OLIVARES WENDY BANESA", "policy_number": "MIL4972376",
         "signature": {"insured_signature": {"is_signed": True, "is_dated": True},
                       "card_holder_signature": {"is_signed": True, "is_dated": True}}}, "registration": [
        {"owners": ["OLIVARES WENDY BANESA"], "is_valid": True,
         "vehicle": {'year': 2010, 'make': 'TOYT', 'vin': '4T3ZA3BB1AU023479', "history": None, "model": None}}],
              "promise_to_provide": {"signature": {"agreed_to_be": {"is_signed": True},
                                                   "condition_and_acknowledgement_agreement": {"is_signed": False}},
                                     "applied_coverage_effective_date": "2021-10-01",
                                     "promise_to_provide_by_date": "2021-10-16",
                                     "promise_to_provide_agreement_date": ["2021-10-01", "2021-10-01", "2021-10-01"]}
              }


async def test__verify_down_payment():
    data = await deserialize(valid_data)
    obj = payment_information.PaymentInformationVerifier(uuid=uuid, data=data)
    response = {'source': SRC_INSURANCE_APPLICATION, 'target': {TRG_CRM_RECEIPT: False}}
    x = await obj._PaymentInformationVerifier__verify_down_payment()
    assert x == response


async def test__verify_vr_fee():
    data = await deserialize(valid_data)
    obj = payment_information.PaymentInformationVerifier(uuid=uuid, data=data)
    response = None
    x = await obj._PaymentInformationVerifier__verify_vr_fee()
    assert x == response


async def test__verify_broker_fee():
    data = await deserialize(valid_data)
    obj = payment_information.PaymentInformationVerifier(uuid=uuid, data=data)
    response = {'source': SRC_CRM_RECEIPT, 'target': {TRG_BROKER_PACKAGE: True}}
    x = await obj._PaymentInformationVerifier__verify_broker_fee()
    assert x == response


async def test_verify_reference_number_valid():
    data = await deserialize(valid_data)
    obj = payment_information.PaymentInformationVerifier(uuid=uuid, data=data)
    response = {'source': SRC_STRIPE_RECEIPT, 'target': {TRG_CRM_RECEIPT: True}}
    x = await obj._PaymentInformationVerifier__verify_reference_number()
    assert x == response


async def test_verify_reference_number_invalid():
    data = await deserialize(valid_data)
    obj = payment_information.PaymentInformationVerifier(uuid=uuid, data=data)
    obj.crm_receipt.reference_number = None
    response = {'source': SRC_STRIPE_RECEIPT, 'target': {TRG_CRM_RECEIPT: None}}
    x = await obj._PaymentInformationVerifier__verify_reference_number()
    assert x == response


async def test_verify_reference_number_false():
    data = await deserialize(valid_data)
    obj = payment_information.PaymentInformationVerifier(uuid=uuid, data=data)
    obj.crm_receipt.reference_number = '123-456'
    response = {'source': SRC_STRIPE_RECEIPT, 'target': {TRG_CRM_RECEIPT: False}}
    x = await obj._PaymentInformationVerifier__verify_reference_number()
    assert x == response


async def test_verify_reference_number_source_none():
    data = await deserialize(valid_data)
    obj = payment_information.PaymentInformationVerifier(uuid=uuid, data=data)
    obj.stripe_receipt.receipt_number = None
    response = None
    x = await obj._PaymentInformationVerifier__verify_reference_number()
    assert x == response


async def test_verify_amount_paid_valid():
    data = await deserialize(valid_data)
    obj = payment_information.PaymentInformationVerifier(uuid=uuid, data=data)
    response = {'source': SRC_STRIPE_RECEIPT, 'target': {TRG_CRM_RECEIPT: True}}
    x = await obj._PaymentInformationVerifier__verify_amount_paid()
    assert x == response


async def test_verify_amount_paid_invalid():
    data = await deserialize(valid_data)
    obj = payment_information.PaymentInformationVerifier(uuid=uuid, data=data)
    obj.crm_receipt.amount_paid = None
    response = {'source': SRC_STRIPE_RECEIPT, 'target': {TRG_CRM_RECEIPT: None}}
    x = await obj._PaymentInformationVerifier__verify_amount_paid()
    assert x == response


async def test_verify_amount_paid_false():
    data = await deserialize(valid_data)
    obj = payment_information.PaymentInformationVerifier(uuid=uuid, data=data)
    obj.crm_receipt.amount_paid = 123
    response = {'source': SRC_STRIPE_RECEIPT, 'target': {TRG_CRM_RECEIPT: False}}
    x = await obj._PaymentInformationVerifier__verify_amount_paid()
    assert x == response


async def test_verify_amount_paid_source_none():
    data = await deserialize(valid_data)
    obj = payment_information.PaymentInformationVerifier(uuid=uuid, data=data)
    obj.stripe_receipt.amount_paid = None
    response = None
    x = await obj._PaymentInformationVerifier__verify_amount_paid()
    assert x == response


async def test_verify_payment_method_valid():
    data = await deserialize(valid_data)
    obj = payment_information.PaymentInformationVerifier(uuid=uuid, data=data)
    response = {'source': SRC_STRIPE_RECEIPT, 'target': {TRG_CRM_RECEIPT: True}}
    x = await obj._PaymentInformationVerifier__verify_payment_method()
    assert x == response


async def test_verify_payment_method_invalid():
    data = await deserialize(valid_data)
    obj = payment_information.PaymentInformationVerifier(uuid=uuid, data=data)
    obj.crm_receipt.payment_notes.card_last_4_digit = None
    response = {'source': SRC_STRIPE_RECEIPT, 'target': {TRG_CRM_RECEIPT: None}}
    x = await obj._PaymentInformationVerifier__verify_payment_method()
    assert x == response


async def test_verify_payment_method_false():
    data = await deserialize(valid_data)
    obj = payment_information.PaymentInformationVerifier(uuid=uuid, data=data)
    obj.crm_receipt.payment_notes.card_last_4_digit = '123'
    response = {'source': SRC_STRIPE_RECEIPT, 'target': {TRG_CRM_RECEIPT: False}}
    x = await obj._PaymentInformationVerifier__verify_payment_method()
    assert x == response


async def test_verify_payment_method_source_none():
    data = await deserialize(valid_data)
    obj = payment_information.PaymentInformationVerifier(uuid=uuid, data=data)
    obj.stripe_receipt.payment_notes.card_last_4_digit = None
    response = None
    x = await obj._PaymentInformationVerifier__verify_payment_method()
    assert x == response
    

async def test_verify_payment_date_valid():
    data = await deserialize(valid_data)
    obj = payment_information.PaymentInformationVerifier(uuid=uuid, data=data)
    response = {'source': SRC_STRIPE_RECEIPT, 'target': {TRG_CRM_RECEIPT: True}}
    x = await obj._PaymentInformationVerifier__verify_payment_date()
    assert x == response


async def test_verify_payment_date_invalid():
    data = await deserialize(valid_data)
    obj = payment_information.PaymentInformationVerifier(uuid=uuid, data=data)
    obj.crm_receipt.payment_date = None
    response = {'source': SRC_STRIPE_RECEIPT, 'target': {TRG_CRM_RECEIPT: None}}
    x = await obj._PaymentInformationVerifier__verify_payment_date()
    assert x == response


async def test_verify_payment_date_false():
    data = await deserialize(valid_data)
    obj = payment_information.PaymentInformationVerifier(uuid=uuid, data=data)
    obj.crm_receipt.payment_date = '2022-02-02'
    response = {'source': SRC_STRIPE_RECEIPT, 'target': {TRG_CRM_RECEIPT: False}}
    x = await obj._PaymentInformationVerifier__verify_payment_date()
    assert x == response


async def test_verify_payment_date_source_none():
    data = await deserialize(valid_data)
    obj = payment_information.PaymentInformationVerifier(uuid=uuid, data=data)
    obj.stripe_receipt.payment_date = None
    response = None
    x = await obj._PaymentInformationVerifier__verify_payment_date()
    assert x == response

async def test_verify_payment_date_source_diff_1():
    data = await deserialize(valid_data)
    obj = payment_information.PaymentInformationVerifier(uuid=uuid, data=data)
    obj.crm_receipt.payment_date = '2022-02-02'
    obj.stripe_receipt.payment_date = '2022-02-03'
    response = {'source': SRC_STRIPE_RECEIPT, 'target': {TRG_CRM_RECEIPT: True}}
    x = await obj._PaymentInformationVerifier__verify_payment_date()
    assert x == response

async def test_verify_payment_date_source_diff_invalid():
    data = await deserialize(valid_data)
    obj = payment_information.PaymentInformationVerifier(uuid=uuid, data=data)
    obj.crm_receipt.payment_date = '2022-02-02'
    obj.stripe_receipt.payment_date = '2022-02-06'
    response = {'source': SRC_STRIPE_RECEIPT, 'target': {TRG_CRM_RECEIPT: False}}
    x = await obj._PaymentInformationVerifier__verify_payment_date()
    assert x == response