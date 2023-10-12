from app.constant import TRG_AGREED_TO_PAY, TRG_PROMISE_TO_PROVIDE, TRG_PTP, SRC_PTP
from app.service.api.v1.insurance_application.verifier_v1.alliance_united import promise_to_provide_information
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
    'broker_package': {"signed_date": "2021-09-23", "broker_fee": 432.49, "insured_name": "urza flores luis"},
    'crm_receipt': {'payment_date': '2021-07-13', 'reference_number': 'Receipt 1782-5122', 'name': 'Olivares, Wendy',
                    'address': {'street': '1355 S Perris Blvd Apt 164', 'city': 'PERRIS', 'state': 'CA',
                                'zip': '92570'}, 'payment_notes': {'card_last_4_digit': 7181, 'notes': None},
                    'payment_method': 'Credit/Debit Card', 'vr_fee_amount': None, 'nb_eft_to_company_amount': 96.89,
                    'broker_fee_amount': 160.0, 'policy_number': 'MIL4972376', 'line_of_business': 'Personal Auto',
                    'amount_paid': 256.89, 'amount_left_to_pay': 0.0}, 'itc': {
        'insured_information': {'name': 'Wendy Banesa Olivares',
                                'address': {'city': 'PERRIS', 'state': 'California', 'zip': '92570',
                                            'street': '1355 S Perris Blvd Apt 164'}},
        'agent_information': {'name': 'Call Center II',
                              'address': {'city': 'SAN BERNARDINO', 'state': 'California', 'zip': '92408'},
                              'producer_code': '0038197'},
        'insurance_company': {'name': "Kemper Auto - Veronica's", 'policy_term': 'Annual'},
        'driver_information': {'bi_amount_each_person': 15000, 'bi_amount_each_accident': 30000,
                               'pd_amount_each_accident': 5000, 'uninsured_bi_amount_each_person': None,
                               'uninsured_bi_amount_each_accident': None, 'uninsured_pd_amount_each_accident': None,
                               'excluded_drivers': None, 'total_number_of_violations': 0, 'drivers': [
                {'id': 1, 'name': 'Wendy Olivares', 'gender': 'female', 'age': 29, 'marital_status': 'Single',
                 'date_of_birth': '1991-10-29', 'fr_filing': None, 'number_of_violations': 0,
                 'attributes': {'months_foreign_license': 1, 'months_mvr_experience_us': 164}}]},
        'vehicle_information': {'vehicles': [
            {'id': 1, 'vin': '4T3ZA3BB1AU023479', 'make': 'TOYOTA', 'model': 'VENZA', 'year': 2010,
             'annual_miles_driven': 8500, 'comprehensive_deductible': 1000, 'collision_deductible': 1000}]},
        'signature': {'insured_information': {'is_signed': True}, 'vehicle_information': {'is_signed': True},
                      'eod_information': {'is_signed': False}}}, 'driving_license': [
        {'address': '4039 MAXSON RD APT 3 EL MONTE, CA 91732', 'date_of_birth': '1991-10-29', 'gender': 'female',
         'license_number': 'F1567382', 'name': 'OLIVARES WENDY BANESA'}], 'artisan_use_letter': [
        {'insured_name': 'OLIVARES WENDY BANESA', 'policy_number': 'MIL4972376',
         'vehicles': [{'year': 2010, 'make': 'TOYT', 'model': 'VENZA', 'vin': '4T3ZA3BB1AU023479'}],
         'signature': {'is_signed': True}}], 'non_owners_letter': [
        {"insured_name": "OLIVARES WENDY BANESA", "policy_number": "MIL4972376", "company_name": "alliance-united",
         "signature": {"is_signed": True}}], "vr": [{"owners": ["GOMEZ LOURDES DERAS"],
                                                     "vehicle": {'year': 2010, 'make': 'TOYT', 'model': 'VENZA',
                                                                 'vin': '4T3ZA3BB1AU023479'}}], "stripe_receipt": [
        {"receipt_number": "1782-5122", "amount_paid": 256.89, "date_paid": "2021-07-13",
         "payment_method": {"card_last_4_digit": 7181}}], "eft": [
        {"insured_name": "OLIVARES WENDY BANESA", "policy_number": "MIL4972376",
         "signature": {"insured_signature": {"is_signed": True, "is_dated": True},
                       "card_holder_signature": {"is_signed": True, "is_dated": True}}}], "registration": [
        {"owners": ["OLIVARES WENDY BANESA"], "is_valid": True,
         "vehicle": {'year': 2010, 'make': 'TOYT', 'vin': '4T3ZA3BB1AU023479', "history": None, "model": None}}],
    "promise_to_provide": {"signature": {"agreed_to_be": {"is_signed": True},
                                         "condition_and_acknowledgement_agreement": {"is_signed": False}},
                           "applied_coverage_effective_date": "2021-10-01",
                           "promise_to_provide_by_date": "2021-10-16",
                           "promise_to_provide_agreement_date": ["2021-10-01", "2021-10-01", "2021-10-01"]}}


