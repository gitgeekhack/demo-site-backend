import os.path
import traceback
import uuid

import aiohttp_jinja2
from aiohttp import web

from app import logger
from app.business_rule_exception import InvalidFile
from app.common.utils import is_image_file, get_file_from_path
from app.service.car_damage_detection.damage_detect import DamageDetector


class DamageExtractor(web.View):
    @aiohttp_jinja2.template('damage-detection.html')
    async def get(self):
        return {}

    @aiohttp_jinja2.template('damage-detection.html')
    async def post(self):
        x_uuid = uuid.uuid1()
        filedata = []
        try:
            data = await self.request.post()
            files = data.getall('file')
            for file in files:
                if isinstance(file, str):
                    file = get_file_from_path(file)
                filename = file.filename
                if not is_image_file(filename):
                    raise InvalidFile(filename)
                print(f'Request ID: [{x_uuid}] FileName: [{filename}]')
                filedata.append(file)
            detector = DamageDetector(x_uuid)
            results = await detector.detect(image_data=filedata)
            return {'results': results}
        except Exception as e:
            print(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            response = {"message": 'Internal Server Error'}
            print(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, status=500)
