import aiohttp_jinja2
from aiohttp import web

from app.constant import PDFAnnotationAndExtraction
from app.service.medical_document_insights.extract import DocumentInsightExtractor


class MedDocHomePage(web.View):
    @aiohttp_jinja2.template('medicaldoc-insights-extractor-homepage.html')
    async def get(self):
        return {}


class MedicalDocExtractorView(web.View):
    async def get(self):
        return web.Response(text="This is the GET response for /med-doc/extract")

    async def post(self):
        data = await self.request.post()

        if 'input_pdf' not in data:
            return web.Response(text="No file uploaded.")

        uploaded_file = data['input_pdf']

        # Process the uploaded file here (e.g., extract insights)
        data = DocumentInsightExtractor(uploaded_file)
        processed_data = data.extract()

        context = {
            'data': processed_data,
        }
        response = aiohttp_jinja2.render_template('medicaldoc-insights-extractor.html', self.request, context)

        return response
