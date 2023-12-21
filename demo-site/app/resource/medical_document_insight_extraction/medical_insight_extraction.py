import os
import json
import uuid
import traceback
from aiohttp import web

from app.common.utils import is_pdf_file
from app.business_rule_exception import InvalidFile
from app.service.medical_document_insights.medical_insights import get_medical_insights
from app.service.medical_document_insights.medical_insights_qna import get_query_response


class MedicalInsightsExtractor:
    async def post(self):
        x_uuid = uuid.uuid1()
        try:
            data_bytes = await self.content.read()
            data = json.loads(data_bytes)

            file_path = data['file_path']

            if file_path == '':
                raise KeyError

            if isinstance(file_path, str):
                if not os.path.exists(file_path):
                    raise FileNotFoundError
            else:
                raise KeyError

            if not is_pdf_file(file_path):
                raise InvalidFile(file_path)

            extracted_information = await get_medical_insights(file_path)
            return web.json_response({'document': extracted_information}, status=200)

        except Exception as e:
            print(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())

            if isinstance(e, KeyError):
                response = {"message": "Either multiple PDF files have been uploaded or the file has not been uploaded at all."}
                return web.json_response(response, status=400)

            if isinstance(e, FileNotFoundError):
                response = {"message": "File Not Found"}
                return web.json_response(response, status=404)

            if isinstance(e, InvalidFile):
                response = {"message": "Unsupported Media Type, Only PDF formats are Supported!"}
                return web.json_response(response, status=415)


class QnAExtractor:
    async def post(self):
        x_uuid = uuid.uuid1()
        try:
            data_bytes = await self.content.read()
            data = json.loads(data_bytes)

            file_path = data['file_path']
            input_query = data['input_query']

            if file_path == '':
                raise KeyError

            if input_query == '':
                raise KeyError

            if isinstance(file_path, str):
                if not os.path.exists(file_path):
                    raise FileNotFoundError
            else:
                raise KeyError

            if not is_pdf_file(file_path):
                raise InvalidFile(file_path)

            result = await get_query_response(input_query, file_path)
            result = json.dumps(result).encode('utf-8')
            return web.Response(body=result, content_type='application/json', status=200)

        except Exception as e:
            print(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())

            if isinstance(e, KeyError):
                response = {"message": "Either multiple PDF files have been uploaded, the file has not been uploaded at all, or an empty input query is sent."}
                return web.json_response(response, status=400)

            if isinstance(e, FileNotFoundError):
                response = {"message": "File Not Found"}
                return web.json_response(response, status=404)

            if isinstance(e, InvalidFile):
                response = {"message": "Unsupported Media Type, Only PDF formats are Supported!"}
                return web.json_response(response, status=415)
