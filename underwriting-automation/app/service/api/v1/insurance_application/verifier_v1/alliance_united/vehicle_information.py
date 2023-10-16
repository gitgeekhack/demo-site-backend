import csv
import traceback

from app import logger, app
from app.constant import SRC_INSURANCE_APPLICATION, TRG_ITC, TRG_PUL, SRC_REGISTRATION, \
    TRG_INS_APP, TRG_AUL, SRC_VR, TRG_REGISTRATION
from app.service.api.v1.insurance_application.verifier_v1.alliance_united.base import AllianceUnitedV1
from app.service.helper.serializer_helper import deserialize


def load_mapping_from_csv(file_path):
    dictionary = {}
    with open(file_path) as f:
        dictionary = dict(filter(None, csv.reader(f)))
    return dictionary


make_mapping = load_mapping_from_csv(app.config.ABREVS_MAPPING_FILE_PATH)


class VehicleInformationVerifier(AllianceUnitedV1):

    def __init__(self, uuid, data):
        super(VehicleInformationVerifier, self).__init__(uuid, data)

    async def __verify_make(self, source, target):
        make = await self.is_equal(source.make, target.make[:4])
        if not make and source.make in make_mapping:
            make = await self.is_subset(make_mapping[source.make], target.make)
        return make

    async def __verify_model(self, source, target):
        application_vehicle_model = source.model
        try:
            trim = target.trim
        except AttributeError:
            trim = None
        if trim:
            application_vehicle_model = ' '.join([application_vehicle_model, trim])
        model = await self.is_subset(application_vehicle_model, target.model)
        return model

    async def __is_equal_vehicle(self, source, target):
        make = model = vin = year = None
        if target:
            make = await self.__verify_make(source, target)
            model = await self.__verify_model(source, target)
            vin = await self.is_equal(source.vin, target.vin)
            year = await self.is_equal(source.year, target.year)
        return {'make': make, 'model': model, 'year': year, 'vin': vin}

    async def find_proof_of_vehicle_by_vin(self, app_vehicle):
        vrs = self.vrs
        registrations = self.registrations
        matched_vehicle = source = None
        if vrs:
            for vr in vrs:
                if vr and 'vehicle' in vr.__dict__.keys() and vr.vehicle.vin == app_vehicle.vin:
                    source = SRC_VR
                    matched_vehicle = vr
                    return source, matched_vehicle

        if registrations:
            for registration in registrations:
                if registration and 'vehicle' in registration.__dict__.keys() and registration.vehicle.vin == app_vehicle.vin:
                    source = SRC_REGISTRATION
                    matched_vehicle = registration
                    return source, matched_vehicle

        return source, matched_vehicle

    async def __find_vehicle(self, source_vehicle, vehicles):
        _vehicle = None
        if source_vehicle:
            for i_vehicle in vehicles:
                if i_vehicle.vin:
                    if await self.is_equal(i_vehicle.vin, source_vehicle.vin):
                        _vehicle = i_vehicle
                        break
                elif source_vehicle.make == i_vehicle.make and source_vehicle.model == i_vehicle.model \
                        and source_vehicle.year == i_vehicle.year:
                    _vehicle = i_vehicle

        return _vehicle

    async def __verify_vehicle_info(self):
        vehicles = []
        _pul_vehicles = await self.__get_pul_vehicles()
        _artisan_vehicles = await self.__get_artisan_vehicles()
        for app_vehicle in self.application.vehicle_information.vehicles:
            vehicle_id = app_vehicle.id
            VEHICLE_SRC, source_vehicle = await self.find_proof_of_vehicle_by_vin(app_vehicle)
            if not source_vehicle:
                vehicle = {'id': vehicle_id,
                           'make': None,
                           'model': None,
                           'vin': None,
                           'year': None,
                           'is_valid': None}
            else:
                pul_vehicle = await self.__find_vehicle(source_vehicle.vehicle, _pul_vehicles)
                if pul_vehicle:
                    _pul_vehicles.remove(pul_vehicle)
                artisan_vehicle = await self.__find_vehicle(source_vehicle.vehicle, _artisan_vehicles)
                if artisan_vehicle:
                    _artisan_vehicles.remove(artisan_vehicle)
                vehicle = await self.__verify_vehicle(VEHICLE_SRC, artisan_vehicle, pul_vehicle, app_vehicle,
                                                      source_vehicle, vehicle_id)
            vehicles.append(vehicle)
        return vehicles

    async def __verify_vehicle(self, source, artisan_vehicle, pul_vehicle, app_vehicle, source_vehicle,
                               vehicle_id):

        vehicle = {'id': vehicle_id,
                   'make': {'source': source, 'target': {}},
                   'model': {'source': source, 'target': {}},
                   'vin': {'source': source, 'target': {}},
                   'year': {'source': source, 'target': {}}}
        validity = await self.get_validity(source, source_vehicle)
        vehicle |= validity
        try:
            itc_vehicle = await self.get_object_by_id(self.itc.vehicle_information.vehicles, vehicle_id)
        except AttributeError:
            itc_vehicle = None
        itc = await self.__is_equal_vehicle(source_vehicle.vehicle, itc_vehicle)
        pul = await self.__is_equal_vehicle(source_vehicle.vehicle, pul_vehicle)
        artisan = await self.__is_equal_vehicle(source_vehicle.vehicle, artisan_vehicle)
        application = await self.__is_equal_vehicle(source_vehicle.vehicle, app_vehicle)
        vehicle['make']['target'] = {TRG_ITC: itc['make'],
                                     TRG_PUL: pul['make'],
                                     TRG_AUL: artisan['make'],
                                     TRG_INS_APP: application['make']}
        vehicle['model']['target'] = {TRG_ITC: itc['model'],
                                      TRG_PUL: pul['model'],
                                      TRG_AUL: artisan['model'],
                                      TRG_INS_APP: application['model']}
        vehicle['year']['target'] = {TRG_ITC: itc['year'],
                                     TRG_PUL: pul['year'],
                                     TRG_AUL: artisan['year'],
                                     TRG_INS_APP: application['year']}
        vehicle['vin']['target'] = {TRG_ITC: itc['vin'],
                                    TRG_PUL: pul['vin'],
                                    TRG_AUL: artisan['vin'],
                                    TRG_INS_APP: application['vin']}
        return vehicle

    async def __get_artisan_vehicles(self):
        try:
            _artisan_vehicles = self.artisan_use_letter.vehicles.copy()
        except AttributeError:
            _artisan_vehicles = []
        return _artisan_vehicles

    async def __get_pul_vehicles(self):
        try:
            _pul_vehicles = self.pleasure_use_letter.vehicles.copy()
        except AttributeError:
            _pul_vehicles = []
        return _pul_vehicles

    async def get_validity(self, source, vehicle):
        if source == SRC_REGISTRATION:
            validity = {'is_valid': {'source': SRC_REGISTRATION, 'target': {
                TRG_REGISTRATION: vehicle.is_valid
            }}}
        else:
            validity = {'is_valid': None}
        return validity

    async def verify(self):
        vehicle_dict = None
        try:
            vehicles = None
            if self.application:
                vehicles = await self.__verify_vehicle_info()
            vehicle_dict = {'vehicles': vehicles}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] %s -> %s', e, traceback.format_exc())

        return vehicle_dict
