import io
import json
import os

import aiohttp
import aiohttp_jinja2
from aiohttp import web

from app.constant import PDFAnnotationAndExtraction
from app.service.medical_document_insights.extract import DocumentInsightExtractor


class MedDocHomePage(web.View):
    @aiohttp_jinja2.template('medicaldoc-insights-extractor-homepage.html')
    async def get(self):
        return {}


class BytesIOWithFilename(io.BytesIO):
    def __init__(self, content, filename):
        super(BytesIOWithFilename, self).__init__(content)
        self.filename = filename


class MedicalDocExtractorView(web.View):
    async def get(self):
        return web.Response(text="This is the GET response for /med-doc/extract")

    async def post(self):
        data = await self.request.post()

        if 'input_pdf' not in data:
            return web.Response(text="No file uploaded.")

        uploaded_file = data['input_pdf']
        if type(uploaded_file) is str:
            try:
                abs_path = os.path.abspath('app') + uploaded_file
                with open(abs_path, 'rb') as file:
                    file_content = file.read()
                    uploaded_file = BytesIOWithFilename(file_content, filename=abs_path)
            except FileNotFoundError:
                print(f"File not found: {uploaded_file}")
        data = DocumentInsightExtractor(uploaded_file)
        processed_data = data.extract()

        context = {
            'data': processed_data,
        }
        response = aiohttp_jinja2.render_template('medicaldoc-insights-extractor.html', self.request, context)

        return response


class QnAExtractorView(web.View):

    async def get(self):
        return web.Response(text="This is the GET response for /med-doc/extract")

    async def post(self):
        data = await self.request.json()

        if 'input_pdf' not in data and 'input_query' not in data:
            return web.Response(text="No file uploaded.")

        document_name = data['input_pdf']
        input_query = data['input_query']
        data = DocumentInsightExtractor(document_name)
        processed_data = data.extract_qna(input_query)
        response_json = json.dumps(processed_data, ensure_ascii=False)

        return web.Response(body=response_json, content_type='application/json', status=200)
