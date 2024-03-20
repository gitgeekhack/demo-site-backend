import os
import time
import asyncio
from concurrent import futures

from app import logger
from app.service.helper.text_extractor import extract_pdf_text
from app.service.medical_document_insights.nlp_extractor.entity_extractor import get_extracted_entities
from app.service.medical_document_insights.nlp_extractor.document_summarizer import DocumentSummarizer
from app.service.medical_document_insights.nlp_extractor.encounters_extractor import EncountersExtractor
from app.service.medical_document_insights.nlp_extractor.phi_and_doc_type_extractor import PHIAndDocTypeExtractor


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


async def get_patient_information(document):
    """ This method is used to get phi dates from document """

    x = time.time()
    logger.info("[Medical-Insights] Extraction of PHI and Document Type is started...")
    phi_and_doc_type_extractor = PHIAndDocTypeExtractor()
    patient_information = await phi_and_doc_type_extractor.get_patient_information(document)
    logger.info(f"[Medical-Insights] Extraction of PHI and Document Type is completed in {time.time() - x} seconds.")
    return patient_information


def get_patient_information_handler(document):
    _loop = asyncio.new_event_loop()
    x = _loop.run_until_complete(get_patient_information(document))
    return x


async def get_encounters(data):
    """ This method is used to get phi dates from document """

    x = time.time()
    logger.info("[Medical-Insights] Encounters Extraction is started...")
    encounters_extractor = EncountersExtractor()
    encounter_events = await encounters_extractor.get_encounters(data)
    logger.info(f"[Medical-Insights] Encounters Extraction is completed in {time.time() - x} seconds.")
    return encounter_events


def get_encounters_handler(data):
    _loop = asyncio.new_event_loop()
    x = _loop.run_until_complete(get_encounters(data))
    return x


def format_output(document_wise_response):
    encounters = []
    patient_names = []
    dob_list = []
    for document_resp in document_wise_response:
        encounters.extend(document_resp['encounters'])
        document_resp.pop('encounters')

        patient_names.append(document_resp['patient_information']['patient_name'])
        document_resp['patient_information'].pop('patient_name')

        dob_list.append(document_resp['patient_information']['date_of_birth'])
        document_resp['patient_information'].pop('date_of_birth')
        document_resp['phi_dates'] = document_resp.pop('patient_information')

    encounters = sorted(encounters, key=lambda e: parse_date(e['date']))

    patient_name = ""
    if len(patient_names) > 0:
        patient_names.sort(key=len)
        patient_name = patient_names[-1]

    dob = ""
    if len(dob_list) > 0:
        dob = sorted(dob_list)[0]

    resp_obj = {
        "patient_information": {
            "patient_name": patient_name,
            "date_of_birth": dob
        },
        "encounters": encounters,
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
    for document in text_result:
        task = []
        with futures.ThreadPoolExecutor(os.cpu_count() - 1) as executor:
            task.append(executor.submit(get_summary_handler, data=document['page_wise_text']))
            task.append(executor.submit(get_entities_handler, data=document['page_wise_text']))
            task.append(executor.submit(get_encounters_handler, data=document))
            task.append(
                executor.submit(get_patient_information_handler, document=os.path.join(project_path, document['name'])))

        extracted_outputs = {'name': os.path.basename(document['name'])}
        results = futures.wait(task)
        for x in results.done:
            extracted_outputs.update(x.result())
        document_wise_response.append(extracted_outputs)
    res = format_output(document_wise_response)
    return res
