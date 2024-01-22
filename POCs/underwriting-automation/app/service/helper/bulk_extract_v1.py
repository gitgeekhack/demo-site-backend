import asyncio
from collections import ChainMap

from aiofile import async_open

from app import logger
from app.business_rule_exception import MissingRequiredDocumentException, InvalidPDFStructureTypeException
from app.service.api.v1.driving_license.extract_v1 import DLDataPointExtractorV1
from app.service.api.v1.itc.extract_v1 import ITCDataPointExtractorV1
from app.service.api.v1.pleasure_use_letter.extract_v1 import PULDataPointExtractorV1
from app.service.api.v1.insurance_application.extract_v1 import APPDataPointExtractorV1
from app.service.api.v1.crm_receipt.extract_v1 import CRMDataPointExtractorV1
from app.service.api.v1.mvr.extract_v1 import MVRDataPointExtractorV1
from app.service.api.v1.broker_package.extract_v1 import BrokerPackageDataPointExtractorV1
from app.service.api.v1.artisan_use_letter.extract_v1 import AULDataPointExtractorV1
from app.service.api.v1.eft.extract_v1 import EFTDataPointExtractorV1
from app.service.api.v1.non_owners_letter.extract_v1 import NOLDataPointExtractorV1
from app.service.api.v1.registration.extract_v1 import REGDataPointExtractorV1
from app.service.api.v1.vr.extract_v1 import VRDataPointExtractorV1
from app.service.api.v1.stripe_receipt.extract_v1 import STRPDataPointExtractorV1
from app.service.api.v1.promise_to_provide.extract_v1 import PTPDataPointExtractorV1

import io