async def test__verify_agree_to_pay_date_1():
    data = await deserialize(valid_data)
    obj = promise_to_provide_information.PromiseToProvideVerifier(uuid=uuid, data=data)
    x = await obj._PromiseToProvideVerifier__verify_agree_to_pay_date()
    response = {'source': SRC_PTP, 'target': {TRG_PTP: True}}
    assert x == response


async def test__verify_agree_to_pay_date_2():
    data = await deserialize(valid_data)
    obj = promise_to_provide_information.PromiseToProvideVerifier(uuid=uuid, data=data)
    obj.promise_to_provide.promise_to_provide_agreement_date[1] = '2022-10-02'
    x = await obj._PromiseToProvideVerifier__verify_agree_to_pay_date()
    response = {'source': SRC_PTP, 'target': {TRG_PTP: False}}
    assert x == response


async def test__verify_agree_to_pay_date_3():
    data = await deserialize(valid_data)
    obj = promise_to_provide_information.PromiseToProvideVerifier(uuid=uuid, data=data)
    obj.promise_to_provide.promise_to_provide_agreement_date = None
    x = await obj._PromiseToProvideVerifier__verify_agree_to_pay_date()
    response = {'source': SRC_PTP, 'target': {TRG_PTP: None}}
    assert x == response


# After a one week
async def test__verify_promise_to_provide_date_false1():
    data = await deserialize(valid_data)
    obj = promise_to_provide_information.PromiseToProvideVerifier(uuid=uuid, data=data)
    obj.promise_to_provide.promise_to_provide_by_date = '2021-10-08'
    x = await obj._PromiseToProvideVerifier__verify_promise_to_provide_date()
    response = {'source': SRC_PTP, 'target': {TRG_PTP: False}}
    assert x == response


# Previous Day
async def test__verify_promise_to_provide_date_false2():
    data = await deserialize(valid_data)
    obj = promise_to_provide_information.PromiseToProvideVerifier(uuid=uuid, data=data)
    obj.promise_to_provide.promise_to_provide_by_date = '2021-09-30'
    x = await obj._PromiseToProvideVerifier__verify_promise_to_provide_date()
    response = {'source': SRC_PTP, 'target': {TRG_PTP: False}}
    assert x == response


# Same Day
async def test__verify_promise_to_provide_date_true1():
    data = await deserialize(valid_data)
    obj = promise_to_provide_information.PromiseToProvideVerifier(uuid=uuid, data=data)
    obj.promise_to_provide.promise_to_provide_by_date = '2021-10-01'
    x = await obj._PromiseToProvideVerifier__verify_promise_to_provide_date()
    response = {'source': SRC_PTP, 'target': {TRG_PTP: True}}
    assert x == response


