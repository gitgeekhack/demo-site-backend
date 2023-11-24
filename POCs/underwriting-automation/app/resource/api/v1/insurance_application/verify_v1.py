import traceback
import uuid

from aiohttp import web

from app import logger
from app.common.utils import is_zip_file
from app.constant import ErrorCode, ErrorMessage, InsuranceCompany
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
            data = await self.request.post()
            file = data['file']
            company_name = data['insurance_company']
            file_name = file.filename
            if file_name:
                await self.__is_allowed(company_name)
                if not is_zip_file(file_name):
                    raise InvalidFileException(file_name)
                print(f'Request ID: [{x_uuid}] FileName: [{file_name}]')
                verifier = DataPointVerifierV1(x_uuid)
                data = await verifier.verify(zip_file=file, company_name=company_name)
                return web.json_response(data=data, status=200)
            return web.json_response({"code": ErrorCode.MISSING_DOCUMENT, "message": ErrorMessage.MISSING_DOCUMENT},
                                     status=400)
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
        except Exception as e:
            print(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            response = {"message": ErrorMessage.SERVER_ERROR}
            print(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, status=500)
