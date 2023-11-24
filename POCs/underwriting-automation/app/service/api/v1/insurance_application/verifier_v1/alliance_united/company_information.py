from app import logger
from app.constant import SRC_INSURANCE_APPLICATION, TRG_PUL, InsuranceCompany, TRG_NOL
from app.service.api.v1.insurance_application.verifier_v1.alliance_united.base import AllianceUnitedV1


class CompanyInformationVerifier(AllianceUnitedV1):

    def __init__(self, uuid, data):
        super(CompanyInformationVerifier, self).__init__(uuid, data)

    async def verify(self):
        company_info = None
        try:
            is_valid_name = await self.verify_company_name()
            company_info = {'name': is_valid_name}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
        return company_info
