import re
from app.constant import PDFAnnotationAndExtraction


class DynamicDataExtractor:
    async def extract_date_range(self, doc, bounding_box, page_no):
        """
            extracts first and last date from given bounding box
            Parameters:
                doc <Document object>: pdf document opened with PyMuPDF
                bounding_box <list>: python list of bounding box coordinates
                page_no <int>: page number of pdf
            Returns:
                dates extracted from pdf
        """
        extracted_text = doc[page_no].get_textbox(bounding_box)
        matches = re.findall(PDFAnnotationAndExtraction.Regex.DATE, extracted_text)

        if len(matches) == 2:
            return {'policy_start_date': matches[0], 'policy_end_date': matches[1]}
        else:
            return {'policy_start_date': None, 'policy_end_date': None}

    async def extract_dynamic_data(self, doc, bounding_box, page_no):
        """
            extracts dynamic data from pdf file
            Parameters:
                doc <Document object>: pdf document opened with PyMuPDF
                bounding_box <list>: python list of bounding box coordinates
                page_no <int>: page number of pdf
            Returns:
                dynamic data extracted from pdf
        """
        type_of_data = bounding_box[0]
        if type_of_data == PDFAnnotationAndExtraction.TypesOfDynamicData.DATE_RANGE:
            return await self.extract_date_range(doc, bounding_box[1:], page_no)
