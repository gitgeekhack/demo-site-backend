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


async def get_medical_insights(document):
    """ This method is used to get the medical insights from the document """

    result = dict()

    pdf_name = os.path.basename(document)
    result['name'] = pdf_name

    page_wise_text = await extract_pdf_text(document)

    task = []
    with futures.ProcessPoolExecutor(os.cpu_count() - 1) as executor:
        task.append(executor.submit(get_summary_handler, data=page_wise_text))
        task.append(executor.submit(get_entities_handler, data=page_wise_text))
        task.append(executor.submit(get_encounters_handler, data=page_wise_text))
        task.append(executor.submit(get_patient_information_handler, document=document))

    results = futures.wait(task)
    for x in results.done:
        result.update(x.result())

    return result
