import os
import uuid
import json
import glob
import boto3
import asyncio
import traceback
from aiohttp import web

from app import logger
from app.constant import MedicalInsights
from app.common.utils import (is_pdf_file, get_file_size, get_response_headers, medical_insights_output_path,
                              get_pdf_page_count)
from app.common.s3_utils import s3_utils
from app.service.medical_document_insights.medical_insights import get_medical_insights
from app.service.medical_document_insights.medical_insights_qna import get_query_response
from app.business_rule_exception import (InvalidFile, HandleFileLimitExceeded, FilePathNull, InputQueryNull,
                                         FolderPathNull,
                                         MultipleFileUploaded, MissingRequestBody, InvalidRequestBody,
                                         TotalPageExceeded)

AWS_BUCKET = MedicalInsights.AWS_BUCKET
encrypted_key = b'\xfbu\xc3\xf83\xe1\xa6\xb8\x06\xa5\x8cdv\xd1\x83,\xd7L\xa8^\xae\xbd\xa9\x17P\x19\xb4\x88(|>\x9c'


class MedicalInsightsExtractor:

    async def post(self):
        logger.info("Post request received.")
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

            if project_path.startswith(MedicalInsights.PREFIX):
                key = project_path.replace(MedicalInsights.PREFIX, '')
            else:
                raise InvalidRequestBody()

            response = await s3_utils.check_s3_path_exists(aws_bucket=AWS_BUCKET, key=key)

            if not response:
                raise FileNotFoundError(project_path)

            download_path = key.replace('user-data', 'static')
            if not os.path.exists(download_path):
                os.makedirs(download_path, exist_ok=False)

            page_count = 0
            for item in response['Contents']:

                if item['Key'].endswith('.pdf'):
                    document_name = os.path.basename(item['Key'])

                    x = os.path.join(download_path, document_name)
                    await s3_utils.download_object(AWS_BUCKET, item['Key'], x)
                    page_count += get_pdf_page_count(x)

                    if page_count > MedicalInsights.TOTAL_PAGES_THRESHOLD:
                        raise TotalPageExceeded(MedicalInsights.TOTAL_PAGES_THRESHOLD)
                else:
                    raise InvalidFile(item['Key'])

            document_list = glob.glob(os.path.join(download_path, '*'))

            project_response_path = key.replace(MedicalInsights.REQUEST_FOLDER_NAME,
                                                MedicalInsights.RESPONSE_FOLDER_NAME)
            project_response_file_path = os.path.join(project_response_path, 'output.json')

            s3_response = await s3_utils.check_s3_path_exists(aws_bucket=AWS_BUCKET, key=project_response_file_path)

            if s3_response:
                local_file_path = project_response_file_path.replace(f'{MedicalInsights.PREFIX}/user-data', 'static')
                await s3_utils.download_object(AWS_BUCKET, project_response_file_path, local_file_path)

                with open(local_file_path, 'r') as file:
                    output_file = json.loads(file.read())

                if output_file['status_code'] == 200:
                    processed_documents = []
                    for document in output_file['data']:
                        processed_documents.append(os.path.join(download_path, document['document_name']))
                    document_list = list(set(document_list) - set(processed_documents))

            if document_list:
                asyncio.create_task(get_medical_insights(download_path, document_list))

            return web.json_response(headers=headers, status=202)

        except TotalPageExceeded as e:
            response = {"message": f"{e}"}
            logger.error(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            logger.error(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, headers=headers, status=400)

        except FolderPathNull as e:
            response = {"message": f"{e}"}
            logger.error(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            logger.error(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, headers=headers, status=400)

        except InvalidRequestBody as e:
            response = {"message": f"{e}"}
            logger.error(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            logger.error(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, headers=headers, status=400)

        except MissingRequestBody as e:
            response = {"message": f"{e}"}
            logger.error(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            logger.error(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, headers=headers, status=400)

        except InvalidFile as e:
            response = {"message": "Unsupported Media Type, Only PDF formats are Supported!"}
            logger.error(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            logger.error(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, headers=headers, status=415)

        except FileNotFoundError as e:
            response = {"message": "Project Not Found"}
            logger.error(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            logger.error(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, headers=headers, status=404)

        except Exception as e:
            logger.error(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            response = {"message": "Internal Server Error"}
            logger.error(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, headers=headers, status=500)

    async def get(self):
        logger.info("GET request received.")
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

            if project_path.startswith(MedicalInsights.PREFIX):
                key = project_path.replace(MedicalInsights.PREFIX, '')
            else:
                raise InvalidRequestBody()

            response = await s3_utils.check_s3_path_exists(aws_bucket=AWS_BUCKET, key=key)

            if not response:
                raise FileNotFoundError(project_path)

            project_response_path = key.replace(MedicalInsights.REQUEST_FOLDER_NAME,
                                                MedicalInsights.RESPONSE_FOLDER_NAME)
            project_response_file_path = os.path.join(project_response_path, 'output.json')

            s3_response = await s3_utils.check_s3_path_exists(aws_bucket=AWS_BUCKET, key=project_response_file_path)

            download_path = project_response_file_path.replace('user-data', 'static')
            if not os.path.exists(download_path):
                os.makedirs(download_path, exist_ok=False)

            for item in s3_response['Contents']:

                if item['Key'].endswith('.json'):
                    document_name = os.path.basename(item['Key'])

                    x = os.path.join(download_path, document_name)
                    await s3_utils.download_object(AWS_BUCKET, item['Key'], x)

                else:
                    raise InvalidFile(item['key'])

            if s3_response:
                local_file_path = project_response_file_path.replace(f'{MedicalInsights.PREFIX}/user-data', 'static')
                await s3_utils.download_object(AWS_BUCKET, project_response_file_path, local_file_path)

                with open(local_file_path, 'r') as file:
                    res = json.loads(file.read())

                    if res["status_code"] == 200:
                        logger.info(f"[Medical-Insights][GET] Loaded output from {project_response_file_path}")
                        return web.json_response(data=res['data'], headers=headers, status=200)
                    else:
                        raise Exception
            else:
                logger.info("[Medical-Insights][GET] Output is still under process, responding with status code 425")
                return web.json_response(headers=headers, status=425)

        except FolderPathNull as e:
            response = {"message": f"{e}"}
            logger.error(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            logger.error(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, headers=headers, status=400)

        except InvalidRequestBody as e:
            response = {"message": f"{e}"}
            logger.error(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            logger.error(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, headers=headers, status=400)

        except MissingRequestBody as e:
            response = {"message": f"{e}"}
            logger.error(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            logger.error(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, headers=headers, status=400)

        except FileNotFoundError as e:
            response = {"message": "Project Not Found"}
            logger.error(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            logger.error(f'Request ID: [{x_uuid}] Response: {response}')
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
            if 'project_path' not in data.keys() or 'input_query' not in data.keys():
                raise MissingRequestBody()
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
            result = await get_query_response(input_query, project_path)
            del result['source_documents']
            result = json.dumps(result).encode('utf-8')
            return web.Response(body=result, headers=headers, content_type='application/json', status=200)

        except FilePathNull as e:
            response = {"message": f"{e}"}
            logger.error(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            logger.error(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, headers=headers, status=400)

        except InputQueryNull as e:
            response = {"message": f"{e}"}
            logger.error(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            logger.error(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, headers=headers, status=400)

        except InvalidRequestBody as e:
            response = {"message": f"{e}"}
            logger.error(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            logger.error(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, headers=headers, status=400)

        except MissingRequestBody as e:
            response = {"message": f"{e}"}
            logger.error(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            logger.error(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, headers=headers, status=400)

        except FileNotFoundError as e:
            response = {"message": "Project Not Found"}
            logger.error(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            logger.error(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, headers=headers, status=404)

        except Exception as e:
            logger.error(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            response = {"message": "Internal Server Error"}
            logger.error(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, headers=headers, status=500)
