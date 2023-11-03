import traceback
import uuid

import aiohttp_jinja2
from aiohttp import web
from app.business_rule_exception import InvalidFile
from app.common.utils import is_image_file
from app.service.barcode_extraction.extract_barcode import BarcodeExtraction
class BarCodeExtraction(web.View):
    @aiohttp_jinja2.template('barcode-detection.html')
    async def get(self):
        return {'results':[{'barcode_detection': ['000000000000'], 'filename': 'barcode.jpg', 'image_count': 1}, {'barcode_detection': ['This is a Test'], 'filename': 'qrcode.png', 'image_count': 2}]}

    @aiohttp_jinja2.template('barcode-detection.html')
    async def post(self):
        x_uuid = uuid.uuid1()
        filedata = []

        try:
            data = await self.request.post()
            files = data.getall('file')
            for file in files:
                filename = file.filename
                if not is_image_file(filename):
                    raise InvalidFile(filename)
                print(f'Request ID: [{x_uuid}] FileName: [{filename}]')
                filedata.append(file)
            extractor = BarcodeExtraction(x_uuid)
            data = extractor.extract(image_data=filedata)
            return {'results': data}
        except Exception as e:
            print(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            response = {"message": 'Internal Server Error'}
            print(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, status=500)


