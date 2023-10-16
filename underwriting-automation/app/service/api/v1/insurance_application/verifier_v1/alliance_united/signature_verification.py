import asyncio

from app import logger
from app.constant import TRG_INS_APP, TRG_NOL, TRG_AUL, TRG_EFT, \
    TRG_BROKER_PACKAGE, TRG_ITC, TRG_PUL, TRG_PTP, TRG_MVR
from app.service.api.v1.insurance_application.verifier_v1.alliance_united.base import AllianceUnitedV1
from app.service.helper.serializer_helper import serialize


class SignatureVerifier(AllianceUnitedV1):

    def __init__(self, uuid, data):
        super(SignatureVerifier, self).__init__(uuid, data)

    async def __verify_application_signatures(self):
        signature = None
        if self.application and self.application.signature:
            signature = await serialize(self.application.signature)
        return signature

    async def __verify_itc_signatures(self):
        signature = None
        if self.itc and self.itc.signature:
            signature = await serialize(self.itc.signature)
        return signature

    async def __verify_broker_package_signatures(self):
        signature = None
        if self.broker_package and self.broker_package.signature:
            signature = await serialize(self.broker_package.signature)
        return signature

    async def __verify_pleasure_use_letter_signatures(self):
        signature = None
        if self.pleasure_use_letter and self.pleasure_use_letter.signature:
            signature = await serialize(self.pleasure_use_letter.signature)
        return signature

    async def __verify_artisan_use_letter_signatures(self):
        signature = None
        if self.artisan_use_letter and self.artisan_use_letter.signature:
            signature = await serialize(self.artisan_use_letter.signature)
        return signature

    async def __verify_non_owners_letter_signatures(self):
        signature = None
        if self.non_owners_letter and self.non_owners_letter.signature:
            signature = await serialize(self.non_owners_letter.signature)
        return signature

    async def __verify_eft_signatures(self):
        signature = None
        if self.eft and self.eft.signature:
            signature = await serialize(self.eft.signature)
        return signature

    async def __verify_promise_to_provide_signatures(self):
        signature = None
        if self.promise_to_provide and self.promise_to_provide.signature:
            signature = await serialize(self.promise_to_provide.signature)
        return signature

    async def __verify_mvr_signatures(self):
        signature = None
        if self.application and self.driving_licenses:
            insured_dl = await self.get_insured_dl_by_license_number(self.application, self.driving_licenses)
            insured_mvr = await self.get_insured_mvr_by_license_number(insured_dl, self.mvrs)
            if insured_mvr:
                signature = await serialize(insured_mvr.signature)
        return signature

    async def verify(self):
        signature = {}
        signature[TRG_INS_APP], signature[TRG_ITC], signature[TRG_BROKER_PACKAGE], signature[
            TRG_AUL], signature[TRG_NOL], signature[TRG_EFT], signature[TRG_PUL], signature[
            TRG_PTP],signature[TRG_MVR] = await asyncio.gather(
            self.__verify_application_signatures(), self.__verify_itc_signatures(),
            self.__verify_broker_package_signatures(),
            self.__verify_artisan_use_letter_signatures(),
            self.__verify_non_owners_letter_signatures(),
            self.__verify_eft_signatures(), self.__verify_pleasure_use_letter_signatures(),
            self.__verify_promise_to_provide_signatures(), self.__verify_mvr_signatures()
        )
        signature = {'signature': signature}
        return signature
