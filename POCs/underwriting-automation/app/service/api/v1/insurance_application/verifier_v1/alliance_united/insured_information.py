import asyncio

import us

from app import logger
from app.constant import SRC_DRIVING_LICENSE, TRG_ITC, TRG_INS_APP, TRG_CRM_RECEIPT, \
    TRG_PUL, TRG_MVR, TRG_BROKER_PACKAGE, TRG_AUL, TRG_NOL, TRG_EFT, TRG_REGISTRATION, TRG_VR
from app.service.api.v1.insurance_application.verifier_v1.alliance_united.base import AllianceUnitedV1


class InsuredInformationVerifier(AllianceUnitedV1):

    def __init__(self, uuid, data):
        super(InsuredInformationVerifier, self).__init__(uuid, data)

    async def __verify_multiple_owners_name(self, target_object, source_name):
        try:
            owners_name = [name for obj in target_object for name in obj.owners]
        except AttributeError:
            return None
        except TypeError:
            return None
        for name in owners_name:
            if await self.is_equal(name, source_name):
                return True
        return False

    async def __verify_insured_name(self):
        name = None
        insured_dl = await self.get_insured_dl_by_license_number(self.application, self.driving_licenses)
        insured_mvr = await self.get_insured_mvr_by_license_number(insured_dl, self.mvrs)
        try:
            dl_name = insured_dl.name
        except AttributeError:
            return None
        try:
            app_name = self.application.insured_information.name
        except AttributeError:
            app_name = None
        try:
            crm_name = self.crm_receipt.name
        except AttributeError:
            crm_name = None
        try:
            pul_name = self.pleasure_use_letter.customer_name
        except AttributeError:
            pul_name = None
        try:
            bp_name = self.broker_package.insured_name
        except AttributeError:
            bp_name = None
        try:
            mvr_name = insured_mvr.name
        except AttributeError:
            mvr_name = None
        try:
            itc_name = self.itc.insured_information.name
        except AttributeError:
            itc_name = None
        try:
            aul_name = self.artisan_use_letter.insured_name
        except AttributeError:
            aul_name = None
        try:
            nol_name = self.non_owners_letter.insured_name
        except AttributeError:
            nol_name = None
        try:
            eft_name = self.eft.insured_name
        except AttributeError:
            eft_name = None
        if dl_name:
            name = {'source': SRC_DRIVING_LICENSE, 'target': {}}
            name['target'][TRG_INS_APP] = await self.is_equal(app_name, dl_name)
            name['target'][TRG_CRM_RECEIPT] = await self.is_equal(crm_name, dl_name)
            name['target'][TRG_ITC] = await self.is_equal(itc_name, dl_name)
            name['target'][TRG_PUL] = await self.is_equal(pul_name, dl_name)
            name['target'][TRG_BROKER_PACKAGE] = await self.is_equal(bp_name, dl_name)
            name['target'][TRG_MVR] = await self.is_equal(mvr_name, dl_name)
            name['target'][TRG_AUL] = await self.is_equal(aul_name, dl_name)
            name['target'][TRG_NOL] = await self.is_equal(nol_name, dl_name)
            name['target'][TRG_EFT] = await self.is_equal(eft_name, dl_name)
            name['target'][TRG_REGISTRATION] = await self.__verify_multiple_owners_name(self.registrations, dl_name)
            name['target'][TRG_VR] = await self.__verify_multiple_owners_name(self.vrs, dl_name)
        return name

    async def __verify_with_crm_address(self, dl_address):
        crm_verify_flag = None
        try:
            crm_full_address = ' '.join(
                [self.crm_receipt.address.street, self.crm_receipt.address.city, self.crm_receipt.address.state,
                 self.crm_receipt.address.zip])
            crm_verify_flag = await self.is_equal(crm_full_address, dl_address)
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
        return crm_verify_flag

    async def __verify_with_itc_address(self, dl_address):
        itc_verify_flag = False
        try:
            state_abbrev = self.itc.insured_information.address.state
            itc_full_address = ' '.join(
                [self.itc.insured_information.address.street, self.itc.insured_information.address.city,
                 us.states.lookup(state_abbrev).abbr, self.itc.insured_information.address.zip])
            itc_verify_flag = await self.is_equal(itc_full_address, dl_address)
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
        return itc_verify_flag

    async def __verify_with_app_address(self, dl_address):
        dl_verify_flag = None
        try:
            if dl_address and ',' in dl_address:
                dl_zip = dl_address.split()[-1]
                dl_street_state_city = dl_address.replace(dl_zip, '')
                app_street_state_city = ' '.join(
                    [self.application.insured_information.address.street,
                     self.application.insured_information.address.city,
                     self.application.insured_information.address.state])
                dl_street_state_city_flag = await self.is_equal(dl_street_state_city,
                                                                app_street_state_city)
                dl_zip_flag = await self.is_subset(dl_zip, self.application.insured_information.address.zip)
                dl_verify_flag = dl_street_state_city_flag & dl_zip_flag
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
            dl_verify_flag = None
        return dl_verify_flag

    async def __verify_insured_address(self):
        try:
            insured_dl = await self.get_insured_dl_by_license_number(self.application, self.driving_licenses)
            address = None
            if insured_dl and insured_dl.address:
                address = {'source': SRC_DRIVING_LICENSE, 'target': {}}
                address['target'][TRG_ITC] = await self.__verify_with_itc_address(insured_dl.address)
                address['target'][TRG_INS_APP] = await self.__verify_with_app_address(insured_dl.address)
                address['target'][TRG_CRM_RECEIPT] = await self.__verify_with_crm_address(insured_dl.address)
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
            address = None
        return address

    async def __verify_itc_dob(self, source_dob):
        insured_itc = await self.get_object_by_id(self.itc.driver_information.drivers, 1)
        return await self.is_equal(insured_itc.date_of_birth, source_dob)

    async def __verify_dob_mvr(self, insured_dl):
        insured_mvr = await self.get_insured_mvr_by_license_number(insured_dl, self.mvrs)
        return await self.is_equal(insured_mvr.date_of_birth, insured_dl.date_of_birth)

    async def __verify_app_dob(self, source_dob):
        insured_app = await self.get_object_by_id(self.application.driver_information.drivers, 1)
        return await self.is_equal(insured_app.date_of_birth, source_dob)

    async def __verify_insured_dob(self):
        date_of_birth = None
        try:
            insured_dl = await self.get_insured_dl_by_license_number(self.application, self.driving_licenses)
            if insured_dl and insured_dl.date_of_birth:
                date_of_birth = {'source': SRC_DRIVING_LICENSE, 'target': {}}
                date_of_birth['target'][TRG_INS_APP] = await self.__verify_app_dob(
                    insured_dl.date_of_birth)
                date_of_birth['target'][TRG_ITC] = await self.__verify_itc_dob(insured_dl.date_of_birth)
                date_of_birth['target'][TRG_MVR] = await self.__verify_dob_mvr(insured_dl)
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
            date_of_birth = None
        return date_of_birth

    async def __verify_insured_license_number(self):
        license_number = None
        try:
            insured_dl = await self.get_insured_dl_by_license_number(self.application, self.driving_licenses)
            insured_mvr = await self.get_insured_mvr_by_license_number(insured_dl, self.mvrs)
            if insured_dl:
                license_number = {'source': SRC_DRIVING_LICENSE,
                                  'target': {TRG_INS_APP: True if insured_dl else None,
                                             TRG_MVR: True if insured_mvr else None}}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
            license_number = None
        return license_number

    async def verify(self):
        insured_info = None
        try:
            name, address, date_of_birth, license_number = await asyncio.gather(self.__verify_insured_name(),
                                                                                self.__verify_insured_address(),
                                                                                self.__verify_insured_dob(),
                                                                                self.__verify_insured_license_number())
            insured_info = {'name': name, 'address': address, 'date_of_birth': date_of_birth,
                            'license_number': license_number}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
        return insured_info