class BulkExtractV1:
    def __init__(self, uuid, file_paths, company_name):
        self.file_paths = file_paths
        self.company_name = company_name
        self.uuid = uuid
        self.extractors = [self.extract_dl(), self.extract_itc(), self.extract_crm_receipt(),
                           self.extract_application(), self.extract_pleasure_use_letter(),
                           self.extract_mvr(), self.extract_broker_package(), self.extract_artisan_use_letter(),
                           self.extract_eft(), self.extract_non_owners_letter(), self.extract_stripe_receipt(),
                           self.extract_registration(), self.extract_vr(), self.extract_promise_to_provide()]

    async def extract_application(self):
        application = self.file_paths['application']
        if not application:
            raise MissingRequiredDocumentException('Alliance United Application')
        async with async_open(application, 'rb') as f:
            file_io = await f.read()
        content = io.BytesIO(file_io)
        extractor = APPDataPointExtractorV1(self.uuid, content)
        response = await extractor.extract(self.company_name)
        return {'insurance_application': response['insurance_application']}

    async def extract_crm_receipt(self):
        crm = self.file_paths['crm_receipt']
        if not crm:
            raise MissingRequiredDocumentException('CRM Receipt')
        async with async_open(crm, 'rb') as f:
            file_io = await f.read()
        content = io.BytesIO(file_io)
        extractor = CRMDataPointExtractorV1(self.uuid)
        response = await extractor.extract(content)
        return {'crm_receipt': response['crm_receipt']}

    async def extract_dl(self):
        dl_response = []
        extractor = DLDataPointExtractorV1(self.uuid)
        dl = self.file_paths['driving_license']
        if not dl:
            raise MissingRequiredDocumentException('Driving License')
        async with async_open(dl, 'rb') as f:
            file_io = await f.read()
        content = io.BytesIO(file_io)
        dl_response.append(extractor.extract(content))
        response = await asyncio.gather(*dl_response)
        response = [x['driving_license'] for x in response]
        return {'driving_license': response}

    async def extract_itc(self):
        itc = self.file_paths['itc']
        if not itc:
            raise MissingRequiredDocumentException('ITC')
        async with async_open(itc, 'rb') as f:
            file_io = await f.read()
        content = io.BytesIO(file_io)
        extractor = ITCDataPointExtractorV1(self.uuid, content)
        response = await extractor.extract()
        return {'itc': response['itc']}

    async def extract_pleasure_use_letter(self):
        pleasure_use_letter = self.file_paths['pleasure_use_letter']
        if not pleasure_use_letter:
            return {'pleasure_use_letter': None}
        async with async_open(pleasure_use_letter, 'rb') as f:
            file_io = await f.read()
            content = io.BytesIO(file_io)
        extractor = PULDataPointExtractorV1(self.uuid, content)
        response = await extractor.extract()
        return {'pleasure_use_letter': response['pleasure_use_letter']}

    async def extract_mvr(self):
        mvr_response = []
        mvr = self.file_paths['motor_vehicle_record']
        if not mvr:
            raise MissingRequiredDocumentException('MVR')
        async with async_open(mvr, 'rb') as f:
            file_io = await f.read()
        content = io.BytesIO(file_io)
        extractor = MVRDataPointExtractorV1(self.uuid, content)
        mvr_response.append(extractor.extract())
        response = await asyncio.gather(*mvr_response)
        response = [x['mvr'] for x in response]
        return {'mvr': response}

    async def extract_broker_package(self):
        broker_package = self.file_paths['broker_package']
        if not broker_package:
            raise MissingRequiredDocumentException('Broker Package')
        async with async_open(broker_package, 'rb') as f:
            file_io = await f.read()
        content = io.BytesIO(file_io)
        extractor = BrokerPackageDataPointExtractorV1(self.uuid, content)
        try:
            response = await extractor.extract()
        except InvalidPDFStructureTypeException:
            logger.warning(f'Request ID: [{self.uuid}] Invalid PDF Structure')
            return {'broker_package': None}
        return {'broker_package': response['broker_package']}

    async def extract_artisan_use_letter(self):
        artisan_use_letter = self.file_paths['artisan_use_letter']
        if not artisan_use_letter:
            return {'artisan_use_letter': None}
        async with async_open(artisan_use_letter, 'rb') as f:
            file_io = await f.read()
        content = io.BytesIO(file_io)
        extractor = AULDataPointExtractorV1(self.uuid, content)
        response = await extractor.extract()
        return {'artisan_use_letter': response['artisan_use_letter']}

    async def extract_registration(self):
        registration_response = []
        extractor = REGDataPointExtractorV1(self.uuid)
        registration = self.file_paths['registration']
        if not registration:
            return {'registration': None}
        async with async_open(registration, 'rb') as f:
            file_io = await f.read()
        content = io.BytesIO(file_io)
        registration_response.append(extractor.extract(content))
        response = await asyncio.gather(*registration_response)
        response = [x['registration'] for x in response]
        return {'registration': response}

    async def extract_eft(self):
        eft = self.file_paths['eft']
        if not eft:
            return {'eft': None}
        async with async_open(eft, 'rb') as f:
            file_io = await f.read()
        content = io.BytesIO(file_io)
        extractor = EFTDataPointExtractorV1(self.uuid, content)
        response = await extractor.extract()
        return {'eft': response['eft']}

    async def extract_vr(self):
        vr_response = []
        vr = self.file_paths['vehicle_record']
        if not vr:
            return {'vr': None}
        async with async_open(vr, 'rb') as f:
            file_io = await f.read()
        content = io.BytesIO(file_io)
        extractor = VRDataPointExtractorV1(self.uuid, content)
        vr_response.append(extractor.extract())
        response = await asyncio.gather(*vr_response)
        response = [x['vr'] for x in response]
        return {'vr': response}

    async def extract_non_owners_letter(self):
        non_owners_letter = self.file_paths['non_owners_letter']
        if not non_owners_letter:
            return {'non_owners_letter': None}

        async with async_open(non_owners_letter, 'rb') as f:
            file_io = await f.read()
        content = io.BytesIO(file_io)
        extractor = NOLDataPointExtractorV1(self.uuid, content)
        response = await extractor.extract()
        return {'non_owners_letter': response['non_owners_letter']}

    async def extract_stripe_receipt(self):
        stripe_receipt = self.file_paths['stripe_receipt']
        if not stripe_receipt:
            return {'stripe_receipt': None}
        async with async_open(stripe_receipt, 'rb') as f:
            file_io = await f.read()
        content = io.BytesIO(file_io)
        extractor = STRPDataPointExtractorV1(self.uuid, content)
        response = await extractor.extract()
        return {'stripe_receipt': response['stripe_receipt']}

    async def extract_promise_to_provide(self):
        promise_to_provide = self.file_paths['promise_to_provide']
        if not promise_to_provide:
            return {'promise_to_provide': None}
        async with async_open(promise_to_provide, 'rb') as f:
            file_io = await f.read()
            content = io.BytesIO(file_io)
        extractor = PTPDataPointExtractorV1(self.uuid, content)
        response = await extractor.extract()
        return {'promise_to_provide': response['promise_to_provide']}

    async def extract(self):
        data = await asyncio.gather(*self.extractors)
        return dict(ChainMap(*data))
