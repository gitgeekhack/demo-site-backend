import os
import uuid
import json
import glob
import asyncio
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

            project_response_path = project_path.replace(MedicalInsights.REQUEST_FOLDER_NAME, MedicalInsights.RESPONSE_FOLDER_NAME)
            project_response_file_path = os.path.join(project_response_path, 'output.json')

            if os.path.exists(project_response_file_path):
                pass
            else:
                asyncio.create_task(get_medical_insights(project_path, document_list))
            return web.json_response(headers=headers, status=202)

        except TotalPageExceeded as e:
            response = {"message": f"{e}"}
            return web.json_response(response, headers=headers, status=400)

        except FolderPathNull as e:
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
            response = {"message": "Project Not Found"}
            return web.json_response(response, headers=headers, status=404)

        except Exception as e:
            logger.error(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            response = {"message": "Internal Server Error"}
            logger.error(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, headers=headers, status=500)

    async def get(self):
        x_uuid = uuid.uuid1()
        headers = await get_response_headers()
        try:
            if 'project_path' in self.query.keys():
                project_path = self.query.get("project_path")
            else:
                raise MissingRequestBody()

            if not project_path:
                raise FolderPathNull()

            if isinstance(project_path, int) or isinstance(project_path, dict) or isinstance(project_path, list):
                raise InvalidRequestBody()

            if not os.path.exists(project_path):
                raise FileNotFoundError(project_path)

            project_response_path = project_path.replace(MedicalInsights.REQUEST_FOLDER_NAME, MedicalInsights.RESPONSE_FOLDER_NAME)
            project_response_file_path = os.path.join(project_response_path, 'output.json')

            if os.path.exists(project_response_file_path):
                with open(project_response_file_path, 'r') as file:
                    res = json.loads(file.read())
                    if res["status_code"] == 200:
                        return web.json_response(data=res['data'], headers=headers, status=200)
                    else:
                        raise Exception
            else:
                return web.json_response(headers=headers, status=102)

        except FolderPathNull as e:
            response = {"message": f"{e}"}
            return web.json_response(response, headers=headers, status=400)

        except InvalidRequestBody as e:
            response = {"message": f"{e}"}
            return web.json_response(response, headers=headers, status=400)

        except MissingRequestBody as e:
            response = {"message": f"{e}"}
            return web.json_response(response, headers=headers, status=400)

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

            project_path = data['project_path']
            input_query = data['input_query']

            if not project_path:
                raise FilePathNull()

            if isinstance(project_path, int) or isinstance(project_path, dict) or isinstance(project_path, list):
                raise InvalidRequestBody()

            if not input_query:
                raise InputQueryNull()

            if isinstance(input_query, int) or isinstance(input_query, dict) or isinstance(input_query, list):
                raise InvalidRequestBody()

            if isinstance(project_path, str):
                if not os.path.exists(project_path):
                    raise FileNotFoundError

            project_response_path = project_path.replace(MedicalInsights.REQUEST_FOLDER_NAME, MedicalInsights.RESPONSE_FOLDER_NAME)
            project_response_file_path = os.path.join(project_response_path, 'embeddings.pkl')

            if os.path.exists(project_response_file_path):
                result = await get_query_response(input_query, project_response_path)
                del result['source_documents']
                result = json.dumps(result).encode('utf-8')
                return web.Response(body=result, headers=headers, content_type='application/json', status=200)
            else:
                return web.json_response(headers=headers, status=102)

        except FilePathNull as e:
            response = {"message": f"{e}"}
            return web.json_response(response, headers=headers, status=400)

        except InputQueryNull as e:
            response = {"message": f"{e}"}
            return web.json_response(response, headers=headers, status=400)

        except InvalidRequestBody as e:
            response = {"message": f"{e}"}
            return web.json_response(response, headers=headers, status=400)

        except MissingRequestBody as e:
            response = {"message": f"{e}"}
            return web.json_response(response, headers=headers, status=400)

        except FileNotFoundError:
            response = {"message": "Project Not Found"}
            return web.json_response(response, headers=headers, status=404)

        except Exception as e:
            logger.error(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            response = {"message": "Internal Server Error"}
            logger.error(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, headers=headers, status=500)
