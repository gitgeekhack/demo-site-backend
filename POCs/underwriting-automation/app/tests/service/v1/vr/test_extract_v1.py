import io

from app.constant import VRDocumentTemplate
from app.service.api.v1.vr import extract_v1

uuid = '89c5de1c-4d25-11ec-8623-d1e221452fcd'


async def test_vehicle_info_valid():
    file_name = 'app/data/temp/test_data/VEHICLE REPORT 37.pdf'
    f = open(file_name, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.VRDataPointExtractorV1(uuid=uuid, file=file)
    x = await obj._VRDataPointExtractorV1__extract_vehicle_info()
    assert x == {"vin": "WBXPC93438WJ16684", "model": None, "make": "BMW", "year": 2008}


async def test_vehicle_info_invalid():
    file_name = 'app/data/temp/test_data/VEHICLE REPORT 37.pdf'
    f = open(file_name, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.VRDataPointExtractorV1(uuid=uuid, file=file)
    obj.indexof.pop(VRDocumentTemplate.VIN)
    obj.indexof.pop(VRDocumentTemplate.MAKE)
    obj.indexof.pop(VRDocumentTemplate.MODEL)
    obj.indexof.pop(VRDocumentTemplate.PLATE)
    obj.indexof.pop(VRDocumentTemplate.STYLE)
    x = await obj._VRDataPointExtractorV1__extract_vehicle_info()
    assert not x


async def test_owner_name_valid():
    file_name = 'app/data/temp/test_data/VEHICLE REPORT 35.pdf'
    f = open(file_name, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.VRDataPointExtractorV1(uuid=uuid, file=file)
    x = await obj._VRDataPointExtractorV1__extract_owners_name()
    assert x == ["FICA LUKE D", "FICA JOAN M"]

async def test_owner_name_valid_or_in_name():
    file_name = 'app/data/temp/test_data/VEHICLE REPORT 13.pdf'
    f = open(file_name, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.VRDataPointExtractorV1(uuid=uuid, file=file)
    x = await obj._VRDataPointExtractorV1__extract_owners_name()
    assert x == ["FLORES RAYMUNDO"]


async def test_owner_name_invalid():
    file_name = 'app/data/temp/test_data/VEHICLE REPORT 35.pdf'
    f = open(file_name, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.VRDataPointExtractorV1(uuid=uuid, file=file)
    obj.indexof.pop(VRDocumentTemplate.REG_OWNER)
    obj.indexof.pop(VRDocumentTemplate.LEGAL_OWNER)
    x = await obj._VRDataPointExtractorV1__extract_owners_name()
    assert not x
async def test_owner_name_valid_lsr_lse_in_name():
    file_name = 'app/data/temp/test_data/VEHICLE REPORT 18.pdf'
    f = open(file_name, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.VRDataPointExtractorV1(uuid=uuid, file=file)
    x = await obj._VRDataPointExtractorV1__extract_owners_name()
    assert x == ['SEPULVEDA OSCAR']