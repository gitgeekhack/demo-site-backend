import os
import json
import time
import boto3
import asyncio
import pdf2image
from concurrent import futures

from app import logger

os.environ['AWS_DEFAULT_REGION'] = "us-east-1"
pdf_folder_name = None
textract = boto3.client('textract', region_name="us-east-1")


async def get_textract_response(image_path):
    """ This method used to call the textract and return the response """

    with open(image_path, 'rb') as image_file:
        img = bytearray(image_file.read())
        response = textract.detect_document_text(
            Document={
                'Bytes': img,
            },
        )

    page_text = ""
    for item in response['Blocks']:
        if item['BlockType'] == 'LINE':
            page_text += item['Text'] + ' '

    return page_text


async def convert_pdf_to_text(pdf_output_dir, image, index):
    """ This method is used to convert pdf page into image and stores the page """

    image_path = os.path.join(pdf_output_dir, f"{index + 1}.jpg")
    image.save(image_path)
    page_text = await get_textract_response(image_path)
    return {f"page_{index + 1}": page_text}


def convert_pdf_to_text_handler(pdf_output_dir, image, index):
    _loop = asyncio.new_event_loop()
    x = _loop.run_until_complete(convert_pdf_to_text(pdf_output_dir, image, index))
    return x


async def save_textract_response(output_dir, page_wise_text):
    """ This method is used to save the textract response in the storage """

    global pdf_folder_name

    json_output_dir = os.path.join(output_dir, "textract_response")

    if not os.path.exists(json_output_dir):
        os.makedirs(json_output_dir, exist_ok=True)
    json_file_path = os.path.join(json_output_dir, f"{pdf_folder_name}_text.json")

    with open(json_file_path, 'w') as json_file:
        json.dump(page_wise_text, json_file, indent=4)


async def extract_pdf_text(file_path, output_dir):
    """ This method is used to provide extracted get from pdf """

    global pdf_folder_name

    x = time.time()
    pdf_images = pdf2image.convert_from_path(file_path)
    pdf_folder_name = os.path.basename(file_path).replace(".pdf", "")
    pdf_output_dir = os.path.join(output_dir, "pdf_images")

    if not os.path.exists(pdf_output_dir):
        os.makedirs(pdf_output_dir, exist_ok=True)

    task = []
    with futures.ProcessPoolExecutor(os.cpu_count() - 1) as executor:
        for i, image in enumerate(pdf_images):
            new_future = executor.submit(convert_pdf_to_text_handler, pdf_output_dir=pdf_output_dir,
                                         image=image, index=i)
            task.append(new_future)

    results = futures.wait(task)

    texts = {}
    for page_text in results.done:
        texts.update(page_text.result())

    page_wise_text = dict(sorted(texts.items(), key=lambda item: item[0]))

    await save_textract_response(output_dir, page_wise_text)

    logger.info(f"Text Extraction from document is completed in {time.time() - x} seconds.")

    return page_wise_text