# Next Day
async def test__verify_promise_to_provide_date_true2():
    data = await deserialize(valid_data)
    obj = promise_to_provide_information.PromiseToProvideVerifier(uuid=uuid, data=data)
    obj.promise_to_provide.promise_to_provide_by_date = '2021-10-02'
    x = await obj._PromiseToProvideVerifier__verify_promise_to_provide_date()
    response = {'source': SRC_PTP, 'target': {TRG_PTP: True}}
    assert x == response


async def test_verify_none():
    data = await deserialize(valid_data)
    obj = promise_to_provide_information.PromiseToProvideVerifier(uuid=uuid, data=data)
    obj.promise_to_provide = None
    x = await obj.verify()
    response = None
    assert x == response


async def test__verify_promise_to_provide_date_invalid_date():
    data = await deserialize(valid_data)
    obj = promise_to_provide_information.PromiseToProvideVerifier(uuid=uuid, data=data)
    obj.promise_to_provide.promise_to_provide_by_date = '2021-09-31'
    x = await obj._PromiseToProvideVerifier__verify_promise_to_provide_date()
    response = {'source': SRC_PTP, 'target': {TRG_PTP: None}}
    assert x == response


async def test__verify_promise_to_provide_date_none():
    data = await deserialize(valid_data)
    obj = promise_to_provide_information.PromiseToProvideVerifier(uuid=uuid, data=data)
    obj.promise_to_provide.promise_to_provide_by_date = None
    x = await obj._PromiseToProvideVerifier__verify_promise_to_provide_date()
    response = {'source': SRC_PTP, 'target': {TRG_PTP: None}}
    assert x == response


async def test_verify_source_none():
    data = await deserialize(valid_data)
    obj = promise_to_provide_information.PromiseToProvideVerifier(uuid=uuid, data=data)
    obj.promise_to_provide.applied_coverage_effective_date = None
    x = await obj.verify()
    response = {TRG_AGREED_TO_PAY: None, TRG_PROMISE_TO_PROVIDE: None}
    assert x == response


async def test_verify_document_none():
    data = await deserialize(valid_data)
    obj = promise_to_provide_information.PromiseToProvideVerifier(uuid=uuid, data=data)
    obj.promise_to_provide = None
    x = await obj.verify()
    response = None
    assert x == response


async def test_verify_valid1():
    data = await deserialize(valid_data)
    obj = promise_to_provide_information.PromiseToProvideVerifier(uuid=uuid, data=data)
    x = await obj.verify()
    response = {TRG_AGREED_TO_PAY: {'source': SRC_PTP,
                                    'target': {TRG_PTP: True}},
                TRG_PROMISE_TO_PROVIDE: {'source': SRC_PTP,
                                         'target': {TRG_PTP: False}}}
    assert x == response


async def test_verify_valid2():
    data = await deserialize(valid_data)
    obj = promise_to_provide_information.PromiseToProvideVerifier(uuid=uuid, data=data)
    obj.promise_to_provide.promise_to_provide_by_date = '2021-10-02'
    x = await obj.verify()
    response = {TRG_AGREED_TO_PAY: {'source': SRC_PTP,
                                    'target': {TRG_PTP: True}},
                TRG_PROMISE_TO_PROVIDE: {'source': SRC_PTP,
                                         'target': {TRG_PTP: True}}}
    assert x == response


async def test_verify_valid3():
    data = await deserialize(valid_data)
    obj = promise_to_provide_information.PromiseToProvideVerifier(uuid=uuid, data=data)
    obj.promise_to_provide.promise_to_provide_by_date = None
    obj.promise_to_provide.promise_to_provide_agreement_date = None
    x = await obj.verify()
    response = {TRG_AGREED_TO_PAY: {'source': SRC_PTP,
                                    'target': {TRG_PTP: None}},
                TRG_PROMISE_TO_PROVIDE: {'source': SRC_PTP,
                                         'target': {TRG_PTP: None}}}
    assert x == response
