from app import logger
from app.constant import SRC_INSURANCE_APPLICATION, TRG_CRM_RECEIPT, VerificationTemplate
from app.service.api.v1.insurance_application.verifier_v1.verify_abc import VerifyABC
from app.constant import SRC_INSURANCE_APPLICATION, TRG_PUL, InsuranceCompany, TRG_NOL


class AllianceUnitedV1(VerifyABC):

    def __init__(self, uuid, data):
        super(AllianceUnitedV1, self).__init__(uuid, data)
        self.driving_licenses = self.data.driving_license
        self.itc = self.data.itc
        self.crm_receipt = self.data.crm_receipt
        self.application = self.data.insurance_application
        self.mvrs = self.data.mvr
        self.broker_package = self.data.broker_package
        self.pleasure_use_letter = self.data.pleasure_use_letter
        self.non_owners_letter = self.data.non_owners_letter
        self.artisan_use_letter = self.data.artisan_use_letter
        self.registrations = self.data.registration
        self.vrs = self.data.vr
        self.eft = self.data.eft
        self.stripe_receipt = self.data.stripe_receipt
        self.promise_to_provide = self.data.promise_to_provide

    async def verify_line_of_business(self):
        line_of_business = None
        try:
            _line_of_business = None
            if self.crm_receipt.line_of_business and self.application.policy_information.insurance_type \
                    and self.application.policy_information.insurance_type in VerificationTemplate.LINE_OF_BUSINESS.keys():
                _line_of_business = await self.is_equal(VerificationTemplate.LINE_OF_BUSINESS[
                                                            self.application.policy_information.insurance_type],
                                                        self.crm_receipt.line_of_business)
            line_of_business_verification = {TRG_CRM_RECEIPT: _line_of_business}
            line_of_business = {'source': SRC_INSURANCE_APPLICATION, 'target': line_of_business_verification}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
        return line_of_business

    async def verify_company_name(self):
        try:
            pul_company_name = self.pleasure_use_letter.company_name
        except AttributeError:
            pul_company_name = None
        try:
            nol_company_name = self.non_owners_letter.company_name
        except AttributeError:
            nol_company_name = None
        is_valid_name = {'source': SRC_INSURANCE_APPLICATION, 'target': {
            TRG_PUL: await self.is_equal(InsuranceCompany.ALLIANCE_UNITED.value, pul_company_name),
            TRG_NOL: await self.is_equal(InsuranceCompany.ALLIANCE_UNITED.value, nol_company_name)}}
        return is_valid_name
