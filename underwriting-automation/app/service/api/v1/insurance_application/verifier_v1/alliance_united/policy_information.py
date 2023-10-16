import asyncio

from app import logger
from app.constant import SRC_INSURANCE_APPLICATION, TRG_ITC, TRG_CRM_RECEIPT, TRG_PUL, \
    TRG_AUL, TRG_EFT, TRG_NOL
from app.service.api.v1.insurance_application.verifier_v1.alliance_united.base import AllianceUnitedV1


class PolicyInformationVerifier(AllianceUnitedV1):

    def __init__(self, uuid, data):
        super(PolicyInformationVerifier, self).__init__(uuid, data)

    async def __verify_policy_number(self):
        policy_number = None
        try:
            app_policy_number = self.application.policy_information.policy_number
        except AttributeError:
            return None
        try:
            crm_policy_number = self.crm_receipt.policy_number
        except AttributeError:
            crm_policy_number = None
        try:
            pul_policy_number = self.pleasure_use_letter.policy_number
        except AttributeError:
            pul_policy_number = None
        try:
            aul_policy_number = self.artisan_use_letter.policy_number
        except AttributeError:
            aul_policy_number = None
        try:
            eft_policy_number = self.eft.policy_number
        except AttributeError:
            eft_policy_number = None
        try:
            nol_policy_number = self.non_owners_letter.policy_number
        except AttributeError:
            nol_policy_number = None
        if app_policy_number:
            policy_number = {'source': SRC_INSURANCE_APPLICATION,
                             'target': {}}
            policy_number['target'][TRG_CRM_RECEIPT] = await self.is_equal(app_policy_number, crm_policy_number)
            policy_number['target'][TRG_PUL] = await self.is_equal(pul_policy_number, app_policy_number)
            policy_number['target'][TRG_AUL] = await self.is_equal(app_policy_number, aul_policy_number)
            policy_number['target'][TRG_EFT] = await self.is_equal(app_policy_number, eft_policy_number)
            policy_number['target'][TRG_NOL] = await self.is_equal(app_policy_number, nol_policy_number)
        return policy_number

    async def __verify_policy_term(self):
        policy_term = None
        try:
            policy_term = {'source': SRC_INSURANCE_APPLICATION}
            itc_policy = None
            if self.itc.insurance_company.policy_term:
                itc_policy = await self.is_equal(self.itc.insurance_company.policy_term,
                                                 self.application.policy_information.policy_term)
            policy_term['target'] = {TRG_ITC: itc_policy}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
            policy_term = None
        return policy_term

    async def verify(self):
        policy_info = None
        try:
            policy_number = policy_term = None
            if self.application.policy_information:
                policy_number, policy_term = await asyncio.gather(self.__verify_policy_number(),
                                                                  self.__verify_policy_term())
            policy_info = {'policy_number': policy_number,
                           'policy_term': policy_term}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
        return policy_info
