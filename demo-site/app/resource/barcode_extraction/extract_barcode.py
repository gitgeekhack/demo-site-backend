import os
import uuid
import json
import traceback
from aiohttp import web

from app import logger
from app.service.barcode_extraction.extract_barcode import BarcodeExtraction
from app.common.utils import is_image_file, get_file_from_path, get_file_size, get_response_headers
from app.business_rule_exception import InvalidFile, FileLimitExceeded, FilePathNull, MultipleFileUploaded, MissingRequestBody


class BarCodeExtraction:
    async def post(self):
        x_uuid = uuid.uuid1()
        headers = await get_response_headers()
        files = []
        try:
            data_bytes = await self.content.read()
            data = json.loads(data_bytes)
            file_path = data['file_path']
            if file_path == '':
                raise FilePathNull()
            if isinstance(file_path, str):
                if not os.path.exists(file_path):
                    raise FileNotFoundError
                filename = os.path.basename(file_path)
                if not is_image_file(filename):
                    raise InvalidFile(filename)
                file_size = get_file_size(file_path)
                if file_size > 25:
                    raise FileLimitExceeded(file_path)

                logger.info(f'Request ID: [{x_uuid}] FileName: [{filename}]')
                files.append(file_path)
            else:
                raise MultipleFileUploaded()
            extractor = BarcodeExtraction(x_uuid)
            data = extractor.extract(image_data=files)
            if isinstance(data, int):
                raise Exception
            elif isinstance(data, str):
                message = {
                    "message": "barcode is not scannable"
                }
                return web.json_response(message, headers=headers, status=422)
            return web.json_response({'data': data}, headers=headers, status=200)

        except FilePathNull as e:
            response = {"message": f"{e}"}
            return web.json_response(response, headers=headers, status=400)

        except MultipleFileUploaded as e:
            response = {"message": f"{e}"}
            return web.json_response(response, headers=headers, status=400)

        except FileNotFoundError:
            response = {"message": "File Not Found"}
            return web.json_response(response, headers=headers, status=404)

        except FileLimitExceeded as e:
            response = {"message": f"{e}"}
            return web.json_response(response, headers=headers, status=400)

        except InvalidFile:
            response = {"message": "Unsupported Media Type, Only JPG, JPEG, and PNG formats are Supported!"}
            return web.json_response(response, headers=headers, status=415)

        except Exception as e:
            logger.error(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            response = {"message": "Internal Server Error"}
            logger.error(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, headers=headers, status=500)
