import os
import json
import time
import fitz
import asyncio
from concurrent import futures

from app import logger
from app.constant import AWS
from app.common.s3_utils import s3_utils
from app.service.helper import textract_client

os.environ['AWS_DEFAULT_REGION'] = AWS.BotoClient.AWS_DEFAULT_REGION
pdf_folder_name = None
textract = textract_client

zoom = 2  # to increase the resolution of image
matrix = fitz.Matrix(zoom, zoom)


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


async def convert_pdf_to_text(pdf_output_dir, page_no, doc_path):
    """ This method is used to convert pdf page into image and stores the page """

    document = fitz.open(doc_path)
    page = document[page_no]
    image = page.get_pixmap(matrix=matrix)
    image_path = os.path.join(pdf_output_dir, f'{page_no + 1}.jpg')
    image.save(image_path)
    page_text = await get_textract_response(image_path)
    return {f"page_{page_no + 1}": page_text}


def convert_pdf_to_text_handler(pdf_output_dir, page_no, doc_path):
    _loop = asyncio.new_event_loop()
    x = _loop.run_until_complete(convert_pdf_to_text(pdf_output_dir, page_no, doc_path))
    return x


async def save_textract_response(pdf_name, output_dir, page_wise_text):
    """ This method is used to save the textract response in the storage """

    json_output_dir = os.path.join(output_dir, "textract_response")

    if not os.path.exists(json_output_dir):
        os.makedirs(json_output_dir, exist_ok=True)

    json_file_path = os.path.join(json_output_dir, f"{pdf_name}_text.json")

    with open(json_file_path, 'w') as json_file:
        json.dump(page_wise_text, json_file, indent=4)


async def extract_pdf_text(file_path):
    """ This method is used to provide extracted get from pdf """

    x = time.time()

    logger.info("[Medical-Insights] Text Extraction from document is started...")

    pdf_name = os.path.basename(file_path)
    dir_path = "/".join(file_path.split('/')[:3])
    textract_path = os.path.join(dir_path, 'textract_response')
    local_textract_path = os.path.join(f'{textract_path}/{pdf_name}_text.json')
    s3_textract_path = local_textract_path.replace('static', 'user-data')

    os.makedirs(local_textract_path, exist_ok=True)
    response = await s3_utils.check_s3_path_exists(bucket=AWS.S3.MEDICAL_BUCKET_NAME, key=s3_textract_path)

    if response:
        await s3_utils.download_object(AWS.S3.MEDICAL_BUCKET_NAME, s3_textract_path, local_textract_path,
                                       AWS.S3.ENCRYPTION_KEY)
        with open(local_textract_path, 'r') as file:
            json_data = json.loads(file.read())
        page_wise_text = json_data
        logger.info("[Medical-Insights] Reading textract response from the cache...")

    else:
        pdf_output_dir = os.path.join(dir_path, "pdf_images")
        os.makedirs(pdf_output_dir, exist_ok=True)

        document = fitz.open(file_path)

        task = []
        with futures.ProcessPoolExecutor(os.cpu_count() - 1) as executor:
            for page_no in range(len(document)):
                new_future = executor.submit(convert_pdf_to_text_handler, pdf_output_dir=pdf_output_dir,
                                             page_no=page_no, doc_path=file_path)
                task.append(new_future)

        results = futures.wait(task)

        texts = {}
        for page_text in results.done:
            texts.update(page_text.result())

        page_wise_text = dict(sorted(texts.items(), key=lambda item: int(item[0].split('_')[1])))

        result = json.dumps(page_wise_text)
        result = result.encode("utf-8")
        await s3_utils.upload_object(AWS.S3.MEDICAL_BUCKET_NAME, s3_textract_path, result, AWS.S3.ENCRYPTION_KEY)

    logger.info(f"[Medical-Insights] Text Extraction from document is completed in {time.time() - x} seconds.")

    return page_wise_text
