import asyncio

from app.service.api.v1.insurance_application.verifier_v1.alliance_united import InsuredInformationVerifier, \
    PaymentInformationVerifier, PolicyInformationVerifier, DriverInformationVerifier, \
    VehicleInformationVerifier, CoverageInformationVerifier, CompanyInformationVerifier, SignatureVerifier, \
    PromiseToProvideVerifier
from app.service.api.v1.insurance_application.verifier_v1.alliance_united.base import AllianceUnitedV1


class AllianceUnitedVerifyV1():
    def __init__(self, uuid, data):
        self.uuid = uuid
        self.data = data

    async def verify(self):
        alliance_united = AllianceUnitedV1(self.uuid, self.data)
        insured_info_verifier = InsuredInformationVerifier(self.uuid, self.data)
        policy_info_verifier = PolicyInformationVerifier(self.uuid, self.data)
        payment_info_verifier = PaymentInformationVerifier(self.uuid, self.data)
        driver_info_verifier = DriverInformationVerifier(self.uuid, self.data)
        vehicle_info_verifier = VehicleInformationVerifier(self.uuid, self.data)
        coverage_info_verifier = CoverageInformationVerifier(self.uuid, self.data)
        company_info_verifier = CompanyInformationVerifier(self.uuid, self.data)
        signature_verifier = SignatureVerifier(self.uuid, self.data)
        promise_to_provide_verifier = PromiseToProvideVerifier(self.uuid, self.data)
        insured_info, policy_info, payment_info, line_of_business, driver_info, vehicle_info, coverage_info, \
        company_info, signature, promise_to_provide = await asyncio.gather(insured_info_verifier.verify(),
                                                                           policy_info_verifier.verify(),
                                                                           payment_info_verifier.verify(),
                                                                           alliance_united.verify_line_of_business(),
                                                                           driver_info_verifier.verify(),
                                                                           vehicle_info_verifier.verify(),
                                                                           coverage_info_verifier.verify(),
                                                                           company_info_verifier.verify(),
                                                                           signature_verifier.verify(),
                                                                           promise_to_provide_verifier.verify())

        verification = {'insured_information': insured_info,
                        'policy_information': policy_info,
                        'payment_information': payment_info,
                        'line_of_business': line_of_business,
                        'driver_information': driver_info,
                        'vehicle_information': vehicle_info,
                        'coverage_information': coverage_info,
                        'company_information': company_info,
                        'signature': signature,
                        'promise_to_provide_information': promise_to_provide}
        return verification
