import traceback
import uuid

import aiohttp_jinja2
from aiohttp import web

from app import logger
from app.business_rule_exception import InvalidFile
from app.common.utils import is_image_file, get_file_from_path
from app.service.certificate_of_title.extract import COTDataPointExtractorV1


class COTExtractor(web.View):
    @aiohttp_jinja2.template('certificate-of-title-ocr.html')
    async def get(self):
        return {}

    @aiohttp_jinja2.template('certificate-of-title-ocr.html')
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

            extractor = COTDataPointExtractorV1(x_uuid)
            data = await extractor.extract(image_data=filedata)
            return {'results': data}
        except Exception as e:
            print(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            response = {"message": 'Internal Server Error'}
            print(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, status=500)
