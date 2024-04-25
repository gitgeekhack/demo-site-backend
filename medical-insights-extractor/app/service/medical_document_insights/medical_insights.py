import os
import time
import json
import asyncio
import traceback
from concurrent import futures

from app import logger
from app.common.s3_utils import s3_utils
from app.constant import MedicalInsights, AWS
from app.service.helper.text_extractor import extract_pdf_text
from app.service.medical_document_insights.nlp_extractor.entity_extractor import get_extracted_entities
from app.service.medical_document_insights.nlp_extractor.document_summarizer import DocumentSummarizer
from app.service.medical_document_insights.nlp_extractor.medical_chronology_extractor import MedicalChronologyExtractor
from app.service.medical_document_insights.nlp_extractor.doc_type_extractor import DocTypeExtractor
from app.service.medical_document_insights.nlp_extractor.history_extractor import HistoryExtractor
from app.service.medical_document_insights.nlp_extractor.patient_demographics_extractor import \
    PatientDemographicsExtractor


async def get_summary(data):
    """ This method is used to get document summary """

    x = time.time()
    logger.info("[Medical-Insights] Summary generation is started...")
    document_summarizer = DocumentSummarizer()
    summary = await document_summarizer.get_summary(data)
    logger.info(f"[Medical-Insights] Summary is generated in {time.time() - x} seconds.")
    return summary


def get_summary_handler(data):
    _loop = asyncio.new_event_loop()
    x = _loop.run_until_complete(get_summary(data))
    return x


async def get_entities(data):
    """ This method is used to get entities from document """

    x = time.time()
    logger.info("[Medical-Insights] Entity Extraction is started...")
    entities = await get_extracted_entities(data)
    logger.info(f"[Medical-Insights] Entity Extraction is completed in {time.time() - x} seconds.")
    return entities


def get_entities_handler(data):
    _loop = asyncio.new_event_loop()
    x = _loop.run_until_complete(get_entities(data))
    return x


async def get_patient_demographics(data):
    """ This method is used to get phi dates from document """

    x = time.time()
    logger.info("[Medical-Insights] Extraction of Patient Demographics is started...")
    demographics_extractor = PatientDemographicsExtractor()
    patient_demographics = await demographics_extractor.get_patient_demographics(data)
    logger.info(f"[Medical-Insights] Extraction of Patient Demographics is completed in {time.time() - x} seconds.")
    return patient_demographics


def get_patient_demographics_handler(data):
    _loop = asyncio.new_event_loop()
    x = _loop.run_until_complete(get_patient_demographics(data))
    return x


async def get_document_type(data):
    """ This method is used to get phi dates from document """

    x = time.time()
    logger.info("[Medical-Insights] Extraction of Document Type is started...")
    doc_type_extractor = DocTypeExtractor()
    doc_type = await doc_type_extractor.extract_document_type(data)
    logger.info(f"[Medical-Insights] Extraction of Document Type is completed in {time.time() - x} seconds.")
    return doc_type


def get_document_type_handler(data):
    _loop = asyncio.new_event_loop()
    x = _loop.run_until_complete(get_document_type(data))
    return x


async def get_medical_chronology(data):
    """ This method is used to get phi dates from document """

    x = time.time()
    logger.info("[Medical-Insights] Medical Chronology Extraction is started...")
    medical_chronology_extractor = MedicalChronologyExtractor()
    medical_chronology = await medical_chronology_extractor.get_medical_chronology(data)
    logger.info(f"[Medical-Insights] Medical Chronology Extraction is completed in {time.time() - x} seconds.")
    return medical_chronology


def get_medical_chronology_handler(data):
    _loop = asyncio.new_event_loop()
    x = _loop.run_until_complete(get_medical_chronology(data))
    return x


async def get_history(data):
    """ This method is used to get History and Psychiatric Injury from document """

    x = time.time()
    logger.info("[Medical-Insights] History & Psychiatric Injury Extraction is started...")
    history_extractor = HistoryExtractor()
    history_info = await history_extractor.get_history(data)
    logger.info(f"[Medical-Insights] History & Psychiatric Injury Extraction is completed in {time.time() - x} seconds.")
    return history_info


def get_history_handler(data):
    _loop = asyncio.new_event_loop()
    x = _loop.run_until_complete(get_history(data))
    return x


def get_textract_text_handler(document):
    _loop = asyncio.new_event_loop()
    x = _loop.run_until_complete(extract_pdf_text(document))
    res = {
        'name': document,
        'page_wise_text': x
    }
    return res


