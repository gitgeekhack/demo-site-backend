import traceback
import uuid

import aiohttp_jinja2
import jinja2
from aiohttp import web

from app import logger
from app.business_rule_exception import InvalidFileException, FailedToDownloadFileFromURLException
from app.common.utils import is_image_file
from app.service.driving_license.extract import DLDataPointExtractorV1


class Index(web.View):
    @aiohttp_jinja2.template('uploader.html')
    async def get(self):
        return {}

class DLExtract(web.View):
    @aiohttp_jinja2.template('results.html')
    async def post(self):
        x_uuid = uuid.uuid1()
        try:
            data = await self.request.post()
            file = data['file']
            file_name = file.filename
            if not is_image_file(file_name):
                raise InvalidFileException(file_name)
            logger.info(f'Request ID: [{x_uuid}] FileName: [{file_name}]')
            extractor = DLDataPointExtractorV1(x_uuid)
            data = await extractor.extract(file=file)
            return {'response': data}
        except Exception as e:
            logger.error(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            response = {"message": 'Internal Server Error'}
            logger.info(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, status=500)
