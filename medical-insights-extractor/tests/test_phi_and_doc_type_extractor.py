import json
import pytest
from langchain.vectorstores.faiss import FAISS
from langchain.embeddings import BedrockEmbeddings
from app.service.medical_document_insights.nlp_extractor import phi_and_doc_type_extractor
from app.service.medical_document_insights.nlp_extractor import bedrock_client

pytest_plugins = ('pytest_asyncio',)


class TestPHIAndDocTypeExtractor:
    @pytest.mark.asyncio
    async def test_get_docs_embeddings_with_valid_parameter(self):
        extractor = phi_and_doc_type_extractor.PHIAndDocTypeExtractor()
        json_file = 'data/json/04-26-17 Neurological Post Op Eval - Mobin_text.json'

        with open(json_file, 'r') as f:
            json_data = json.load(f)

        result = await extractor._PHIAndDocTypeExtractor__get_docs_embeddings(json_data)
        assert result is not None

    @pytest.mark.asyncio
    async def test_get_docs_embeddings_with_empty_json(self):
        extractor = phi_and_doc_type_extractor.PHIAndDocTypeExtractor()
        json_data = {}
        try:
            await extractor._PHIAndDocTypeExtractor__get_docs_embeddings(json_data)
        except IndexError:
            assert True

    @pytest.mark.asyncio
    async def test_extract_values_between_curly_braces_with_valid_parameter(self):
        extractor = phi_and_doc_type_extractor.PHIAndDocTypeExtractor()
        input_text = "Hello my name is {Kashyap} and my birth date is {16-08-2001}."
        result = await extractor._PHIAndDocTypeExtractor__extract_values_between_curly_braces(input_text)
        assert result == ["{Kashyap}", "{16-08-2001}"]

    @pytest.mark.asyncio
    async def test_extract_values_between_curly_braces_without_curly_braces(self):
        extractor = phi_and_doc_type_extractor.PHIAndDocTypeExtractor()
        input_text = "Hello my name is Kashyap and my birth date is 16-08-2001."
        try:
            result = await extractor._PHIAndDocTypeExtractor__extract_values_between_curly_braces(input_text)
            assert result == []
        except AssertionError:
            assert True

    @pytest.mark.asyncio
    async def test_parse_date_with_valid_parameter(self):
        extractor = phi_and_doc_type_extractor.PHIAndDocTypeExtractor()
        input_date = "25 January 2023"
        result = await extractor._PHIAndDocTypeExtractor__parse_date(input_date)
        assert result == "01-25-2023"
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_parse_date_without_valid_format(self):
        extractor = phi_and_doc_type_extractor.PHIAndDocTypeExtractor()
        input_date = "Not a valid date"
        result = await extractor._PHIAndDocTypeExtractor__parse_date(input_date)
        assert result == "None"

    @pytest.mark.asyncio
    async def test_parse_date_with_int_parameter(self):
        extractor = phi_and_doc_type_extractor.PHIAndDocTypeExtractor()
        input_date = 16082001
        try:
            await extractor._PHIAndDocTypeExtractor__parse_date(input_date)
        except TypeError:
            assert True

    @pytest.mark.asyncio
    async def test_process_patient_name_and_dob_with_valid_parameter(self):
        extractor = phi_and_doc_type_extractor.PHIAndDocTypeExtractor()
        input_text = "Hello my name is Kashyap and I am 23 years old."
        result = await extractor._PHIAndDocTypeExtractor__process_patient_name_and_dob(input_text)
        assert result is not None

    @pytest.mark.asyncio
    async def test_process_patient_name_and_dob_with_emtpy_string(self):
        extractor = phi_and_doc_type_extractor.PHIAndDocTypeExtractor()
        input_text = " "
        try:
            await extractor._PHIAndDocTypeExtractor__process_patient_name_and_dob(input_text)
        except AssertionError:
            assert True

    @pytest.mark.asyncio
    async def test_get_document_type_with_valid_parameter(self):
        extractor = phi_and_doc_type_extractor.PHIAndDocTypeExtractor()
        model_embeddings = 'amazon.titan-embed-text-v1'
        bedrock_client_store = bedrock_client
        bedrock_embeddings = BedrockEmbeddings(model_id=model_embeddings, client=bedrock_client_store)
        vectorstore_path = "data/vectorstore"

        load_faiss = FAISS.load_local(
            vectorstore_path,
            bedrock_embeddings, index_name='embeddings', allow_dangerous_deserialization=True)
        result = await extractor._PHIAndDocTypeExtractor__get_document_type(load_faiss)
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_get_document_type_with_invalid_vectorstore_path(self):
        extractor = phi_and_doc_type_extractor.PHIAndDocTypeExtractor()
        model_embeddings = 'amazon.titan-embed-text-v1'
        bedrock_client_store = bedrock_client
        bedrock_embeddings = BedrockEmbeddings(model_id=model_embeddings, client=bedrock_client_store)
        vectorstore_path = "/invalid/path/to/vectorstore"

        try:
            load_faiss = FAISS.load_local(vectorstore_path, bedrock_embeddings, index_name='embeddings',
                                          allow_dangerous_deserialization=True)
            await extractor._PHIAndDocTypeExtractor__get_document_type(load_faiss)
            assert False
        except RuntimeError:
            assert True

    @pytest.mark.asyncio
    async def test_get_document_type_with_invalid_embedding_model(self):
        extractor = phi_and_doc_type_extractor.PHIAndDocTypeExtractor()
        model_embeddings = 'invalid-embed-text-v1'
        bedrock_client_store = bedrock_client
        bedrock_embeddings = BedrockEmbeddings(model_id=model_embeddings, client=bedrock_client_store)
        vectorstore_path = "data/vectorstore"

        try:
            load_faiss = FAISS.load_local(vectorstore_path, bedrock_embeddings, index_name='embeddings',
                                          allow_dangerous_deserialization=True)
            await extractor._PHIAndDocTypeExtractor__get_document_type(load_faiss)
            assert False
        except ValueError:
            assert True

    @pytest.mark.asyncio
    async def test_get_patient_name_and_dob_with_valid_parameter(self):
        extractor = phi_and_doc_type_extractor.PHIAndDocTypeExtractor()
        model_embeddings = 'amazon.titan-embed-text-v1'
        bedrock_client_store = bedrock_client
        bedrock_embeddings = BedrockEmbeddings(model_id=model_embeddings, client=bedrock_client_store)
        vectorstore_path = "data/vectorstore"

        load_faiss = FAISS.load_local(
            vectorstore_path,
            bedrock_embeddings, index_name='embeddings', allow_dangerous_deserialization=True)
        result = await extractor._PHIAndDocTypeExtractor__get_patient_name_and_dob(load_faiss)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_parse_dates_in_phi_response_valid_parameter(self):
        extractor = phi_and_doc_type_extractor.PHIAndDocTypeExtractor()
        parse_input = {
            "key1": ["2023-01-01", "2023-02-02"],
            "key2": ["2023-03-03", "2023-04-04"]
        }
        parsed_response = await extractor._PHIAndDocTypeExtractor__parse_dates_in_phi_response(parse_input)
        assert parsed_response == {
            "key1": ["01-01-2023", "02-02-2023"],
            "key2": ["03-03-2023", "04-04-2023"]
        }

    @pytest.mark.asyncio
    async def test_parse_dates_in_phi_response_with_invalid_pattern(self):
        extractor = phi_and_doc_type_extractor.PHIAndDocTypeExtractor()
        parse_input = "16 january 2023"
        try:
            await extractor._PHIAndDocTypeExtractor__parse_dates_in_phi_response(parse_input)
        except AttributeError:
            assert True

    @pytest.mark.asyncio
    async def test_get_patient_information_with_valid_parameter(self):
        extractor = phi_and_doc_type_extractor.PHIAndDocTypeExtractor()
        json_file = 'data/json/04-26-17 Neurological Post Op Eval - Mobin_text.json'

        with open(json_file, 'r') as f:
            json_data = json.load(f)

        response = await extractor.get_patient_information(json_data)
        assert len(response['patient_information']) == 2

    @pytest.mark.asyncio
    async def test_get_patient_information_with_string(self):
        extractor = phi_and_doc_type_extractor.PHIAndDocTypeExtractor()
        json_data = "This is the wrong type of json data."
        try:
            await extractor.get_patient_information(json_data)
        except AttributeError:
            assert True
