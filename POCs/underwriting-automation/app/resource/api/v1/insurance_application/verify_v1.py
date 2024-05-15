import os.path
import shutil
import traceback
import uuid
import json
from aiohttp import web

from app import logger
from app.common.s3_utils import s3_utils
from app.common.utils import is_image_url, is_pdf_url, get_file_size, get_response_headers
from app.constant import ErrorCode, ErrorMessage, InsuranceCompany, Keys, S3, PROJECT_NAME
from app.resource.authentication import required_authentication
from app.service.api.v1 import DataPointVerifierV1
from app.business_rule_exception import InvalidInsuranceCompanyException, MissingRequiredDocumentException, \
    InvalidFileException, InvalidPDFStructureTypeException, FileSizeLimitExceed, MultipleFileUploaded, \
    InvalidRequestBody


class VerifyV1(web.View):
    async def __is_allowed(self, company_name):
        if not company_name in InsuranceCompany.items():
            raise InvalidInsuranceCompanyException(company_name)

    async def options(self):
        headers = await get_response_headers()
        return web.json_response(headers=headers, status=200)

    @required_authentication
    async def post(self):
        x_uuid = uuid.uuid1()
        headers = await get_response_headers()
        try:
            data_bytes = await self.request.content.read()
            data = json.loads(data_bytes)
            company_name = "alliance-united"
            file_paths = Keys.KEYS_DIC

            local_dir_path = os.path.dirname(data['driving_license'].replace(S3.PREFIX, ''))
            local_dir_path = os.path.join(local_dir_path.replace(S3.AWS_KEY_PATH, S3.LOCAL_PATH), PROJECT_NAME)
            os.makedirs(local_dir_path, exist_ok=True)

            for key in file_paths:
                if key not in data.keys() or not data[key]:
                    if key in Keys.REQUIRED_KEYS:
                        raise MissingRequiredDocumentException(key)
                else:
                    if isinstance(data[key], str):

                        if data[key].startswith(S3.PREFIX):
                            s3_key = data[key].replace(S3.PREFIX, '')
                        else:
                            raise InvalidRequestBody()

                        response = await s3_utils.check_s3_path_exists(bucket=S3.BUCKET_NAME, key=s3_key)
                        if not response:
                            raise FileNotFoundError(s3_key)

                        local_path = os.path.join(local_dir_path, os.path.basename(s3_key))
                        await s3_utils.download_object(S3.BUCKET_NAME, s3_key, local_path, S3.ENCRYPTION_KEY)

                        if key in Keys.IMAGE_KEYS:
                            if not is_image_url(local_path):
                                raise InvalidFileException(local_path)
                        else:
                            if not is_pdf_url(local_path):
                                raise InvalidFileException(local_path)
                        if get_file_size(local_path) > 25:
                            raise FileSizeLimitExceed(local_path)
                        file_paths[key] = local_path
                    else:
                        raise MultipleFileUploaded

            print(f'Request ID: [{x_uuid}]')
            verifier = DataPointVerifierV1(x_uuid)
            res = await verifier.verify(file_paths=file_paths, company_name=company_name)

            shutil.rmtree(local_dir_path)
            return web.json_response(data=res, headers=headers, status=200)

        except MissingRequiredDocumentException as e:
            logger.warning(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            response = {"code": ErrorCode.MISSING_DOCUMENT,
                        "message": ErrorMessage.MISSING_DOCUMENTS_FOR_VERIFICATION}
            print(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, headers=headers, status=400)

        except InvalidInsuranceCompanyException as e:
            logger.warning(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            response = {"code": ErrorCode.INVALID_DOCUMENT,
                        "message": ErrorMessage.INVALID_INSURANCE_COMPANY_APPLICATION}
            print(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, headers=headers, status=400)

        except InvalidFileException as e:
            logger.warning(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            response = {"code": ErrorCode.INVALID_DOCUMENT, "message": ErrorMessage.INVALID_DOCUMENT}
            print(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, headers=headers, status=400)

        except InvalidPDFStructureTypeException as e:
            logger.warning(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            response = {"code": ErrorCode.INVALID_PDF_STRUCTURE, "message": ErrorMessage.INVALID_PDF_STRUCTURE}
            print(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, headers=headers, status=400)

        except FileSizeLimitExceed as e:
            logger.warning(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            response = {"code": ErrorCode.SIZE_LIMIT_EXCEEDED, "message": ErrorMessage.SIZE_LIMIT_EXCEEDED}
            print(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, headers=headers, status=400)

        except MultipleFileUploaded as e:
            logger.warning(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            response = {"code": ErrorCode.MULTIPLE_FILE_UPLOADED, "message": ErrorMessage.MULTIPLE_FILE_UPLOADED}
            print(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, headers=headers, status=400)

        except FileNotFoundError as e:
            print(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            response = {"message": ErrorMessage.FILE_NOT_FOUND}
            print(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, headers=headers, status=404)

        except Exception as e:
            print(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            response = {"message": ErrorMessage.SERVER_ERROR}
            print(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, headers=headers, status=500)
