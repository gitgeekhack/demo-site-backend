import fitz
from app.service.api.v1.same_person_statement import extract_v1
from app.service.helper.pdf_helper import PDFHelper

file = 'app/data/temp/test_data/SAME_PERS_STATEMENT_Sheree Williams 1.pdf'
document_url = 'http://127.0.0.1:8080/download/example/same_person_statement/SAME_PERS_STATEMENT_Sheree Williams 1.pdf'
doc = fitz.open(file, filetype="pdf")

async def test_get_signature_valid():
    obj = extract_v1.SPSDataPointExtractorV1(uuid='89c5de1c-4d25-11ec-8623-d1e221452fcd', document_url=document_url)
    obj.pdf_helper = PDFHelper(doc)
    response = {"is_signed": True}
    x = await obj._SPSDataPointExtractorV1__get_signature()
    assert x == response
