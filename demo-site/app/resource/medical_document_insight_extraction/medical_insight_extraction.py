import json
import uuid
import traceback
from aiohttp import web

from app.business_rule_exception import InvalidFile
from app.service.medical_document_insights.medical_insights import get_medical_insights


class MedicalInsightsExtractor:
    async def post(self):
        x_uuid = uuid.uuid1()
        try:
            data_bytes = await self.content.read()
            data = json.loads(data_bytes)

            uploaded_file = data['file_path']
            extracted_information = await get_medical_insights(uploaded_file)
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

