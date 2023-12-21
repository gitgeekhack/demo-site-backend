import time
import traceback

from app import logger
from app.service.medical_document_insights.nlp_extractor.document_qna import DocumentQnA


async def get_query_response(query, document):

    try:
        x = time.time()
        document_qna = DocumentQnA()
        response = await document_qna.get_query_response(query, document)
        logger.info(f"Query response generated in {time.time() - x} seconds.")
        return response

    except Exception as e:
        logger.error('%s -> %s' % (e, traceback.format_exc()))
