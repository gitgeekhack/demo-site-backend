import json
import uuid
import traceback
from aiohttp import web

from app import logger
from app.service.car_damage_detection.damage_detect import DamageDetector
from app.common.utils import is_image_file, get_file_from_path, get_file_size, get_response_headers
from app.business_rule_exception import (InvalidFile, FileLimitExceeded, FilePathNull, FileUploadLimitReached,
                                         MissingRequestBody, InvalidRequestBody)


class DamageExtractor:
    async def post(self):
        x_uuid = uuid.uuid1()
        headers = await get_response_headers()
        filedata = []
        try:
            data_bytes = await self.content.read()

            if not data_bytes:
                raise MissingRequestBody()

            data = json.loads(data_bytes)
            file_paths = data['file_paths']
            if not file_paths:
                raise FilePathNull()

            if isinstance(file_paths, list) and len(file_paths) >= 10:
                raise FileUploadLimitReached(10)

            if isinstance(file_paths, str) or isinstance(file_paths, int):
                raise InvalidRequestBody()

            for file in file_paths:
                if isinstance(file, str):
                    file_path = get_file_from_path(file)

                    if isinstance(file_path, FileNotFoundError):
                        raise FileNotFoundError

                    filename = file_path.filename
                    if not is_image_file(filename):
                        raise InvalidFile(filename)

                    file_size = get_file_size(file)
                    if file_size > 25:
                        raise FileLimitExceeded(file_path)

                    print(f'Request ID: [{x_uuid}] FileName: [{filename}]')
                    filedata.append(file_path)

            detector = DamageDetector(x_uuid)
            results = await detector.detect(image_data=filedata)

            return web.json_response({'data': results}, headers=headers, status=200)

        except FilePathNull as e:
            response = {"message": f"{e}"}
            return web.json_response(response, headers=headers, status=400)

        except MissingRequestBody as e:
            response = {"message": f"{e}"}
            return web.json_response(response, headers=headers, status=400)

        except InvalidRequestBody as e:
            response = {"message": f"{e}"}
            return web.json_response(response, headers=headers, status=400)

        except FileUploadLimitReached as e:
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
            response = {"message": f"Internal Server Error with error {e}"}
            return web.json_response(response, headers=headers, status=500)
