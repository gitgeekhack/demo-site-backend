import re
from app.service.helper.table_extractor import TableExtractor
from app.constant import PDFAnnotationAndExtraction
from app import logger


class DynamicDataExtractor:
    def __init__(self, uuid):
        self.uuid = uuid

    @staticmethod
    async def __extract_date_range(doc, box, page_no):
        """
            extracts first and last date from given bounding box
            Parameters:
                doc <Document object>: pdf document opened with PyMuPDF
                bounding_box <list>: python list of bounding box coordinates
                page_no <int>: page number of pdf
            Returns:
                dates extracted from pdf
        """
        bounding_box = [box[1][0]['@xtl'], box[1][0]['@ytl'], box[1][0]['@xbr'], box[1][0]['@ybr']]
        extracted_text = doc[page_no].get_textbox(bounding_box)
        matches = re.findall(PDFAnnotationAndExtraction.Regex.DATE, extracted_text)

        if len(matches) == 2:
            return {page_no: {box[1][0]['@label']: {'data': f'Start Date: {matches[0]}, End Date: {matches[1]}',
                                                    'bbox': bounding_box}}}
        else:
            return {page_no: {box[1][0]['@label']: {'data': f'Start Date: {None}, End Date: {None}',
                                                    'bbox': bounding_box}}}

    @staticmethod
    async def __get_tables(box, page_no, tables):
        bounding_box = [box[1][0]['@xtl'], box[1][0]['@ytl'], box[1][0]['@xbr'], box[1][0]['@ybr']]
        filename = box[0].split('.')[0][:-9] + '.pdf'
        table_name = box[1][0]['@label']
        if table_name not in tables.keys():
            tables[table_name] = {}

        tables[table_name].update({'page': page_no})
        tables[table_name].update({'filename': filename})
        tables[table_name].update({[box[1][0]['attribute']['#text']][0]: bounding_box})

        return tables

    @staticmethod
    async def __response_generator(data, response):
        for key in list(data.keys()):
            if key in response.keys():
                response[key].update(data[key])
            else:
                response.update(data)

    async def extract_dynamic_data(self, doc, dynamic_blocks, file):
        """
            extracts dynamic data from pdf file
            Parameters:
                doc <Document object>: pdf document opened with PyMuPDF
                bounding_box <list>: python list of bounding box coordinates
                page_no <int>: page number of pdf
            Returns:
                dynamic data extracted from pdf
        """
        response = {}
        tables = {}
        table_labels = set()
        try:
            for page_no, boxes in dynamic_blocks.items():
                for box in boxes:
                    if box[1][0]['attribute']['@name'] == PDFAnnotationAndExtraction.TypesOfDynamicData.DATE_RANGE:
                        date = await self.__extract_date_range(doc, box, page_no)
                        await self.__response_generator(date, response)
                    elif box[1][0]['attribute']['@name'] == PDFAnnotationAndExtraction.TypesOfDynamicData.TABLE:
                        tables = await self.__get_tables(box, page_no, tables)
                        table_labels.add(box[1][0]['@label'].replace('_', ' ').title())

            table_extractor = TableExtractor(self.uuid)

            table_result = await table_extractor.extract(tables, doc, file)
            await self.__response_generator(table_result, response)
        except (AttributeError, IndexError) as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')

        return response, table_labels
