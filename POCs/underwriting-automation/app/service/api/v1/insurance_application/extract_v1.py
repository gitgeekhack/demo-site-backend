from app.constant import InsuranceCompany
from app.service.api.v1.insurance_application.extractor_v1 import alliance_united
from app import logger

class APPDataPointExtractorV1():
    def __init__(self, uuid, file):
        self.uuid = uuid
        self.file = file

    async def extract(self, company_name):
        data = None
        if company_name == InsuranceCompany.ALLIANCE_UNITED.value:
            extractor = alliance_united.APPAllianceUnitedDataPointExtractorV1(self.uuid, self.file)
            data = await extractor.extract()
        print(f'Request ID: [{self.uuid}] Response: {data}')

        return data
