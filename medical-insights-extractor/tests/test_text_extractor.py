import pytest
import shutil
from app.common.s3_utils import S3Utils
from app.service.helper.text_extractor import get_textract_response, convert_pdf_to_text, extract_pdf_text

import fitz

pytest_plugins = ('pytest_asyncio',)


class TestTextExtractor:
    @pytest.mark.asyncio
    async def test_get_textract_response_with_image(self):
        image_path = "data/image/image-with-text.png"
        page_text = await get_textract_response(image_path)
        assert page_text.strip() == "This is some longer text that will"

    @pytest.mark.asyncio
    async def test_get_textract_response_with_pdf(self):
        pdf_path = "data/pdf/This is a Dummy PDF.pdf"
        page_text = await get_textract_response(pdf_path)
        assert page_text.strip() == "This is a Dummy PDF"

    @pytest.mark.asyncio
    async def test_get_textract_response_with_invalid_path(self):
        pdf_path = "./data/data_text_extractor/image-text.png"
        try:
            page_text = await get_textract_response(pdf_path)
        except FileNotFoundError:
            assert True

    @pytest.mark.asyncio
    async def test_convert_pdf_to_text_with_valid_pdf(self, tmp_path):
        image_output_dir = tmp_path
        page_no = 0
        doc_path = "data/pdf/This is a Dummy PDF.pdf"
        text = await convert_pdf_to_text(image_output_dir, page_no, doc_path)
        assert text == {f"page_{page_no + 1}": "This is a Dummy PDF "}

    @pytest.mark.asyncio
    async def test_convert_pdf_to_text_with_image(self, tmp_path):
        image_output_dir = tmp_path
        page_no = 0
        doc_path = "data/image/image-with-text.png"
        text = await convert_pdf_to_text(image_output_dir, page_no, doc_path)
        assert text == {f"page_{page_no + 1}": "This is some longer text that will "}

    @pytest.mark.asyncio
    async def test_convert_pdf_to_text_with_invalid_output_path(self):
        image_output_dir = "target"
        page_no = 0
        doc_path = "data/pdf/This is a Dummy PDF.pdf"
        try:
            text = await convert_pdf_to_text(image_output_dir, page_no, doc_path)
        except RuntimeError:
            assert True

    @pytest.mark.asyncio
    async def test_extract_pdf_text_with_valid_pdf(self, tmp_path):
        s3 = S3Utils()
        bucket = "medical-insights-extractor-ds"

        file_path = tmp_path / "This is a Dummy PDF.pdf"
        local_path = "data/pdf/This is a Dummy PDF.pdf"
        shutil.copy(local_path, file_path)
        page_wise_text = await extract_pdf_text(file_path)
        assert page_wise_text == {"page_1": "This is a Dummy PDF "}
        objects_to_delete = s3.client.list_objects_v2(Bucket=bucket, Prefix=str(tmp_path))
        if 'Contents' in objects_to_delete:
            delete_keys = {'Objects': [{'Key': obj['Key']} for obj in objects_to_delete['Contents']]}
            s3.client.delete_objects(Bucket=bucket, Delete=delete_keys)

    @pytest.mark.asyncio
    async def test_extract_pdf_text_with_image(self, tmp_path):
        s3 = S3Utils()
        bucket = "medical-insights-extractor-ds"

        file_path = tmp_path / "image-with-text.png"
        local_path = "data/image/image-with-text.png"
        shutil.copy(local_path, file_path)
        page_wise_text = await extract_pdf_text(file_path)
        assert page_wise_text == {"page_1": "This is some longer text that will "}
        objects_to_delete = s3.client.list_objects_v2(Bucket=bucket, Prefix=str(tmp_path))
        if 'Contents' in objects_to_delete:
            delete_keys = {'Objects': [{'Key': obj['Key']} for obj in objects_to_delete['Contents']]}
            s3.client.delete_objects(Bucket=bucket, Delete=delete_keys)

    @pytest.mark.asyncio
    async def test_extract_pdf_text_with_invalid_path(self, tmp_path):
        file_path = tmp_path / "image-with-text.png"
        try:
            page_wise_text = await extract_pdf_text(file_path)
        except fitz.fitz.FileNotFoundError:
            assert True
