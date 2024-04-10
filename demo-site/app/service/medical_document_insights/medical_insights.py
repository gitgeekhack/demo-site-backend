import os
import time
import json
import asyncio
import traceback
from concurrent import futures

from app import logger
from app.constant import MedicalInsights
from app.service.helper.text_extractor import extract_pdf_text
from app.service.medical_document_insights.nlp_extractor.entity_extractor import get_extracted_entities
from app.service.medical_document_insights.nlp_extractor.document_summarizer import DocumentSummarizer
from app.service.medical_document_insights.nlp_extractor.medical_chronology_extractor import MedicalChronologyExtractor
from app.service.medical_document_insights.nlp_extractor.phi_and_doc_type_extractor import PHIAndDocTypeExtractor
from app.service.medical_document_insights.nlp_extractor.history_extractor import HistoryExtractor
from app.service.medical_document_insights.nlp_extractor.patient_demographics_extractor import PatientDemographicsExtractor


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


async def get_patient_information(data):
    """ This method is used to get phi dates from document """

    x = time.time()
    logger.info("[Medical-Insights] Extraction of PHI and Document Type is started...")
    phi_and_doc_type_extractor = PHIAndDocTypeExtractor()
    patient_information = await phi_and_doc_type_extractor.get_patient_information(data)
    logger.info(f"[Medical-Insights] Extraction of PHI and Document Type is completed in {time.time() - x} seconds.")
    return patient_information


def get_patient_information_handler(data):
    _loop = asyncio.new_event_loop()
    x = _loop.run_until_complete(get_patient_information(data))
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


def format_output(document_wise_response):
    medical_chronology = []
    patient_names = []
    dob_list = []
    for document_resp in document_wise_response:
        medical_chronology.extend(document_resp['medical_chronology'])
        document_resp.pop('medical_chronology')

        patient_names.append(document_resp['patient_information']['patient_name'])
        document_resp['patient_information'].pop('patient_name')

        dob_list.append(document_resp['patient_information']['date_of_birth'])
        document_resp['patient_information'].pop('date_of_birth')
        document_resp['phi_dates'] = document_resp.pop('patient_information')

    medical_chronology = sorted(medical_chronology, key=lambda e: parse_date(e['date']))

    patient_name = ""
    if len(patient_names) > 0:
        patient_names.sort(key=len)
        patient_name = patient_names[-1]

    dob = ""
    if len(dob_list) > 0:
        dob = sorted(dob_list)[0]

    resp_obj = {
        "patient_demographics": {
            "patient_name": patient_name,
            "date_of_birth": dob
        },
        "medical_chronology": medical_chronology,
        "documents": document_wise_response
    }
    return resp_obj


def get_textract_text_handler(document):
    _loop = asyncio.new_event_loop()
    x = _loop.run_until_complete(extract_pdf_text(document))
    res = {
        'name': document,
        'page_wise_text': x
    }
    return res


def parse_date(date_str):
    parts = date_str.split('-')
    if len(parts) == 3:
        month, day, year = map(int, parts)
        return year, month, day
    elif len(parts) == 2:
        month, year = map(int, parts)
        day = 1
        return year, month, day
    elif len(parts) == 1:
        year = int(parts[0])
        month = 1
        day = 1
        return year, month, day
    else:
        raise ValueError("Invalid date format: {}".format(date_str))


async def get_medical_insights(project_path, document_list):
    """ This method is used to get the medical insights from the document """
    try:
        text_result = []
        document_task = []
        with futures.ThreadPoolExecutor(os.cpu_count() - 1) as executor:
            for document in document_list:
                new_future = executor.submit(get_textract_text_handler, document=document)
                document_task.append(new_future)

        document_results = futures.wait(document_task)
        for x in document_results.done:
            text_result.append(x.result())

        document_wise_response = []
        task = []
        with futures.ThreadPoolExecutor(os.cpu_count() - 1) as executor:
            for document in text_result:
                task.append(executor.submit(get_summary_handler, data=document['page_wise_text']))
                task.append(executor.submit(get_entities_handler, data=document['page_wise_text']))
                task.append(executor.submit(get_medical_chronology_handler, data=document))
                task.append(executor.submit(get_patient_information_handler, data=document['page_wise_text']))
                task.append(executor.submit(get_history_handler, data=document['page_wise_text']))
            task.append(executor.submit(get_patient_demographics_handler, data=text_result))

            extracted_outputs = {'name': os.path.basename(document['name'])}
            results = futures.wait(task)
            for x in results.done:
                extracted_outputs.update(x.result())
            document_wise_response.append(extracted_outputs)
        res = format_output(document_wise_response)
        res_obj = {
            "status_code": 200,
            "data": res,
            "message": "OK"
        }

        project_response_path = project_path.replace(MedicalInsights.REQUEST_FOLDER_NAME, MedicalInsights.RESPONSE_FOLDER_NAME)
        os.makedirs(project_response_path, exist_ok=True)
        project_response_file_path = os.path.join(project_response_path, 'output.json')

        with open(project_response_file_path, 'w') as file:
            file.write(json.dumps(res_obj))

    except Exception as e:
        res_obj = {
            "status_code": 500,
            "data": str(e),
            "message": "Internal Server Error"
        }
        logger.error(f'{e} -> {traceback.format_exc()}')
        project_response_path = project_path.replace(MedicalInsights.REQUEST_FOLDER_NAME, MedicalInsights.RESPONSE_FOLDER_NAME)
        os.makedirs(project_response_path, exist_ok=True)
        project_response_file_path = os.path.join(project_response_path, 'output.json')
        with open(project_response_file_path, 'w') as file:
            file.write(json.dumps(res_obj))
