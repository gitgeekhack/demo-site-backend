import os
import io
import pytest
from app.common.s3_utils import S3Utils
from app.service.medical_document_insights.nlp_extractor.document_qna import DocumentQnA


pytest_plugins = ('pytest_asyncio',)


class TestDocumentQnA:
    @pytest.mark.asyncio
    async def test_data_formatter_with_raw_text(self):
        dq = DocumentQnA()
        txt_file_path = "data/text/sample.txt"
        with open(txt_file_path, 'r') as file:
            raw_text = file.read()
        assert len(await dq._DocumentQnA__data_formatter(raw_text)) == 2

    @pytest.mark.asyncio
    async def test_data_formatter_with_empty_raw_text(self):
        dq = DocumentQnA()
        raw_text = ''
        assert len(await dq._DocumentQnA__data_formatter(raw_text)) == 0

    @pytest.mark.asyncio
    async def test_get_query_response_with_valid_path(self, tmp_path):
        s3 = S3Utils()
        file_bytes_buffer = io.BytesIO()
        textract_bytes_buffer = io.BytesIO()
        file_path = "data/pdf/sample_patient_report.pdf"
        textract_response_path = "data/json/sample_textract_response.json"
        with open(file_path, mode='rb') as file:
            file_bytes_buffer.write(file.read())
        with open(textract_response_path, mode='rb') as file:
            textract_bytes_buffer.write(file.read())

        bucket = "ds-medical-insights-extractor"
        file_key = str(tmp_path / "tests-data/sample/request/sample_patient_report.pdf")
        textract_response_key = str(tmp_path / "tests-data/sample/textract_response/sample_textract_response.json")
        file_object = file_bytes_buffer.getvalue()
        textract_response_object = textract_bytes_buffer.getvalue()
        encrypted_key = eval(os.environ["S3_ENCRYPTION_KEY"])

        await s3.upload_object(bucket, file_key, file_object, encrypted_key)
        await s3.upload_object(bucket, textract_response_key, textract_response_object, encrypted_key)

        dq = DocumentQnA()
        project_path = str(tmp_path / "tests-data/sample/request")
        query = "What is patient's name ?"
        assert (await dq.get_query_response(query, project_path))['result'] == " The patient's name is Maya Parmar."

        objects_to_delete = s3.client.list_objects_v2(Bucket=bucket, Prefix=str(tmp_path))
        if 'Contents' in objects_to_delete:
            delete_keys = {'Objects': [{'Key': obj['Key']} for obj in objects_to_delete['Contents']]}
            s3.client.delete_objects(Bucket=bucket, Delete=delete_keys)

    @pytest.mark.asyncio
    async def test_get_query_response_with_empty_query(self, tmp_path):
        s3 = S3Utils()
        file_bytes_buffer = io.BytesIO()
        textract_bytes_buffer = io.BytesIO()
        file_path = "data/pdf/sample_patient_report.pdf"
        textract_response_path = "data/json/sample_textract_response.json"
        with open(file_path, mode='rb') as file:
            file_bytes_buffer.write(file.read())
        with open(textract_response_path, mode='rb') as file:
            textract_bytes_buffer.write(file.read())

        bucket = "ds-medical-insights-extractor"
        file_key = str(tmp_path / "tests-data/sample/request/sample_patient_report.pdf")
        textract_response_key = str(tmp_path / "tests-data/sample/textract_response/sample_textract_response.json")
        file_object = file_bytes_buffer.getvalue()
        textract_response_object = textract_bytes_buffer.getvalue()
        encrypted_key = eval(os.environ["S3_ENCRYPTION_KEY"])

        await s3.upload_object(bucket, file_key, file_object, encrypted_key)
        await s3.upload_object(bucket, textract_response_key, textract_response_object, encrypted_key)

        dq = DocumentQnA()
        project_path = str(tmp_path / "tests-data/sample/request")
        query = ""
        try:
            assert (await dq.get_query_response(query, project_path))['result'] == " The patient's name is Maya Parmar."
        except ValueError:
            assert True
            objects_to_delete = s3.client.list_objects_v2(Bucket=bucket, Prefix=str(tmp_path))
            if 'Contents' in objects_to_delete:
                delete_keys = {'Objects': [{'Key': obj['Key']} for obj in objects_to_delete['Contents']]}
                s3.client.delete_objects(Bucket=bucket, Delete=delete_keys)

    @pytest.mark.asyncio
    async def test_get_query_response_with_invalid_path(self, tmp_path):
        dq = DocumentQnA()
        project_path = str(tmp_path / "tests-data/sample/request")
        query = "What is patient's name ?"
        try:
            assert (await dq.get_query_response(query, project_path))['result'] == " The patient's name is Maya Parmar."
        except TypeError:
            assert True
