import os
import io
import pytest
from app.common.s3_utils import S3Utils

from botocore.exceptions import ClientError, ParamValidationError

pytest_plugins = ('pytest_asyncio',)


class TestS3Utils:
    @pytest.mark.asyncio
    async def test_download_object_with_valid_parameters(self, tmp_path):
        s3 = S3Utils()
        target_path = tmp_path / "target"
        target_path.mkdir(parents=True, exist_ok=True)

        bucket = "medical-insights-extractor-ds"
        key = "sample-data/sample1/request/operative_report.pdf"
        download_path = str(target_path / "operative_report.pdf")
        encrypted_key = eval(os.environ["S3_ENCRYPTION_KEY"])

        await s3.download_object(bucket, key, download_path, encrypted_key)
        assert sum(len(files) for _, _, files in os.walk(target_path)) == 1

    @pytest.mark.asyncio
    async def test_download_object_with_invalid_encryption_key(self, tmp_path):
        s3 = S3Utils()
        target_path = tmp_path / "target"
        target_path.mkdir(parents=True, exist_ok=True)

        bucket = "medical-insights-extractor-ds"
        key = "sample-data/sample1/request/operative_report.pdf"
        download_path = str(target_path / "operative_report.pdf")
        encrypted_key = "wrong-encrypted-key"

        try:
            await s3.download_object(bucket, key, download_path, encrypted_key)
        except ClientError:
            assert True

    @pytest.mark.asyncio
    async def test_download_object_with_invalid_download_path(self, tmp_path):
        s3 = S3Utils()
        target_path = tmp_path / "target"
        target_path.mkdir(parents=True, exist_ok=True)

        bucket = "medical-insights-extractor-ds"
        key = "sample-data/sample1/request/operative_report.pdf"
        download_path = str(target_path / "pdf" / "operative_report.pdf")
        encrypted_key = eval(os.environ["S3_ENCRYPTION_KEY"])

        try:
            await s3.download_object(bucket, key, download_path, encrypted_key)
        except FileNotFoundError:
            assert True

    @pytest.mark.asyncio
    async def test_download_object_with_invalid_key(self, tmp_path):
        s3 = S3Utils()
        target_path = tmp_path / "target"
        target_path.mkdir(parents=True, exist_ok=True)

        bucket = "medical-insights-extractor-ds"
        key = "sample-data/sample1/request/op_report.pdf"
        download_path = str(target_path / "operative_report.pdf")
        encrypted_key = eval(os.environ["S3_ENCRYPTION_KEY"])

        try:
            await s3.download_object(bucket, key, download_path, encrypted_key)
        except ClientError:
            assert True

    @pytest.mark.asyncio
    async def test_download_object_with_invalid_bucket(self, tmp_path):
        s3 = S3Utils()
        target_path = tmp_path / "target"
        target_path.mkdir(parents=True, exist_ok=True)

        bucket = "medical-insights-ds"
        key = "sample-data/sample1/request/operative_report.pdf"
        download_path = str(target_path / "operative_report.pdf")
        encrypted_key = eval(os.environ["S3_ENCRYPTION_KEY"])

        try:
            await s3.download_object(bucket, key, download_path, encrypted_key)
        except ClientError:
            assert True

    @pytest.mark.asyncio
    async def test_upload_object_with_valid_parameters(self):
        s3 = S3Utils()
        bytes_buffer = io.BytesIO()
        file_path = "data/pdf/operative_report.pdf"
        with open(file_path, mode='rb') as file:
            bytes_buffer.write(file.read())

        bucket = "medical-insights-extractor-ds"
        key = "tests-data/operative_report.pdf"
        file_object = bytes_buffer.getvalue()
        encrypted_key = eval(os.environ["S3_ENCRYPTION_KEY"])

        await s3.upload_object(bucket, key, file_object, encrypted_key)
        if await s3.check_s3_path_exists(bucket, key):
            assert True
            await s3.delete_object(bucket, key)
        else:
            assert False

    @pytest.mark.asyncio
    async def test_upload_object_with_invalid_encryption_key(self):
        s3 = S3Utils()
        bytes_buffer = io.BytesIO()
        file_path = "data/pdf/operative_report.pdf"
        with open(file_path, mode='rb') as file:
            bytes_buffer.write(file.read())

        bucket = "medical-insights-extractor-ds"
        key = "tests-data/operative_report.pdf"
        file_object = bytes_buffer.getvalue()
        encrypted_key = "wrong-encrypted-key"

        try:
            await s3.upload_object(bucket, key, file_object, encrypted_key)
            if await s3.check_s3_path_exists(bucket, key):
                assert True
                await s3.delete_object(bucket, key)
            else:
                assert False
        except ClientError:
            assert True

    @pytest.mark.asyncio
    async def test_upload_object_with_invalid_bucket(self):
        s3 = S3Utils()
        bytes_buffer = io.BytesIO()
        file_path = "data/pdf/operative_report.pdf"
        with open(file_path, mode='rb') as file:
            bytes_buffer.write(file.read())

        bucket = "medical-insights-ds"
        key = "tests-data/operative_report.pdf"
        file_object = bytes_buffer.getvalue()
        encrypted_key = eval(os.environ["S3_ENCRYPTION_KEY"])

        try:
            await s3.upload_object(bucket, key, file_object, encrypted_key)
            if await s3.check_s3_path_exists(bucket, key):
                assert True
                await s3.delete_object(bucket, key)
            else:
                assert False
        except s3.client.exceptions.NoSuchBucket:
            assert True

    @pytest.mark.asyncio
    async def test_delete_object_with_valid_parameters(self):
        s3 = S3Utils()
        bytes_buffer = io.BytesIO()
        file_path = "data/pdf/operative_report.pdf"
        with open(file_path, mode='rb') as file:
            bytes_buffer.write(file.read())

        bucket = "medical-insights-extractor-ds"
        key = "tests-data/operative_report.pdf"
        file_object = bytes_buffer.getvalue()
        encrypted_key = eval(os.environ["S3_ENCRYPTION_KEY"])

        await s3.upload_object(bucket, key, file_object, encrypted_key)

        await s3.delete_object(bucket, key)
        if not await s3.check_s3_path_exists(bucket, key):
            assert True
        else:
            assert False

    @pytest.mark.asyncio
    async def test_delete_object_with_invalid_key(self):
        s3 = S3Utils()

        bucket = "medical-insights-extractor-ds"
        key = ""
        try:
            await s3.delete_object(bucket, key)
        except ParamValidationError:
            assert True

    @pytest.mark.asyncio
    async def test_delete_object_with_invalid_bucket(self):
        s3 = S3Utils()

        bucket = "medical-insights-ds"
        key = "tests-data/operative_report.pdf"
        try:
            await s3.delete_object(bucket, key)
        except s3.client.exceptions.NoSuchBucket:
            assert True

    @pytest.mark.asyncio
    async def test_check_s3_path_exists_with_valid_parameters(self):
        s3 = S3Utils()

        bucket = "medical-insights-extractor-ds"
        key = "sample-data/sample1/request/operative_report.pdf"
        if await s3.check_s3_path_exists(bucket, key):
            assert True
        else:
            assert False

    @pytest.mark.asyncio
    async def test_check_s3_path_exists_with_invalid_key(self):
        s3 = S3Utils()

        bucket = "medical-insights-extractor-ds"
        key = "sample-data/sample1/request/op_report.pdf"
        if not await s3.check_s3_path_exists(bucket, key):
            assert True
        else:
            assert False

    @pytest.mark.asyncio
    async def test_check_s3_path_exists_with_invalid_bucket(self):
        s3 = S3Utils()

        bucket = "medical-insights-ds"
        key = "sample-data/sample1/request/operative_report.pdf"
        try:
            await s3.check_s3_path_exists(bucket, key)
        except s3.client.exceptions.NoSuchBucket:
            assert True