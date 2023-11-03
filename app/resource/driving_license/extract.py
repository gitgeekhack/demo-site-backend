import traceback
import uuid

import aiohttp_jinja2
from aiohttp import web

from app import logger
from app.business_rule_exception import InvalidFile
from app.common.utils import is_image_file
from app.service.driving_license.extract import DLDataPointExtractorV1


class DLExtractor(web.View):
    @aiohttp_jinja2.template('driving-license-ocr.html')
    async def get(self):
        return {'sample': {'filename': '10302019_drivers_174607-1560x1006_jpg.rf.fbea054a628a5144443fb6ecf00c520b.jpg'}}

    @aiohttp_jinja2.template('driving-license-ocr.html')
    async def post(self):
        x_uuid = uuid.uuid1()
        filedata = []
        try:
            data = await self.request.post()
            files = data.getall('file')

            for file in files:
                filename = file.filename
                if not is_image_file(filename):
                    raise InvalidFile(filename)
                print(f'Request ID: [{x_uuid}] FileName: [{filename}]')
                filedata.append(file)
            extractor = DLDataPointExtractorV1(x_uuid)
            data = await extractor.extract(image_data=filedata)
            return {'results': data}
        except Exception as e:
            print(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            response = {"message": 'Internal Server Error'}
            print(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, status=500)
