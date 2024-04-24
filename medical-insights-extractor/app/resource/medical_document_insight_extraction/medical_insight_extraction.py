import os
import uuid
import json
import glob
import asyncio
import traceback
from aiohttp import web
import boto3
from app.constant import MedicalInsights, BotoClient

from app import logger
from app.constant import MedicalInsights
from app.common.utils import is_pdf_file, get_file_size, get_response_headers, medical_insights_output_path, \
    get_pdf_page_count
from app.service.medical_document_insights.medical_insights import get_medical_insights
from app.service.medical_document_insights.medical_insights_qna import get_query_response
from app.business_rule_exception import (InvalidFile, HandleFileLimitExceeded, FilePathNull, InputQueryNull,
                                         FolderPathNull,
                                         MultipleFileUploaded, MissingRequestBody, InvalidRequestBody,
                                         TotalPageExceeded)


class MedicalInsightsExtractor:
    async def post(self):
        aws_bucket = BotoClient.AWS_BUCKET
        client = boto3.client('s3')
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
                updated_path = project_path[len(MedicalInsights.PREFIX):]
            else:
                raise Exception(project_path)

            response = client.list_objects_v2(Bucket=aws_bucket, Prefix=updated_path)
            if 'Contents' not in response or not len(response['Contents']) > 0:
                raise FileNotFoundError(response)

            documents = []
            for item in response['Contents']:
                if item['Key'].endswith('.pdf'):
                    documents.append(item['Key'])

            download_dir = MedicalInsights.DOWNLOAD_DIR

            if not os.path.exists(download_dir):
                os.makedirs(download_dir)

            for document in documents:
                file_name = document.split('/')[-1]
                s3_response = client.get_object(Bucket=aws_bucket, Key=document)
                s3_object_body = s3_response.get('Body')
                content = s3_object_body.read()
                full_path = os.path.join(download_dir, file_name)

                with open(full_path, 'wb') as file:
                    file.write(content)

            document_list = glob.glob(os.path.join(download_dir, '*'))
            for file_path in document_list:
                if not is_pdf_file(file_path):
                    raise InvalidFile(file_path)

                page_count = 0
                page_count += get_pdf_page_count(file_path)
                if page_count > MedicalInsights.TOTAL_PAGES_THRESHOLD:
                    raise TotalPageExceeded(MedicalInsights.TOTAL_PAGES_THRESHOLD)

            project_response_path = project_path.replace(MedicalInsights.REQUEST_FOLDER_NAME,
                                                         MedicalInsights.RESPONSE_FOLDER_NAME)
            project_response_file_path = os.path.join(project_response_path, 'output.json')

            if project_response_file_path.startswith(MedicalInsights.PREFIX):
                project_response_file_path = project_response_file_path[len(MedicalInsights.PREFIX):]

            updated_project_response_file_path = client.put_object(Bucket=aws_bucket, Key=project_response_file_path,
                                                                   SSECustomerKey=b'\xfbu\xc3\xf83\xe1\xa6\xb8\x06\xa5\x8cdv\xd1\x83,\xd7L\xa8^\xae\xbd\xa9\x17P\x19\xb4\x88(|>\x9c',
                                                                   SSECustomerAlgorithm="AES256")

            if not os.path.exists(updated_project_response_file_path):
                os.makedirs(updated_project_response_file_path)
                with open(updated_project_response_file_path, 'r') as file:
                    output_file = json.loads(file.read())

                if output_file['status_code'] == 200:
                    processed_documents = []
                    for document in output_file['data']:
                        processed_documents.append(os.path.join(project_path, document['document_name']))
                    document_list = list(set(document_list) - set(processed_documents))

            # if os.path.exists(project_response_file_path):
            #     with open(project_response_file_path, 'r') as file:
            #         output_file = json.loads(file.read())
            #
            #     if output_file['status_code'] == 200:
            #         processed_documents = []
            #         for document in output_file['data']:
            #             processed_documents.append(os.path.join(project_path, document['document_name']))
            #         document_list = list(set(document_list) - set(processed_documents))
            if document_list:
                asyncio.create_task(get_medical_insights(project_path, document_list))
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

            if not os.path.exists(project_path):
                raise FileNotFoundError(project_path)

            project_response_path = project_path.replace(MedicalInsights.REQUEST_FOLDER_NAME,
                                                         MedicalInsights.RESPONSE_FOLDER_NAME)
            project_response_file_path = os.path.join(project_response_path, 'output.json')

            if os.path.exists(project_response_file_path):
                with open(project_response_file_path, 'r') as file:
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