async def format_output(extracted_outputs):
    logger.info("[Medical-Insights] Formatting of Response started...")

    document_wise_response = {}
    for document_resp in extracted_outputs:
        if 'document_name' in document_resp.keys():
            if document_resp['document_name'] not in document_wise_response.keys():
                document_wise_response[document_resp['document_name']] = {}
            key = list(document_resp.keys())
            key.remove("document_name")
            document_wise_response[document_resp['document_name']][key[0]] = document_resp[key[0]]

    document_wise_response_list = []

    for key, value in document_wise_response.items():
        value |= {"document_name": os.path.basename(key)}
        document_wise_response_list.append(value)

    logger.info("[Medical-Insights] Formatting of Response ended...")
    return document_wise_response_list


async def merge_outputs(formatted_output, project_path):
    logger.info("[Medical-Insights] Merging of Responses started...")

    local_file_path = project_path.replace(os.path.join(MedicalInsights.PREFIX, 'user-data'), 'static')
    local_file_path = local_file_path.replace(MedicalInsights.REQUEST_FOLDER_NAME, MedicalInsights.RESPONSE_FOLDER_NAME)
    local_file_path = os.path.join(local_file_path, 'output.json')

    if os.path.exists(local_file_path):
        with open(local_file_path, 'r') as file:
            processed_data = json.loads(file.read())

        if processed_data['status_code'] == 200:
            documents = processed_data['data']
            documents.extend(formatted_output)
            logger.info("[Medical-Insights] Merging of Responses ended...")
            return documents
        else:
            return formatted_output
    else:
        return formatted_output


async def get_medical_insights(project_path, document_list):
    """ This method is used to get the medical insights from the document """
    try:
        text_result = []
        document_task = []
        with futures.ThreadPoolExecutor(2) as executor:
            for document in document_list:
                if document.endswith('.pdf'):
                    new_future = executor.submit(get_textract_text_handler, document=document)
                    document_task.append(new_future)

        document_results = futures.wait(document_task)
        for x in document_results.done:
            text_result.append(x.result())

        task = []
        with futures.ThreadPoolExecutor(2) as executor:
            for document in text_result:
                task.append(executor.submit(get_summary_handler, data=document))
                task.append(executor.submit(get_entities_handler, data=document))
                task.append(executor.submit(get_medical_chronology_handler, data=document))
                task.append(executor.submit(get_history_handler, data=document))
                task.append(executor.submit(get_document_type_handler, data=document))
                task.append(executor.submit(get_patient_demographics_handler, data=document))

            extracted_outputs = []
            results = futures.wait(task)
            for x in results.done:
                extracted_outputs.append(x.result())

        formatted_output = await format_output(extracted_outputs)
        merged_output = await merge_outputs(formatted_output, project_path)
        res_obj = {
            "status_code": 200,
            "data": merged_output,
            "message": "OK"
        }

        project_response_path = project_path.replace(MedicalInsights.REQUEST_FOLDER_NAME,
                                                     MedicalInsights.RESPONSE_FOLDER_NAME)
        project_response_path = project_response_path.replace('static', 'user-data')
        s3_output_key = os.path.join(project_response_path, 'output.json')

        result = json.dumps(res_obj)
        result = result.encode("utf-8")
        await s3_utils.upload_object(AWS.S3.MEDICAL_BUCKET_NAME, s3_output_key, result, AWS.S3.ENCRYPTION_KEY)
        logger.info(f"[Medical-Insights] Output Stored in {s3_output_key} !!!")

        s3_embedding_paths = project_response_path.replace(MedicalInsights.RESPONSE_FOLDER_NAME, 'embeddings')
        project_embedding_file_path = os.path.join(s3_embedding_paths, 'embeddings.pkl')
        response = await s3_utils.check_s3_path_exists(aws_bucket=AWS.S3.MEDICAL_BUCKET_NAME,
                                                       key=project_embedding_file_path)
        if response:
            await s3_utils.delete_object(aws_bucket=AWS.S3.MEDICAL_BUCKET_NAME, key=project_embedding_file_path)
            logger.info(f"[Medical-Insights] embeddings.pkl removed from {project_embedding_file_path} !!!")

    except Exception as e:
        res_obj = {
            "status_code": 500,
            "data": str(e),
            "message": "Internal Server Error"
        }
        logger.error(f'{e} -> {traceback.format_exc()}')

        s3_key = project_path.replace(MedicalInsights.PREFIX, '')
        project_response_path = s3_key.replace(MedicalInsights.REQUEST_FOLDER_NAME,
                                               MedicalInsights.RESPONSE_FOLDER_NAME)
        project_response_file_path = os.path.join(project_response_path, 'output.json')

        result = json.dumps(res_obj)
        result = result.encode("utf-8")
        await s3_utils.upload_object(AWS.S3.MEDICAL_BUCKET_NAME, project_response_file_path, result,
                                     AWS.S3.ENCRYPTION_KEY)
