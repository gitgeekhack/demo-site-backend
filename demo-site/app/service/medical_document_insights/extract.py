import io
import json
import os
import shutil
import time

from app.service.helper.text_extractor import PDFTextExtractor
from app.service.medical_document_insights.nlp_extractor.dates_extractor import BedrockDatesExtractor
from app.service.medical_document_insights.nlp_extractor.encounter_dates_extractor import BedrockEncounterDatesExtractor
from app.service.medical_document_insights.nlp_extractor.entity_extractor import ComprehendMedicalExtractor

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

from app.service.medical_document_insights.nlp_extractor.summarizer import LanguageModelWrapper
from app.constant import USER_DATA_PATH


class DocumentInsightExtractor:

    def __init__(self, document):
        self.document = document

    def extract(self):
        if not isinstance(self.document, io.BytesIO):
            file_content_bytesio = io.BytesIO(self.document.file.read())
        else:
            file_content_bytesio = self.document

        input_ = os.path.join(USER_DATA_PATH, 'medical_insights_poc')
        if not os.path.exists(input_):
            os.mkdir(input_)
        pdf_files_directory = os.path.join(input_, 'pdf_files')
        if not os.path.exists(pdf_files_directory):
            os.mkdir(pdf_files_directory)
        input_dir = os.path.join(pdf_files_directory, self.document.filename)
        with open(input_dir, "wb+") as pdf_file:
            pdf_file.write(file_content_bytesio.getvalue())
        pdf_name = input_dir.split("/")[-1].split(".")[0]
        output_dir = "medical_insights_poc"

        result = dict()
        result['document'] = self.document.filename
        pdf_extractor = PDFTextExtractor(input_dir, output_dir)
        pdf_extractor.extract_and_save_text()
        json_dir = "medical_insights_poc/json_save"
        with open(f'{json_dir}/{pdf_name}_text.json', 'r') as file:
            data = json.loads(file.read())

        raw_text = "".join(data.values())
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=10000, chunk_overlap=200
        )
        texts = text_splitter.split_text(raw_text)
        docs = [Document(page_content=t) for t in texts]

        language_model = LanguageModelWrapper()
        summary = language_model.generate_summary(docs)
        result['summary'] = summary

        extractor = ComprehendMedicalExtractor()
        entities = extractor.pagewise_entity_extractor(data)
        result['entities'] = entities

        dates_extractor = BedrockDatesExtractor()
        date_result = dates_extractor.generate_response(docs)
        result['PHI_dates'] = date_result

        encounter_dates = BedrockEncounterDatesExtractor()
        enc_result = encounter_dates.generate_response(docs)
        result['document_origanizer'] = enc_result

        return result
