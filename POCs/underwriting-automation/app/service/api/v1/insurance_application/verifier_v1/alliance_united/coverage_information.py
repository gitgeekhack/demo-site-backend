from app import logger
from app.constant import SRC_ITC, TRG_INS_APP
from app.service.api.v1.insurance_application.verifier_v1.alliance_united.base import AllianceUnitedV1


class CoverageInformationVerifier(AllianceUnitedV1):

    def __init__(self, uuid, data):
        super(CoverageInformationVerifier, self).__init__(uuid, data)

    async def __get_comprehensive_deductible(self, itc_vehicle, app_vehicle):
        comp_deduct_itc = None
        try:
            if itc_vehicle:
                comp_deduct_itc = {'source': SRC_ITC, 'target': {
                    TRG_INS_APP: await self.is_equal(itc_vehicle.comprehensive_deductible,
                                                     app_vehicle.comprehensive_deductible)}}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
            comp_deduct_itc = None
        return comp_deduct_itc

    async def __get_collision_deductible(self, itc_vehicle, app_vehicle):
        coll_deduct_itc = None
        try:
            if itc_vehicle:
                coll_deduct_itc = {'source': SRC_ITC, 'target': {
                    TRG_INS_APP: await self.is_equal(itc_vehicle.collision_deductible,
                                                     app_vehicle.collision_deductible)}}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
            coll_deduct_itc = None
        return coll_deduct_itc

    async def __get_coverage_info_for_vehicles(self):
        vehicles = None
        try:
            if self.application.coverage_information.vehicles:
                vehicles = []
                for app_vehicle in self.application.coverage_information.vehicles:
                    vehicle_id = app_vehicle.id
                    itc_vehicle = await self.get_object_by_id(self.itc.vehicle_information.vehicles, app_vehicle.id)
                    comprehensive_deductible = await self.__get_comprehensive_deductible(itc_vehicle, app_vehicle)
                    collision_deductible = await self.__get_collision_deductible(itc_vehicle, app_vehicle)
                    vehicle_dict = {'id': vehicle_id, 'comprehensive_deductible': comprehensive_deductible,
                                    'collision_deductible': collision_deductible}
                    vehicles.append(vehicle_dict)
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
            vehicles = None
        return vehicles

    async def __get_insured_bi(self):
        bi = None
        try:
            if self.itc.driver_information.bi_amount_each_person:
                bi_person = await self.is_equal(self.itc.driver_information.bi_amount_each_person,
                                                self.application.coverage_information.bi_amount_each_person)
                bi_accident = await self.is_equal(self.itc.driver_information.bi_amount_each_person,
                                                  self.application.coverage_information.bi_amount_each_person)
                bi = {'source': SRC_ITC, 'target': {TRG_INS_APP: bi_person & bi_accident}}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
            bi = None
        return bi

    async def __get_uninsured_bi(self):
        uni_bi = None
        try:
            if self.itc.driver_information.uninsured_bi_amount_each_person:
                uni_bi_person = await self.is_equal(self.itc.driver_information.uninsured_bi_amount_each_person,
                                                    self.application.coverage_information.uninsured_bi_amount_each_person)
                uni_bi_accident = await self.is_equal(self.itc.driver_information.uninsured_bi_amount_each_accident,
                                                      self.application.coverage_information.uninsured_bi_amount_each_accident)
                uni_bi = {'source': SRC_ITC, 'target': {TRG_INS_APP: uni_bi_person & uni_bi_accident}}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
            uni_bi = None
        return uni_bi

    async def __get_insured_pd(self):
        pd = None
        try:
            if self.itc.driver_information.pd_amount_each_accident:
                pd = {'source': SRC_ITC,
                      'target': {TRG_INS_APP: await self.is_equal(
                          self.itc.driver_information.pd_amount_each_accident,
                          self.application.coverage_information.pd_amount_each_accident)}}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
            pd = None
        return pd

    async def __get_uninusred_pd(self):
        uni_pd = None
        try:
            if self.itc.driver_information.uninsured_pd_amount_each_accident:
                uni_pd = {'source': SRC_ITC, 'target': {TRG_INS_APP: await self.is_equal(
                    self.itc.driver_information.uninsured_pd_amount_each_accident,
                    self.application.coverage_information.uninsured_pd_amount_each_accident)}}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
            uni_pd = None
        return uni_pd

    async def __verify_coverage_info(self):
        coverage_info = None
        try:
            vehicles = await self.__get_coverage_info_for_vehicles()
            coverage_info = {'bodily_injury': await self.__get_insured_bi(),
                             'property_damage': await self.__get_insured_pd(),
                             'uninsured_bodily_injury': await self.__get_uninsured_bi(),
                             'uninsured_property_damage': await self.__get_uninusred_pd(), 'vehicles': vehicles}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
        return coverage_info

    async def verify(self):
        coverage = None
        try:
            if self.itc:
                coverage = await self.__verify_coverage_info()
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
        return coverage
