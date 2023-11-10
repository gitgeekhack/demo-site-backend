import pdf2image
import os
import boto3
import json


class PDFTextExtractor:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.text_per_page = []
        self.page_text_json = {}
        self.document_page_counter = 1
        self.textract = boto3.client('textract', region_name="us-east-1")

    def create_output_directory(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def convert_pdf_to_images(self):
        pdf_images = pdf2image.convert_from_path(self.input_dir)
        self.pdf_folder_name = os.path.basename(self.input_dir).replace(".pdf", "")
        pdf_output_dir = os.path.join(self.output_dir, self.pdf_folder_name)

        if not os.path.exists(pdf_output_dir):
            os.makedirs(pdf_output_dir, exist_ok=True)

        for i, image in enumerate(pdf_images):
            image_path = os.path.join(pdf_output_dir, f"{i + 1}.jpg")
            image.save(image_path)
            self.extract_text_from_image(image_path, i)

    def extract_text_from_image(self, image_path, page_number):
        with open(image_path, 'rb') as image_file:
            img = bytearray(image_file.read())
            response = self.textract.detect_document_text(
                Document={
                    'Bytes': img,
                },
            )
            page_text = ""
            for item in response['Blocks']:
                if item['BlockType'] == 'LINE':
                    page_text += item['Text'] + ' '
            self.text_per_page.append(page_text)
            self.page_text_json[f"Page {page_number + 1}"] = page_text
        return self.page_text_json

    def save_text_to_json(self):
        json_file_path = os.path.join(self.output_dir, f"{self.pdf_folder_name}_text.json")
        with open(json_file_path, 'w') as json_file:
            json.dump(self.page_text_json, json_file, indent=4)

    def extract_and_save_text(self):
        self.create_output_directory()
        self.convert_pdf_to_images()
        self.save_text_to_json()
