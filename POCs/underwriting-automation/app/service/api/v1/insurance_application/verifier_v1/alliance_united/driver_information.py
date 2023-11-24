import asyncio
from datetime import datetime

from dateutil.relativedelta import relativedelta

from app import logger
from app.constant import SRC_ITC, SRC_INSURANCE_APPLICATION, SRC_DRIVING_LICENSE, TRG_ITC, TRG_INS_APP, \
    TRG_CRM_RECEIPT, TRG_MVR, TRG_PUL, TRG_BROKER_PACKAGE, SRC_MVR, TRG_AUL, TRG_NOL, TRG_REGISTRATION, TRG_VR
from app.constant import VerificationTemplate
from app.service.api.v1.insurance_application.verifier_v1.alliance_united.base import AllianceUnitedV1


class DriverInformationVerifier(AllianceUnitedV1):

    def __init__(self, uuid, data):
        super(DriverInformationVerifier, self).__init__(uuid, data)

    async def __verify_driver_relationship(self, driver, insured_driver, relationship_in_application):
        _relationship = None
        relationship_status = None
        try:
            if driver.relationship in VerificationTemplate.Relationship.INSURED:
                _relationship = await self.is_equal(driver.name, insured_driver.name)
            elif driver.relationship in VerificationTemplate.Relationship.PARENT_CHILD:
                if driver.date_of_birth and insured_driver.date_of_birth:
                    difference_in_years = relativedelta(datetime.strptime(driver.date_of_birth, '%Y-%m-%d'),
                                                        datetime.strptime(insured_driver.date_of_birth,
                                                                          '%Y-%m-%d')).years
                    _relationship = True if difference_in_years > 15 else False
            elif driver.relationship in VerificationTemplate.Relationship.SIGNIFICANT_OTHER:
                total = 0
                for item in VerificationTemplate.Relationship.SIGNIFICANT_OTHER:
                    total = total + relationship_in_application.count(item)
                _relationship = True if total == 1 else False
            elif driver.relationship in VerificationTemplate.Relationship.OTHER_ALLOWED:
                _relationship = True
            relationship_status = {'source': SRC_INSURANCE_APPLICATION,
                                   'target': {TRG_INS_APP: _relationship}}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
            relationship_status = None
        return relationship_status

    async def __get_itc_driver_by_name(self, name):
        if self.itc and self.itc.driver_information.drivers:
            for driver in self.itc.driver_information.drivers:
                if await self.is_equal(driver.name, name):
                    return driver
        return None

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

    async def __verify_name(self, app_driver, dl, mvr):
        name = None
        itc_driver = await self.__get_itc_driver_by_name(dl.name)
        try:
            dl_name = dl.name
        except AttributeError:
            return None
        try:
            app_name = app_driver.name
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
            mvr_name = mvr.name
        except AttributeError:
            mvr_name = None
        try:
            itc_name = itc_driver.name
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
            name['target'][TRG_REGISTRATION] = await self.__verify_multiple_owners_name(self.registrations, dl_name)
            name['target'][TRG_VR] = await self.__verify_multiple_owners_name(self.vrs, dl_name)
        return name

    async def __verify_dob(self, app_driver, dl, mvr):
        date_of_birth = None
        try:
            if dl.date_of_birth:
                itc_driver = await self.__get_itc_driver_by_name(dl.name)
                date_of_birth = {'source': SRC_DRIVING_LICENSE, 'target':
                    {TRG_ITC: await self.is_equal(itc_driver.date_of_birth, dl.date_of_birth) if itc_driver else None,
                     TRG_INS_APP: await self.is_equal(app_driver.date_of_birth,
                                                      dl.date_of_birth) if app_driver else None,
                     TRG_MVR: await self.is_equal(mvr.date_of_birth, dl.date_of_birth) if mvr else None}}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
            date_of_birth = None
        return date_of_birth

    async def __verify_license_number(self, app_driver, dl, mvr):
        license_number = None
        try:
            if dl.license_number:
                license_number = {'source': SRC_DRIVING_LICENSE, 'target':
                    {TRG_INS_APP: await self.is_equal(app_driver.license_number,
                                                      dl.license_number) if app_driver else None,
                     TRG_MVR: await self.is_equal(mvr.license_number, dl.license_number) if mvr else None}}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
            license_number = None
        return license_number

    async def __verify_marital_status(self, app_driver, itc_driver):
        marital_status = None
        try:
            if itc_driver.marital_status:
                marital_status = {'source': SRC_INSURANCE_APPLICATION, 'target': {
                    TRG_ITC: await self.is_equal(itc_driver.marital_status, app_driver.marital_status)}}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
            marital_status = None
        return marital_status

    async def __verify_number_of_violation(self, mvr, itc_driver):
        number_of_violation = None
        try:
            if itc_driver.number_of_violations:
                number_of_violation = {'source': SRC_MVR,
                                       'target': {TRG_ITC: await self.is_equal(mvr.number_of_violations,
                                                                               itc_driver.number_of_violations)}}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
            number_of_violation = None
        return number_of_violation

    async def __check_driving_experience(self, x, y):
        diff = abs(x - y) < 12
        return diff

    async def __verify_driving_experience(self, app_driver, itc_driver):
        driving_experience = None
        try:
            if app_driver.driving_experience_in_months and itc_driver.attributes.months_mvr_experience_us:
                driving_experience = {'source': SRC_ITC,
                                      'target': {
                                          SRC_INSURANCE_APPLICATION: True if itc_driver and await
                                          self.__check_driving_experience(app_driver.driving_experience_in_months,
                                                                          itc_driver.attributes.months_mvr_experience_us)
                                          else False}}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
            driving_experience = None
        return driving_experience

    async def __verify_sr_filing(self, app_driver, itc_driver):
        sr_filing = None
        try:
            if app_driver.sr_filing:
                sr_filing = {'source': SRC_ITC, 'target': {
                    TRG_ITC: await self.is_equal(itc_driver.fr_filing, VerificationTemplate.SR_FILING)}}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
            sr_filing = None
        return sr_filing

    async def __verify_status(self, app_driver):
        status = None
        try:
            excluded_drivers = [driver.name for driver in
                                self.itc.driver_information.excluded_drivers] if self.itc.driver_information.excluded_drivers else None
            rated_drivers = [driver.name for driver in
                             self.itc.driver_information.drivers] if self.itc.driver_information.drivers else None
            _status = None
            if app_driver.status == 'Rated' and rated_drivers:
                _status = True if app_driver.name in rated_drivers else False
            elif app_driver.status == 'Excluded' and excluded_drivers:
                _status = True if app_driver.name in excluded_drivers else False
            status = {'source': SRC_ITC, 'target': {TRG_INS_APP: _status}}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
            status = None
        return status

    async def __verify_gender(self, app_driver, dl, itc_driver, mvr):
        gender = None
        try:
            if dl.gender:
                gender = {'source': SRC_DRIVING_LICENSE, 'target':
                    {TRG_INS_APP: await self.is_equal(app_driver.gender,
                                                      dl.gender) if app_driver else None,
                     TRG_ITC: await self.is_equal(itc_driver.gender, dl.gender) if itc_driver else None,
                     TRG_MVR: await self.is_equal(mvr.gender, dl.gender) if mvr.gender else None}}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
            gender = None
        return gender

    async def __verify_driver_info(self):
        drivers = []
        try:
            insured_driver = await self.get_object_by_id(self.application.driver_information.drivers, 1)
            for app_driver in self.application.driver_information.drivers:
                name = dob = lic = marital_status = violation = gender = None
                status = driving_exp = sr_filing = relationship = None
                if app_driver:
                    relationship_in_application = [x.relationship for x in self.application.driver_information.drivers]
                    dl = await self.get_driver_with_lic_no(self.driving_licenses, app_driver.license_number)
                    mvr = await self.get_driver_with_lic_no(self.mvrs, app_driver.license_number)
                    itc_driver = await self.__get_itc_driver_by_name(app_driver.name)
                    if dl:
                        name, lic, dob, gender = await asyncio.gather(self.__verify_name(app_driver, dl, mvr),
                                                                      self.__verify_license_number(app_driver, dl, mvr),
                                                                      self.__verify_dob(app_driver, dl, mvr),
                                                                      self.__verify_gender(app_driver, dl, itc_driver,
                                                                                           mvr))
                    if itc_driver:
                        marital_status, driving_exp, sr_filing, status = await asyncio.gather(
                            self.__verify_marital_status(app_driver, itc_driver),
                            self.__verify_driving_experience(app_driver, itc_driver),
                            self.__verify_sr_filing(app_driver, itc_driver),
                            self.__verify_status(app_driver))
                    if mvr and itc_driver:
                        violation = await self.__verify_number_of_violation(mvr, itc_driver)
                    relationship = await self.__verify_driver_relationship(app_driver, insured_driver,
                                                                           relationship_in_application)

                info = {'id': app_driver.id, 'status': status, 'name': name, 'date_of_birth': dob, 'gender': gender,
                        'marital_status': marital_status, 'driving_experience': driving_exp, 'sr_filing': sr_filing,
                        'license_number': lic, 'number_of_violation': violation, 'relationship': relationship}
                drivers.append(info)

        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
            drivers = None
        return drivers

    async def verify(self):
        driver_information = None
        try:
            drivers = await self.__verify_driver_info()
            driver_information = {'drivers': drivers}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
        return driver_information
