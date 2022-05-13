import traceback
import uuid

import aiohttp_jinja2
from aiohttp import web

from app import logger
from app.business_rule_exception import InvalidFile
from app.common.utils import is_image_file
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
                filename = file.filename
                if not is_image_file(filename):
                    raise InvalidFile(filename)
                logger.info(f'Request ID: [{x_uuid}] FileName: [{filename}]')
                filedata.append(file)
            detector = DamageDetector(x_uuid)
            data = await detector.detect(image_data=filedata)
            return {'results': data}
        except Exception as e:
            logger.error(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            response = {"message": 'Internal Server Error'}
            logger.info(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, status=500)
