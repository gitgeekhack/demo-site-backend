import traceback
import uuid
import json

import aiohttp_jinja2
from aiohttp import web
from app.business_rule_exception import InvalidFile
from app.common.utils import is_image_file, get_file_from_path
from app.service.barcode_extraction.extract_barcode import BarcodeExtraction


class BarCodeExtraction:
    async def post(self):
        x_uuid = uuid.uuid1()
        filedata = []

        try:
            data_bytes = await self.content.read()
            data = json.loads(data_bytes)
            files = data['file_paths']
            if '' in files:
                raise KeyError
            for file in files:
                if isinstance(file, str):
                    file = get_file_from_path(file)
                    if isinstance(file, FileNotFoundError):
                        raise FileNotFoundError
                filename = file.filename
                if not is_image_file(filename):
                    raise InvalidFile(filename)
                print(f'Request ID: [{x_uuid}] FileName: [{filename}]')
                filedata.append(file)
            extractor = BarcodeExtraction(x_uuid)
            data = extractor.extract(image_data=filedata)
            if isinstance(data, int):
                raise Exception
            elif isinstance(data, str):
                message = {
                    "message": "barcode is not scannable"
                }
                return web.json_response(message, status=422)
            return web.json_response({'data': data}, status=200)
        except Exception as e:
            print(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            if isinstance(e, KeyError):
                response = {"message": "Parameter 'file_paths' is required in the request."}
                return web.json_response(response, status=400)
            if isinstance(e, InvalidFile):
                response = {"message": 'Unsupported Media Type'}
                return web.json_response(response, status=415)
            if isinstance(e, FileNotFoundError):
                response = {"message": "File Not Found"}
                return web.json_response(response, status=404)
            response = {"message": 'Internal Server Error'}
            print(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, status=500)
