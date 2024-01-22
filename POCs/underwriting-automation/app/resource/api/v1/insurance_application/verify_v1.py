import os.path
import traceback
import uuid
import json
from aiohttp import web

from app import logger
from app.common.utils import is_image_url, is_pdf_url
from app.constant import ErrorCode, ErrorMessage, InsuranceCompany, Keys
from app.resource.authentication import required_authentication
from app.service.api.v1 import DataPointVerifierV1
from app.business_rule_exception import InvalidInsuranceCompanyException, MissingRequiredDocumentException, \
    InvalidFileException, InvalidPDFStructureTypeException


class VerifyV1(web.View):
    async def __is_allowed(self, company_name):
        if not company_name in InsuranceCompany.items():
            raise InvalidInsuranceCompanyException(company_name)

    @required_authentication
    async def post(self):
        x_uuid = uuid.uuid1()
        try:
            data_bytes = await self.request.content.read()
            data = json.loads(data_bytes)
            company_name = "alliance-united"

            for key in data.keys():
                if not data[key]:
                    if key in Keys.REQUIRED_KEYS:
                        raise MissingRequiredDocumentException(key)
                else:
                    if not os.path.exists(data[key]):
                        raise FileNotFoundError
                    if key in Keys.IMAGE_KEYS:
                        if not is_image_url(data[key]):
                            raise InvalidFileException(data[key])
                    else:
                        if not is_pdf_url(data[key]):
                            raise InvalidFileException(data[key])

            print(f'Request ID: [{x_uuid}]')
            verifier = DataPointVerifierV1(x_uuid)
            res = await verifier.verify(file_paths=data, company_name=company_name)
            return web.json_response(data=res, status=200)

        except MissingRequiredDocumentException as e:
            logger.warning(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            response = {"code": ErrorCode.MISSING_DOCUMENT,
                        "message": ErrorMessage.MISSING_DOCUMENTS_FOR_VERIFICATION}
            print(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, status=400)
        except InvalidInsuranceCompanyException as e:
            logger.warning(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            response = {"code": ErrorCode.INVALID_DOCUMENT,
                        "message": ErrorMessage.INVALID_INSURANCE_COMPANY_APPLICATION}
            print(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, status=400)
        except InvalidFileException as e:
            logger.warning(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            response = {"code": ErrorCode.INVALID_DOCUMENT, "message": ErrorMessage.INVALID_DOCUMENT}
            print(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, status=400)
        except InvalidPDFStructureTypeException as e:
            logger.warning(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            response = {"code": ErrorCode.INVALID_PDF_STRUCTURE, "message": ErrorMessage.INVALID_PDF_STRUCTURE}
            print(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, status=400)
        except FileNotFoundError as e:
            print(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            response = {"message": ErrorMessage.FILE_NOT_FOUND}
            print(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, status=404)
        except Exception as e:
            print(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            response = {"message": ErrorMessage.SERVER_ERROR}
            print(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, status=500)
