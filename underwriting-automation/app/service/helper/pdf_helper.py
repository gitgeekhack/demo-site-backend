import fitz

from app.constant import PDF
from app.service.helper.cv_helper import CVHelper


class PDFHelper:
    """ Contains helper method for commonly used PDF extraction operations"""

    def __init__(self, doc):
        self.doc = doc
        self.metadata = ()
        for page in self.doc:
            blocks = page.get_text('dict')['blocks']
            page_text = tuple(
                [(span['text'], span['bbox'], page.number) for block in blocks if not block['type'] for line in
                 block['lines'] for span in line['spans']])
            page_text = tuple(sorted(page_text, key=lambda x: x[1][1]))
            self.metadata = self.metadata + page_text
        self.converted_doc = fitz.open('pdf', self.doc.convert_to_pdf(from_page=0, to_page=self.doc.page_count))

    async def get_images_by_page(self, page_no):
        """
        extracts all images from input page of a pdf document.
        Parameters:
            page_no <int>: The input PDF document Page number.
        Returns:
            <list>: The output list of images present on the input Page
        """
        return self.converted_doc[page_no].get_images(full=True)

    async def find_page_by_text(self, text):
        """
          finds page number where input text is found
          Parameters:
              text <str>: The input text to be found.
          Returns:
              <list>: The list of page number(s) where the input text is found
          """
        output = list(filter(lambda x: text in x, self.metadata))
        return list(set([x[-1] for x in output])) if output else None

    async def apply_bbox_padding(self, page_no, bbox, x0_pad=0.0, y0_pad=0.0, x1_pad=0.0, y1_pad=0.0):
        """
            applies padding to the input bounding box relative to the page size.
            Parameters:
              page_no <int> : The input page_no of bounding box.
              bbox <tuple> : The input bounding box to be padded.
              x0_pad <float> : The input percentage relative to page size to be padded to x0
              x1_pad <float> : The input percentage relative to page size to be padded to x1
              y0_pad <float> : The input percentage relative to page size to be padded to y0
              y1_pad <float> : The input percentage relative to page size to be padded to y1
            Returns:
             <tuple> : The output padded bounding box
        """
        x0, y0, x1, y1 = bbox
        page_dim = self.doc[page_no].CropBox
        w = page_dim[2]
        h = page_dim[3]
        x0, y0 = x0 + w * x0_pad, y0 + h * y0_pad
        x1, y1 = x1 + w * x1_pad, y1 + h * y1_pad
        return x0, y0, x1, y1

    async def match_bbox(self, source_bboxes, target_bbox):
        """
            calculate iou of text bounding box for each section bounding box.
            Parameters:
                source_bboxes <list> : List of Bounding Box of Sections.
                target_bbox <tuple> : The input bounding box of target.
            Return:
                <tuple>, None: Matched source bounding box else None.
        """
        cv_helper = CVHelper()
        response = tuple([section_bbox for section_bbox in source_bboxes if
                          await cv_helper.calculate_iou(section_bbox, target_bbox) > 0])
        return response if response else None

    async def get_bbox_by_text(self, text, page_no=None):
        """
            Return Bounding Box and Page Number where is text is found on the page.
            If page number is not given it will return Bounding Box and Page Number
            for whole document where text is found.
            Parameters:
                text <str> : The input text to be found.
                page_no <int> : The input page_no of document.
            Return:
                <tuple> : The output bounding box and page number where text is found.
        """
        bbox = tuple(filter(lambda x: text == x[PDF.TEXT].strip() and page_no == x[PDF.PAGE_NUMBER],
                            self.metadata)) if page_no is not None else tuple(
            filter(lambda x: text == x[PDF.TEXT].strip(), self.metadata))
        bbox = tuple(x[1:] for x in bbox)
        return bbox

    async def get_attributes_by_text(self, text, page_no=None):
        """
            Return all attributes of data of the input text is found on the page.
            If text is not given it will return attributes for whole document where text is found.
            Parameters:
                text <str> : The input text to be found.
                page_no <int> : The input page_no of document.
            Return:
                <tuple> : The output bounding box and page number where text is found.
        """
        data = tuple(filter(lambda x: text in x and page_no == x[PDF.PAGE_NUMBER],
                            self.metadata)) if page_no is not None else tuple(
            filter(lambda x: text in x[PDF.TEXT], self.metadata))
        return data

    async def get_attributes_by_page(self, page_no):
        """
            Return all attributes of input page of document.
            Parameters:
                page_no <int> : The input page_no of document.
            Return:
                <tuple> : The output text, bounding box and page number where page_no is found.
        """
        data = tuple(filter(lambda x: x[PDF.PAGE_NUMBER] == page_no, self.metadata))
        return data

    async def get_form_fields_by_page(self, page_no):
        """
            Return PDF Form field, also called a “widget”, as dictionary of field name as key and
            field value as dictionary value and returns None when no form field is found on the page.
            Parameters:
                page_no <int> : The input page_no of document.
            Return:
                fields <dict>: PDF Form field name and value for the given page no, as dictionary of field name
                 as key and field value is dictionary value. {field_name: field_value}
        """
        fields = {field.field_name: field.field_value for field in self.doc[page_no].widgets()}
        return fields if fields else None
