import traceback
import uuid

import aiohttp_jinja2
from aiohttp import web

from app import logger
from app.business_rule_exception import InvalidFile
from app.common.utils import is_image_file, get_file_from_path
from app.service.driving_license.extract import DLDataPointExtractorV1


class DLExtractor():
    async def post(self):
        x_uuid = uuid.uuid1()
        filedata = []
        try:
            data = await self.post()
            files = data.getall('file')

            if '' in files:
                raise KeyError
            for file in files:
                if isinstance(file, str):
                    file = get_file_from_path(file)
                filename = file.filename
                if not is_image_file(filename):
                    raise InvalidFile(filename)
                print(f'Request ID: [{x_uuid}] FileName: [{filename}]')
                filedata.append(file)
            extractor = DLDataPointExtractorV1(x_uuid)
            data = await extractor.extract(image_data=filedata)
            if isinstance(data, int):
                raise Exception
            else:
                return web.json_response({'data': data}, status=200)
        except Exception as e:
            print(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            if isinstance(e, KeyError):
                response = {"message": "Parameter 'file' is required in the request."}
                return web.json_response(response, status=400)
            if isinstance(e, InvalidFile):
                response = {"message": 'Unsupported Media Type'}
                return web.json_response(response, status=415)
            response = {"message": 'Internal Server Error'}
            print(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, status=500)
