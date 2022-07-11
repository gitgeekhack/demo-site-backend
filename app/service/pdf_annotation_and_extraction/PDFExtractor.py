import asyncio
import shutil
import fitz
import ocrmypdf
from app.common.utils import make_dir
from app import logger
import os
from app.service.helper.xml_parser import find_rectangle_boxes
from app.service.helper.dynamic_data_extractor import DynamicDataExtractor
from app.constant import PDFAnnotationAndExtraction


class DataPointExtraction:
    def __init__(self, uuid):
        self.data = {}
        self.uuid = uuid

    async def convert_vectored_to_electronic(self, filepath):
        """
            converts vectored pdf to electronic pdf
            Parameters:
                filepath <str>: path of a vector pdf file
        """
        await make_dir(PDFAnnotationAndExtraction.CONVERTED_PDF_FOLDER)
        try:
            ocrmypdf.ocr(input_file=filepath,
                         output_file=os.path.join(PDFAnnotationAndExtraction.CONVERTED_PDF_FOLDER,
                                                  f'{filepath.split("/")[-1]}'),
                         force_ocr=True)
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')

    async def extract_data(self, doc, rect_boxes):
        """
            extracts data from pdf using annotation bounding boxes
            Parameters:
                doc <fitz Document>: pdf file opened by fitz
                rect_boxes <dict>: dictionary of annotation bounding boxes
            Returns:
                single_file_data <dict>: dictionary of extracted data from pdf
        """
        single_file_data = {}
        try:
            for page_no, datapoints in rect_boxes.items():
                for label, bounding_box in datapoints.items():
                    single_file_data[label] = doc[page_no].get_textbox(bounding_box)
        except IndexError as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')

        return single_file_data

    async def draw_annotation_and_convert_to_image(self, doc, rect_boxes):
        """
            draws annotation on pdf and converts pdf to page wise images
            Parameters:
                doc <fitz Document>: pdf file opened by fitz
                rect_boxes <dict>: dictionary of annotation bounding boxes
        """
        try:
            total_pages = doc.page_count
            for key in rect_boxes.keys():
                for rect in rect_boxes[key].values():
                    if rect is not None:
                        doc[key].add_rect_annot(fitz.Rect(rect))

            try:
                shutil.rmtree(PDFAnnotationAndExtraction.PDF_IMAGES_FOLDER)
            except OSError as e:
                logger.warning(f'Request ID: [{self.uuid}]  -> {e}')

            await make_dir(PDFAnnotationAndExtraction.PDF_IMAGES_FOLDER)
            for page_no in range(total_pages):
                pix = doc[page_no].get_pixmap()
                pix.save(os.path.join(PDFAnnotationAndExtraction.PDF_IMAGES_FOLDER, f'image{page_no}.jpg'))
        except IndexError as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')

    async def change_label(self, result):
        try:
            if result['extracted_data'].keys():
                new_labels = []
                for label in result['extracted_data'].keys():
                    new_label = label.replace('_', ' ')
                    new_label = new_label.title()
                    new_labels.append([label, new_label])
                for label in new_labels:
                    result['extracted_data'][label[1]] = result['extracted_data'].pop(label[0])
        except KeyError as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')

    async def process_dynamic_data_result(self, dynamic_data, static_rect_boxes, filename):
        for page_no, val in dynamic_data.items():
            for label, data in val.items():
                if page_no not in static_rect_boxes.keys():
                    static_rect_boxes[page_no] = {label: data['bbox']}
                else:
                    static_rect_boxes[page_no].update({label: data['bbox']})
                self.data[filename].update({label: data['data']})

    async def change_output_label_names(self, results):
        try:
            change_labels_coroutines = [self.change_label(result) for result in results]

            await asyncio.gather(*change_labels_coroutines)
        except KeyError as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')

        return results

    async def response_generator(self, page_no, rect_boxes, results, image_count):
        try:
            if page_no in rect_boxes.keys():
                extracted_data = {}
                for label in rect_boxes[page_no].keys():
                    extracted_data[label] = list(self.data.values())[0][label]
                image_path = os.path.join(PDFAnnotationAndExtraction.PDF_IMAGES_PATH, f'image{page_no}.jpg')
                results.append(
                    {'image_path': image_path, 'extracted_data': extracted_data, 'image_count': image_count})
                image_count += 1
            else:
                image_path = os.path.join(PDFAnnotationAndExtraction.PDF_IMAGES_PATH, f'image{page_no}.jpg')
                results.append({'image_path': image_path, 'extracted_data': {}, 'image_count': image_count})
                image_count += 1
        except KeyError as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')

    async def generate_output_response(self, rect_boxes):
        results = []
        total_images = len(os.listdir(PDFAnnotationAndExtraction.PDF_IMAGES_FOLDER))

        try:
            output_response_coroutines = [self.response_generator(page, rect_boxes, results, 1 + page)
                                          for page in range(total_images)]

            await asyncio.gather(*output_response_coroutines)

        except KeyError as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')

        response = await self.change_output_label_names(results)

        return response

    async def extract(self, annotation_file, file):
        results = []
        static_rect_boxes, dynamic_blocks = await find_rectangle_boxes(self.uuid, annotation_file, file)

        doc = fitz.open(file)

        self.data[os.path.basename(file)] = await self.extract_data(doc, static_rect_boxes)

        # if data is not extracted then do ocr on pdf (convert vectored to electronic)
        values = list(self.data.values())[0]
        if list(values.values()).count('') > 0:
            await self.convert_vectored_to_electronic(file)
            doc = fitz.open(os.path.join(PDFAnnotationAndExtraction.STATIC_FOLDER,
                                         f'converted_files/{os.path.basename(file)}'))
            self.data[os.path.basename(file)] = await self.extract_data(doc, static_rect_boxes)

        extractor = DynamicDataExtractor(self.uuid)

        dynamic_extracted_data, table_labels = await extractor.extract_dynamic_data(doc, dynamic_blocks, file)
        await self.process_dynamic_data_result(dynamic_extracted_data, static_rect_boxes,
                                               filename=os.path.basename(file))

        await self.draw_annotation_and_convert_to_image(doc, static_rect_boxes)
        results = await self.generate_output_response(static_rect_boxes)

        return results, table_labels
