import traceback
import uuid

from aiohttp import web

from app import logger
from app.business_rule_exception import InvalidFileException, FailedToDownloadFileFromURLException, \
    InvalidInsuranceCompanyException
from app.common.utils import is_pdf_url
from app.constant import ErrorCode, ErrorMessage, InsuranceCompany
from app.resource.authentication import required_authentication
from app.service.api.v1 import APPDataPointExtractorV1
from app.service.helper.file_downloader import get_file_stream


class APPExtractV1(web.View):

    async def __is_allowed(self, company_name):
        if not company_name in InsuranceCompany.items():
            raise InvalidInsuranceCompanyException(company_name)

    @required_authentication
    async def post(self):
        x_uuid = uuid.uuid1()
        try:
            if self.request.body_exists:
                payload = await self.request.json()
                x_uuid = payload.get('uuid', x_uuid)
                print(f'Request ID: [{x_uuid}] Request Payload: {payload}')
                document_url = payload.get('document_url', None)
                company_name = payload.get('insurance_company', None)
                if document_url:
                    await self.__is_allowed(company_name)
                    if not is_pdf_url(url=document_url):
                        raise InvalidFileException(document_url)
                    file = await get_file_stream(x_uuid, document_url)
                    extractor = APPDataPointExtractorV1(x_uuid, file)
                    data = await extractor.extract(company_name)
                    response = {
                        "data": data
                    }

                    return web.json_response(response)

            return web.json_response({"code": ErrorCode.MISSING_DOCUMENT, "message": ErrorMessage.MISSING_DOCUMENT},
                                     status=400)
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
        except FailedToDownloadFileFromURLException as e:
            logger.warning(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            response = {"code": ErrorCode.INVALID_URL, "message": ErrorMessage.INVALID_URL}
            print(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, status=400)
        except Exception as e:
            print(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            response = {"message": ErrorMessage.SERVER_ERROR}
            print(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, status=500)
