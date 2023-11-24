import os
import aiohttp_jinja2
from aiohttp import web
import uuid
import traceback
from app import logger
from app.business_rule_exception import InvalidFile
from app.constant import PDFAnnotationAndExtraction, AllowedFileType, USER_DATA_PATH
from app.common.utils import is_allowed_file, save_file, get_file_from_path
from app.service.pdf_annotation_and_extraction.PDFExtractor import DataPointExtraction
from app.service.helper.annotation_file import extract_annotation_files, get_annotation_filenames


class HomePage(web.View):
    @aiohttp_jinja2.template('pdf-annotation-extraction-homepage.html')
    async def get(self):
        return {'cvat_ip': PDFAnnotationAndExtraction.CVAT_IP}


class DataExtraction(web.View):
    @aiohttp_jinja2.template('pdf_extract_data.html')
    async def get(self):
        await extract_annotation_files()
        annotation_filenames = await get_annotation_filenames()
        return {'annotated': annotation_filenames}

    @aiohttp_jinja2.template('pdf_extract_data.html')
    async def post(self):
        annotation_filenames = await get_annotation_filenames()
        x_uuid = uuid.uuid1()
        try:
            data = await self.request.post()
            pdf_file = data.get('input_pdf')
            annotation_file = data.get('document_selector')  # document type selected by user
            if isinstance(pdf_file, str):
                pdf_file = get_file_from_path(pdf_file)
            else:
                # saving pdf file
                await save_file(file_object=pdf_file, folder_path=USER_DATA_PATH)

            filename = pdf_file.filename
            if not is_allowed_file(filename, allowed_extensions=AllowedFileType.PDF):
                raise InvalidFile(filename)

            print(f'Request ID: [{x_uuid}] FileName: [{filename}]')

            extractor = DataPointExtraction(x_uuid)
            results, table_labels = await extractor.extract(os.path.join(PDFAnnotationAndExtraction.ANNOTATION_FOLDER,
                                                                         annotation_file + '.xml'),
                                                            os.path.join(PDFAnnotationAndExtraction.UPLOAD_FOLDER,
                                                                         filename))

            return {'results': results, 'annotated': annotation_filenames, 'table_labels': table_labels}
        except Exception as e:
            print(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
            response = {"message": 'Internal Server Error'}
            print(f'Request ID: [{x_uuid}] Response: {response}')
            return web.json_response(response, status=500)
