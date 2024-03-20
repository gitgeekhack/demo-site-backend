import os
import uuid
import json
import glob
import traceback
from aiohttp import web

from app.constant import MedicalInsights
from app import logger
from app.common.utils import is_pdf_file, get_file_size, get_response_headers, medical_insights_output_path, get_pdf_page_count
from app.service.medical_document_insights.medical_insights import get_medical_insights
from app.service.medical_document_insights.medical_insights_qna import get_query_response
from app.business_rule_exception import (InvalidFile, HandleFileLimitExceeded, FilePathNull, InputQueryNull, FolderPathNull,
                                         MultipleFileUploaded, MissingRequestBody, InvalidRequestBody, TotalPageExceeded)


class MedicalInsightsExtractor:
    async def post(self):
        x_uuid = uuid.uuid1()
        headers = await get_response_headers()
        try:
            data_bytes = await self.content.read()

            if not data_bytes:
                raise MissingRequestBody()

            data = json.loads(data_bytes)

            if 'project_path' in data.keys():
                project_path = data['project_path']
            else:
                raise MissingRequestBody()

            if not project_path:
                raise FolderPathNull()

            if isinstance(project_path, int) or isinstance(project_path, dict) or isinstance(project_path, list):
                raise InvalidRequestBody()

            if not os.path.exists(project_path):
                raise FileNotFoundError(project_path)

            page_count = 0
            document_list = glob.glob(os.path.join(project_path, '*'))
            for file_path in document_list:
                if not is_pdf_file(file_path):
                    raise InvalidFile(file_path)

                page_count += get_pdf_page_count(file_path)
                if page_count > MedicalInsights.TOTAL_PAGES_THRESHOLD:
                    raise TotalPageExceeded(MedicalInsights.TOTAL_PAGES_THRESHOLD)

            project_id = os.path.basename(project_path).split("/")[-1]
            project_response_path = os.path.join(medical_insights_output_path, f'{project_id}.json')

            if os.path.exists(project_response_path):
                with open(project_response_path, 'r') as file:
                    document_response = json.loads(file.read())
            else:
                extracted_information = await get_medical_insights(project_path, document_list)
                document_response = {'data': extracted_information}
                with open(project_response_path, 'w') as file:
                    file.write(json.dumps(document_response))

            return web.json_response(document_response, headers=headers, status=200)

        except TotalPageExceeded as e:
            response = {"message": f"{e}"}
            return web.json_response(response, headers=headers, status=400)

        except FolderPathNull as e:
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
            response = {"message": "Project Not Found"}
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

            result = await get_query_response(input_query, file_path)
            del result['source_documents']
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
