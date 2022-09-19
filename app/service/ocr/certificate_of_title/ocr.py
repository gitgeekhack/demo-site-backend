import csv
import os

import cv2
from google.cloud import vision
from app.common.utils import MonoState
from app.constant import DrivingLicenseParser
from app.service.helper.certificate_of_title_helper import apply_preprocessing, cropped_object_removal, \
    bradley_roth_numpy
from app.service.helper.certificate_of_title_parser import parse_title_number, parse_vin, parse_year, parse_make, \
    parse_model, parse_body_style, parse_owner_name, parse_address, parse_lien_name, parse_odometer_reading, \
    parse_doc_type, parse_title_type, parse_remarks, parse_issue_date

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/vishva/Downloads/solid-coral-358809-c1e9bab2aac9.json"


def load_us_cities():
    with open(DrivingLicenseParser.WORLD_CITIES_LIST, newline='') as csvfile:
        reader = csv.reader(csvfile)
        us_cities = [row[0] for row in reader if row[4] == 'United States']
    return us_cities


def detect_text(image):
    client = vision.ImageAnnotatorClient()

    response = client.text_detection(
        image=image,
        image_context={"language_hints": ["en_US"]}
    )
    texts = response.text_annotations

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

    return texts


class CertificateOfTitleOCR(MonoState):
    _internal_state = {'us_cities': load_us_cities()}

    async def get_title_number(self, image):
        pre_image = await apply_preprocessing(image, auto_scaling=True, resize_dimension=500)
        clean_image = await cropped_object_removal(pre_image)

        success, encoded_image = cv2.imencode('.jpg', clean_image)
        roi_image = encoded_image.tobytes()
        roi_image = vision.Image(content=roi_image)

        texts = detect_text(roi_image)
        text_list = [text.description for text in texts]
        title_no = ''

        if text_list:
            title_no = parse_title_number(text_list[0])

        return title_no

    async def get_vin(self, image):
        pre_image = await apply_preprocessing(image, auto_scaling=True, resize_dimension=500)
        clean_image = await cropped_object_removal(pre_image)

        success, encoded_image = cv2.imencode('.jpg', clean_image)
        roi_image = encoded_image.tobytes()
        roi_image = vision.Image(content=roi_image)

        texts = detect_text(roi_image)
        text_list = [text.description for text in texts]
        vin = ''
        if text_list:
            vin = parse_vin(text_list[0])

        if not vin:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            bradley_image = await bradley_roth_numpy(gray, t=12)

            success, encoded_image = cv2.imencode('.jpg', bradley_image)
            roi_image = encoded_image.tobytes()
            roi_image = vision.Image(content=roi_image)

            texts = detect_text(roi_image)
            text_list = [text.description for text in texts]

            vin = parse_vin(text_list[0])

        return vin

    async def get_year(self, image):
        image = await apply_preprocessing(image, auto_scaling=True, resize_dimension=500)
        clean_image = await cropped_object_removal(image)
        success, encoded_image = cv2.imencode('.jpg', clean_image)
        roi_image = encoded_image.tobytes()
        roi_image = vision.Image(content=roi_image)

        texts = detect_text(roi_image)
        text_list = [text.description for text in texts]
        year = ''

        if text_list:
            year = parse_year(text_list[0])

        return year

    async def get_make(self, image):
        pre_image = await apply_preprocessing(image, auto_scaling=True, resize_dimension=320)
        clean_image = await cropped_object_removal(pre_image)
        success, encoded_image = cv2.imencode('.jpg', clean_image)
        roi_image = encoded_image.tobytes()
        roi_image = vision.Image(content=roi_image)

        texts = detect_text(roi_image)
        text_list = [text.description for text in texts]
        make = ''

        if text_list:
            make = parse_make(text_list[0])

        return make

    async def get_model(self, image):
        pre_image = await apply_preprocessing(image, auto_scaling=True, resize_dimension=320)
        clean_image = await cropped_object_removal(pre_image)
        success, encoded_image = cv2.imencode('.jpg', clean_image)
        roi_image = encoded_image.tobytes()
        roi_image = vision.Image(content=roi_image)

        texts = detect_text(roi_image)
        text_list = [text.description for text in texts]
        model = ''
        if text_list:
            model = parse_model(text_list[0])

        return model

    async def get_body_style(self, image):
        pre_image = await apply_preprocessing(image, auto_scaling=True, resize_dimension=320)
        clean_image = await cropped_object_removal(pre_image)
        success, encoded_image = cv2.imencode('.jpg', clean_image)
        roi_image = encoded_image.tobytes()
        roi_image = vision.Image(content=roi_image)

        texts = detect_text(roi_image)
        text_list = [text.description for text in texts]
        body_style = ''

        if text_list:
            body_style = parse_body_style(text_list[0])

        return body_style

    async def get_odometer_reading(self, image):
        pre_image = await apply_preprocessing(image, auto_scaling=True, resize_dimension=500)
        clean_image = await cropped_object_removal(pre_image)

        success, encoded_image = cv2.imencode('.jpg', clean_image)
        roi_image = encoded_image.tobytes()
        roi_image = vision.Image(content=roi_image)

        texts = detect_text(roi_image)
        text_list = [text.description for text in texts]
        odometer = ''
        if text_list:
            odometer = parse_odometer_reading(text_list[0])

        if not odometer:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            bradley_image = await bradley_roth_numpy(gray, t=12)

            success, encoded_image = cv2.imencode('.jpg', bradley_image)
            roi_image = encoded_image.tobytes()
            roi_image = vision.Image(content=roi_image)

            texts = detect_text(roi_image)
            text_list = [text.description for text in texts]

            odometer = parse_odometer_reading(text_list[0])

        return odometer

    async def get_owner_name(self, image):
        pre_image = await apply_preprocessing(image, auto_scaling=True, resize_dimension=400)
        clean_image = await cropped_object_removal(pre_image)

        success, encoded_image = cv2.imencode('.jpg', clean_image)
        roi_image = encoded_image.tobytes()
        roi_image = vision.Image(content=roi_image)

        texts = detect_text(roi_image)
        text_list = [text.description for text in texts]
        owner_name = ''

        if text_list:
            owner_name = parse_owner_name(text_list[0])

        return owner_name

    async def get_address(self, image):
        pre_image = await apply_preprocessing(image, auto_scaling=True, resize_dimension=400)
        clean_image = await cropped_object_removal(pre_image)

        success, encoded_image = cv2.imencode('.jpg', clean_image)
        roi_image = encoded_image.tobytes()
        roi_image = vision.Image(content=roi_image)

        texts = detect_text(roi_image)
        text_list = [text.description for text in texts]
        address = ''

        if text_list:
            address = parse_address(text_list[0],cities=self.us_cities)

        return address

    async def get_lien_address(self, image):
        pre_image = await apply_preprocessing(image, auto_scaling=True, resize_dimension=500)
        clean_image = await cropped_object_removal(pre_image)

        success, encoded_image = cv2.imencode('.jpg', clean_image)
        roi_image = encoded_image.tobytes()
        roi_image = vision.Image(content=roi_image)

        texts = detect_text(roi_image)
        text_list = [text.description for text in texts]
        address = ''

        if text_list:
            address = parse_address(text_list[0], cities=self.us_cities)

        return address

    async def get_lien_name(self, image):
        pre_image = await apply_preprocessing(image, auto_scaling=True, resize_dimension=500)
        clean_image = await cropped_object_removal(pre_image)

        success, encoded_image = cv2.imencode('.jpg', clean_image)
        roi_image = encoded_image.tobytes()
        roi_image = vision.Image(content=roi_image)

        texts = detect_text(roi_image)
        text_list = [text.description for text in texts]
        lien_name = ''
        if text_list:
            lien_name = parse_lien_name(text_list[0])

        return lien_name

    async def get_date(self, image):
        pre_image = await apply_preprocessing(image, auto_scaling=True, resize_dimension=500)
        clean_image = await cropped_object_removal(pre_image)

        success, encoded_image = cv2.imencode('.jpg', clean_image)
        roi_image = encoded_image.tobytes()
        roi_image = vision.Image(content=roi_image)

        texts = detect_text(roi_image)
        text_list = [text.description for text in texts]
        date = ''

        if text_list:
            date = parse_issue_date(text_list[0])

        return date

    async def get_doc_type(self, image):
        pre_image = await apply_preprocessing(image, auto_scaling=True, resize_dimension=500)
        clean_image = await cropped_object_removal(pre_image)

        success, encoded_image = cv2.imencode('.jpg', clean_image)
        roi_image = encoded_image.tobytes()
        roi_image = vision.Image(content=roi_image)

        texts = detect_text(roi_image)
        text_list = [text.description for text in texts]
        doc_type = ''
        if text_list:
            doc_type = parse_doc_type(text_list[0])

        return doc_type

    async def get_title_type(self, image):
        pre_image = await apply_preprocessing(image, auto_scaling=True, resize_dimension=500)
        clean_image = await cropped_object_removal(pre_image)

        success, encoded_image = cv2.imencode('.jpg', clean_image)
        roi_image = encoded_image.tobytes()
        roi_image = vision.Image(content=roi_image)

        texts = detect_text(roi_image)
        text_list = [text.description for text in texts]
        title_type = ''

        if text_list:
            title_type = parse_title_type(text_list[0])

        return title_type

    async def get_remark(self, image):
        pre_image = await apply_preprocessing(image, auto_scaling=True, resize_dimension=500)
        clean_image = await cropped_object_removal(pre_image)

        success, encoded_image = cv2.imencode('.jpg', clean_image)
        roi_image = encoded_image.tobytes()
        roi_image = vision.Image(content=roi_image)

        texts = detect_text(roi_image)
        text_list = [text.description for text in texts]
        remark = ''
        if text_list:
            remark = parse_remarks(text_list[0])

        return remark
