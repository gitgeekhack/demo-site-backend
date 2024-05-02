import uuid
import json
import shutil
import os.path
import traceback
from aiohttp import web

from app import logger
from app.common.s3_utils import s3_utils
from app.constant import CertificateOfTitle
from app.service.certificate_of_title.extract import COTDataPointExtractorV1
from app.common.utils import is_image_file, get_file_from_path, get_file_size, get_response_headers
from app.business_rule_exception import (InvalidFile, FileLimitExceeded, FilePathNull, MultipleFileUploaded,
                                         MissingRequestBody, InvalidRequestBody)


class COTExtractor:
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

            if file_path.startswith(CertificateOfTitle.S3.PREFIX):
                s3_key = file_path.replace(CertificateOfTitle.S3.PREFIX, '')
            else:
                raise InvalidRequestBody()

            s3_dir_name = os.path.dirname(s3_key)
            local_path = os.path.join(
                s3_dir_name.replace(CertificateOfTitle.S3.AWS_KEY_PATH, CertificateOfTitle.S3.LOCAL_PATH),
                CertificateOfTitle.PROJECT_NAME)
            os.makedirs(local_path, exist_ok=True)

            if isinstance(file_path, str):
                response = await s3_utils.check_s3_path_exists(CertificateOfTitle.S3.BUCKET_NAME, s3_key)
                if not response:
                    raise FileNotFoundError

                filename = os.path.basename(file_path)
                local_file_name = os.path.join(local_path, filename)
                if not is_image_file(filename):
                    raise InvalidFile(filename)

                await s3_utils.download_object(CertificateOfTitle.S3.BUCKET_NAME, s3_key,
                                               local_file_name, CertificateOfTitle.S3.ENCRYPTION_KEY)

                file_size = get_file_size(local_file_name)

                if file_size > 25:
                    raise FileLimitExceeded(file_path)

                logger.info(f'Request ID: [{x_uuid}] FileName: [{filename}]')
                files.append(local_file_name)
            else:
                raise MultipleFileUploaded()
            extractor = COTDataPointExtractorV1(x_uuid)
            data = await extractor.extract(image_data=files)

            shutil.rmtree(local_path)

            if isinstance(data, int):
                raise Exception
            else:
                return web.json_response({'data': data}, headers=headers, status=200)

        except FilePathNull as e:
            response = {"message": f"{e}"}
            return web.json_response(response, headers=headers, status=400)

        except MultipleFileUploaded as e:
            response = {"message": f"{e}"}
            return web.json_response(response, headers=headers, status=400)

        except InvalidRequestBody as e:
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
