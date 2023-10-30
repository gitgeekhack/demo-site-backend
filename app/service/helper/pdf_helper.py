import io
import traceback

import fitz
from PIL import Image
from app.common.utils import stop_watch
from flask import current_app
from app.business_rule_exception import InvalidFileException


class PDFHelper:


    def __get_image_pixel_map(self, item):
        xref = item[0]  # xref of PDF image
        smask = item[1]  # xref of its /SMask

        # special case: /SMask exists
        # use Pillow to recover original image
        if smask > 0:
            fpx = io.BytesIO(  # BytesIO object from image binary
                self.__pdf_document.extractImage(xref)["image"],
            )
            fps = io.BytesIO(  # BytesIO object from smask binary
                self.__pdf_document.extractImage(smask)["image"],
            )
            img0 = Image.open(fpx)  # Pillow Image
            mask = Image.open(fps)  # Pillow Image
            img = Image.new("RGBA", img0.size)  # prepare result Image
            img.paste(img0, None, mask)  # fill in base image and mask
            bf = io.BytesIO()
            img.save(bf, "png")  # save to BytesIO
            return {
                "ext": "png",
                "colorspace": 3,
                "image": bf.getvalue()
            }

        # special case: /ColorSpace definition exists
        # to be sure, we convert these cases to RGB PNG images
        if "/ColorSpace" in self.__pdf_document.xrefObject(xref, compressed=True):
            pix1 = fitz.Pixmap(self.__pdf_document, xref)
            pix2 = fitz.Pixmap(fitz.csRGB, pix1)
            return {
                "ext": "png",
                "colorspace": 3,
                "image": pix2.getImageData("png")
            }
        return self.__pdf_document.extractImage(xref)


    def extract_first_image(self, file_path):
        self.__pdf_document = fitz.open(file_path)
        if not self.__pdf_document.is_pdf:
            raise InvalidFileException(file_path)
        image_vector_list = self.__pdf_document.getPageImageList(0)
        print(f'number of images found in page 1:{len(image_vector_list)}')
        if len(image_vector_list) == 0:
            return
        first_vector = image_vector_list[0]
        image_pixel_map = self.__get_image_pixel_map(item=first_vector)
        image_bytes = image_pixel_map["image"]
        image = Image.open(io.BytesIO(image_bytes))
        return image
