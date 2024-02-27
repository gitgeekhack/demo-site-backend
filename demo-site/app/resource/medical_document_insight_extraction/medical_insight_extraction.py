import os
import uuid
import json
import traceback
from aiohttp import web

from app import logger
from app.common.utils import is_pdf_file, get_file_size, get_response_headers, medical_insights_output_path
from app.service.medical_document_insights.medical_insights import get_medical_insights
from app.service.medical_document_insights.medical_insights_qna import get_query_response
from app.business_rule_exception import (InvalidFile, FileLimitExceeded, HandleFileLimitExceeded, FilePathNull, InputQueryNull,
                                         MultipleFileUploaded, MissingRequestBody, InvalidRequestBody)


class MedicalInsightsExtractor:
    async def post(self):
        x_uuid = uuid.uuid1()
        headers = await get_response_headers()
        try:
            data_bytes = await self.content.read()

            if not data_bytes:
                raise MissingRequestBody()

            data = json.loads(data_bytes)

            file_path = data['file_path']

            if not file_path:
                raise FilePathNull()

            if isinstance(file_path, int) or isinstance(file_path, dict):
                raise InvalidRequestBody()

            if isinstance(file_path, list) or isinstance(file_path, dict):
                raise MultipleFileUploaded()

            if isinstance(file_path, str):
                if not os.path.exists(file_path):
                    raise FileNotFoundError

                if not is_pdf_file(file_path):
                    raise InvalidFile(file_path)

                file_size = get_file_size(file_path)
                if file_size > 1024:
                    raise HandleFileLimitExceeded(file_path)

            document_name = os.path.basename(file_path).split(".")[0]
            document_response_path = os.path.join(medical_insights_output_path, f'{document_name}.json')

            if os.path.exists(document_response_path):
                with open(document_response_path, 'r') as file:
                    document_response = json.loads(file.read())
            else:
                extracted_information = await get_medical_insights(file_path)
                document_response = {'document': extracted_information}
                with open(document_response_path, 'w') as file:
                    file.write(json.dumps(document_response))

            return web.json_response(document_response, headers=headers, status=200)

        except FilePathNull as e:
            response = {"message": f"{e}"}
            return web.json_response(response, headers=headers, status=400)

        except MultipleFileUploaded as e:
            response = {"message": f"{e}"}
            return web.json_response(response, headers=headers, status=400)

        except FileLimitExceeded as e:
            response = {"message": f"{e}"}
            return web.json_response(response, headers=headers, status=400)

        except InvalidRequestBody as e:
            response = {"message": f"{e}"}
            return web.json_response(response,headers=headers, status=400)

        except MissingRequestBody as e:
            response = {"message": f"{e}"}
            return web.json_response(response, headers=headers, status=400)

        except InvalidFile:
            response = {"message": "Unsupported Media Type, Only PDF formats are Supported!"}
            return web.json_response(response, headers=headers, status=415)

        except FileNotFoundError:
            response = {"message": "File Not Found"}
            return web.json_response(response, headers=headers, status=404)

        except Exception as e:
            logger.error(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            response = {"message": "Internal Server Error"}
            logger.error(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, headers=headers, status=500)


class QnAExtractor:
    async def post(self):
        x_uuid = uuid.uuid1()
        headers = await get_response_headers()
        try:
            data_bytes = await self.content.read()

            if not data_bytes:
                raise MissingRequestBody()

            data = json.loads(data_bytes)

            file_path = data['file_path']
            input_query = data['input_query']

            if not file_path:
                raise FilePathNull()

            if isinstance(file_path, int) or isinstance(file_path, dict):
                raise InvalidRequestBody()

            if isinstance(file_path, list) or isinstance(file_path, dict):
                raise MultipleFileUploaded()

            if not input_query:
                raise InputQueryNull()

            if isinstance(input_query, int) or isinstance(input_query, dict) or isinstance(input_query, list):
                raise InvalidRequestBody()

            if isinstance(file_path, str):
                if not os.path.exists(file_path):
                    raise FileNotFoundError

                if not is_pdf_file(file_path):
                    raise InvalidFile(file_path)

                file_size = get_file_size(file_path)
                if file_size > 1024:
                    raise HandleFileLimitExceeded(file_path)

            result = await get_query_response(input_query, file_path)
            result = json.dumps(result).encode('utf-8')
            return web.Response(body=result, headers=headers, content_type='application/json', status=200)

        except FilePathNull as e:
            response = {"message": f"{e}"}
            return web.json_response(response, headers=headers, status=400)

        except InputQueryNull as e:
            response = {"message": f"{e}"}
            return web.json_response(response, headers=headers, status=400)

        except MultipleFileUploaded as e:
            response = {"message": f"{e}"}
            return web.json_response(response, headers=headers, status=400)

        except FileLimitExceeded as e:
            response = {"message": f"{e}"}
            return web.json_response(response, headers=headers, status=400)

        except InvalidRequestBody as e:
            response = {"message": f"{e}"}
            return web.json_response(response, headers=headers, status=400)

        except MissingRequestBody as e:
            response = {"message": f"{e}"}
            return web.json_response(response, headers=headers, status=400)

        except InvalidFile:
            response = {"message": "Unsupported Media Type, Only PDF formats are Supported!"}
            return web.json_response(response, headers=headers, status=415)

        except FileNotFoundError:
            response = {"message": "File Not Found"}
            return web.json_response(response, headers=headers, status=404)

        except Exception as e:
            logger.error(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            response = {"message": "Internal Server Error"}
            logger.error(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, headers=headers, status=500)
