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
        return {'results':[{'image_path': 'damage_detection/Detected/out_images.jpeg', 'detection': [['Headlights(Broken/Missing)', 0], ['Front Windshield', 0], ['Rear Windshield', 0], ['Hood', 0], ['Front Bumper', 0], ['Rear Bumper', 0], ['Fender', 87], ['Door', 90], ['Trunk', 0], ['Taillights', 0], ['Window', 68], ['Missing Wheel', 0], ['Flat Tyre', 0], ['Missing Mirror', 0], ['Interior Damage', 0]], 'image_count': 1}]}

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
