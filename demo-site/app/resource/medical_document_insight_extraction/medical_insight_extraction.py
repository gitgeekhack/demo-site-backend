import os
import json
from aiohttp import web

from app.common.utils import is_pdf_file, get_file_size
from app.service.medical_document_insights.medical_insights import get_medical_insights
from app.service.medical_document_insights.medical_insights_qna import get_query_response
from app.business_rule_exception import InvalidFile, FileLimitExceeded, FilePathNull, InputQueryNull, MultipleFileUploaded


class MedicalInsightsExtractor:
    async def post(self):
        try:
            data_bytes = await self.content.read()
            data = json.loads(data_bytes)

            file_path = data['file_path']

            if file_path == '':
                raise FilePathNull()

            if isinstance(file_path, str):
                if not os.path.exists(file_path):
                    raise FileNotFoundError

                if not is_pdf_file(file_path):
                    raise InvalidFile(file_path)

                file_size = get_file_size(file_path)
                if file_size > 25:
                    raise FileLimitExceeded(file_path)

            else:
                raise MultipleFileUploaded()

            extracted_information = await get_medical_insights(file_path)
            return web.json_response({'document': extracted_information}, status=200)

        except FilePathNull as e:
            response = {"message": f"{e}"}
            return web.json_response(response, status=400)

        except MultipleFileUploaded as e:
            response = {"message": f"{e}"}
            return web.json_response(response, status=400)

        except FileLimitExceeded as e:
            response = {"message": f"{e}"}
            return web.json_response(response, status=400)

        except InvalidFile:
            response = {"message": "Unsupported Media Type, Only PDF formats are Supported!"}
            return web.json_response(response, status=415)

        except FileNotFoundError:
            response = {"message": "File Not Found"}
            return web.json_response(response, status=404)

        except Exception as e:
            response = {"message": f"Internal Server Error with error {e}"}
            return web.json_response(response, status=500)


class QnAExtractor:
    async def post(self):
        try:
            data_bytes = await self.content.read()
            data = json.loads(data_bytes)

            file_path = data['file_path']
            input_query = data['input_query']

            if file_path == '':
                raise FilePathNull()

            if input_query == '':
                raise InputQueryNull()

            if isinstance(file_path, str):
                if not os.path.exists(file_path):
                    raise FileNotFoundError

                if not is_pdf_file(file_path):
                    raise InvalidFile(file_path)

                file_size = get_file_size(file_path)
                if file_size > 25:
                    raise FileLimitExceeded(file_path)

            else:
                raise MultipleFileUploaded()

            result = await get_query_response(input_query, file_path)
            result = json.dumps(result).encode('utf-8')
            return web.Response(body=result, content_type='application/json', status=200)

        except FilePathNull as e:
            response = {"message": f"{e}"}
            return web.json_response(response, status=400)

        except InputQueryNull as e:
            response = {"message": f"{e}"}
            return web.json_response(response, status=400)

        except MultipleFileUploaded as e:
            response = {"message": f"{e}"}
            return web.json_response(response, status=400)

        except FileLimitExceeded as e:
            response = {"message": f"{e}"}
            return web.json_response(response, status=400)

        except InvalidFile:
            response = {"message": "Unsupported Media Type, Only PDF formats are Supported!"}
            return web.json_response(response, status=415)

        except FileNotFoundError:
            response = {"message": "File Not Found"}
            return web.json_response(response, status=404)

        except Exception as e:
            response = {"message": f"Internal Server Error with error {e}"}
            return web.json_response(response, status=500)
