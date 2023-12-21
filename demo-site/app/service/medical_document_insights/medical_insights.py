import os
import time
import asyncio
import traceback
from concurrent import futures

from app import logger
from app.service.helper.text_extractor import extract_pdf_text
from app.service.medical_document_insights.nlp_extractor.entity_extractor import EntityExtractor
from app.service.medical_document_insights.nlp_extractor.phi_dates_extractor import PHIDatesExtractor
from app.service.medical_document_insights.nlp_extractor.document_summarizer import DocumentSummarizer
from app.service.medical_document_insights.nlp_extractor.encounters_extractor import EncountersExtractor


async def get_summary(data):
    """ This method is used to get document summary """

    x = time.time()
    document_summarizer = DocumentSummarizer()
    summary = await document_summarizer.get_summary(data)
    logger.info(f"Summary is generated in {time.time() - x} seconds.")
    return summary


def get_summary_handler(data):
    _loop = asyncio.new_event_loop()
    x = _loop.run_until_complete(get_summary(data))
    return x


async def get_entities(data):
    """ This method is used to get entities from document """

    x = time.time()
    entity_extractor = EntityExtractor()
    entities = await entity_extractor.get_extracted_entities(data)
    logger.info(f"Entity Extraction is completed in {time.time() - x} seconds.")
    return entities


def get_entities_handler(data):
    _loop = asyncio.new_event_loop()
    x = _loop.run_until_complete(get_entities(data))
    return x


async def get_phi_dates(data):
    """ This method is used to get phi dates from document """

    x = time.time()
    phi_dates_extractor = PHIDatesExtractor()
    phi_dates = await phi_dates_extractor.get_phi_dates(data)
    logger.info(f"PHI Dates Extraction is completed in {time.time() - x} seconds.")
    return phi_dates


def get_phi_handler(data):
    _loop = asyncio.new_event_loop()
    x = _loop.run_until_complete(get_phi_dates(data))
    return x


async def get_encounters(data):
    """ This method is used to get phi dates from document """

    x = time.time()
    encounters_extractor = EncountersExtractor()
    encounter_events = await encounters_extractor.get_encounters(data)
    logger.info(f"Encounters Extraction is completed in {time.time() - x} seconds.")
    return encounter_events


def get_encounters_handler(data):
    _loop = asyncio.new_event_loop()
    x = _loop.run_until_complete(get_encounters(data))
    return x


async def get_medical_insights(document):
    """ This method is used to get the medical insights from the document """

    try:
        result = dict()

        pdf_name = os.path.basename(document)
        output_dir = document.replace(".pdf", "")
        os.makedirs(output_dir, exist_ok=True)
        result['name'] = pdf_name
        page_wise_text = await extract_pdf_text(document, output_dir)

        task = []
        with futures.ProcessPoolExecutor(os.cpu_count() - 1) as executor:
            task.append(executor.submit(get_summary_handler, data=page_wise_text))
            task.append(executor.submit(get_entities_handler, data=page_wise_text))
            task.append(executor.submit(get_phi_handler, data=page_wise_text))
            task.append(executor.submit(get_encounters_handler, data=page_wise_text))

        results = futures.wait(task)

        for x in results.done:
            result.update(x.result())

        return result

    except Exception as e:
        logger.error('%s -> %s' % (e, traceback.format_exc()))
