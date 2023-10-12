from app.constant import InsuranceCompany
from app.service.api.v1.insurance_application.verifier_v1 import AllianceUnitedVerifyV1
from app.service.helper.bulk_extract_v1 import BulkExtractV1
from app.service.helper.serializer_helper import deserialize


class DataPointVerifierV1():
    def __init__(self, uuid):
        self.uuid = uuid

    async def verify(self, zip_file, company_name):
        extractor = BulkExtractV1(self.uuid, company_name)
        data = await extractor.extract_by_zip(zip_file)
        deserialized_data = await deserialize(data)
        verification_data = None
        if company_name == InsuranceCompany.ALLIANCE_UNITED.value:
            verifier = AllianceUnitedVerifyV1(self.uuid, deserialized_data)
            verification_data = await verifier.verify()
        return verification_data
