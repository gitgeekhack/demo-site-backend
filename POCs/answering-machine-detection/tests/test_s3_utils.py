import os
import io
import pytest
os.chdir("../")
from app.common.s3_utils import S3Utils

from botocore.exceptions import ClientError, ParamValidationError

encrypted_key = eval(os.getenv("S3_ENCRYPTION_KEY"))

pytest_plugins = ('pytest_asyncio',)

class TestS3Utils:
    @pytest.mark.asyncio
    async def test_download_object_with_valid_parameters(self, tmp_path):
        s3 = S3Utils()
        target_path = tmp_path / "target"
        target_path.mkdir(parents=True, exist_ok=True)

        bucket = "ds-answering-machine-detection"
        key = "sample-data/answering_machine.ulaw"
        download_path = str(target_path / "answering_machine.ulaw")

        await s3.download_object(bucket, key, download_path, encrypted_key)
        assert sum(len(files) for _, _, files in os.walk(target_path)) == 1

    @pytest.mark.asyncio
    async def test_download_object_with_invalid_key(self, tmp_path):
        s3 = S3Utils()
        target_path = tmp_path / "target"
        target_path.mkdir(parents=True, exist_ok=True)

        bucket = "ds-answering-machine-detection"
        key = "wrong-key"
        download_path = str(target_path / "answering_machine.mp3")

        try:
            await s3.download_object(bucket, key, download_path, encrypted_key)
        except ClientError:
            assert True

    @pytest.mark.asyncio
    async def test_download_object_with_invalid_download_path(self, tmp_path):
        s3 = S3Utils()
        target_path = tmp_path / "target"
        target_path.mkdir(parents=True, exist_ok=True)

        bucket = "ds-answering-machine-detection"
        key = "sample-data/answering_machine.ulaw"
        download_path = str(target_path / "pdf" / "answering_machine.ulaw")

        try:
            await s3.download_object(bucket, key, download_path, encrypted_key)
        except FileNotFoundError:
            assert True

    @pytest.mark.asyncio
    async def test_download_object_with_invalid_bucket(self, tmp_path):
        s3 = S3Utils()
        target_path = tmp_path / "target"
        target_path.mkdir(parents=True, exist_ok=True)

        bucket = "wrong-bucket-name"
        key = "sample-data/answering_machine.ulaw"
        download_path = str(target_path / "answering_machine.ulaw")

        try:
            await s3.download_object(bucket, key, download_path, encrypted_key)
        except ClientError:
            assert True

    @pytest.mark.asyncio
    async def test_upload_object_with_valid_parameters(self):
        s3 = S3Utils()
        bytes_buffer = io.BytesIO()
        file_path = "tests/static_data/answering_machine.ulaw"
        with open(file_path, mode='rb') as file:
            bytes_buffer.write(file.read())

        bucket = "ds-answering-machine-detection"
        key = "tests-data/answering_machine.ulaw"
        file_object = bytes_buffer.getvalue()

        await s3.upload_object(bucket, key, file_object, encrypted_key)
        if await s3.check_s3_path_exists(bucket, key):
            assert True
            await s3.delete_object(bucket, key)
        else:
            assert False

    @pytest.mark.asyncio
    async def test_upload_object_with_invalid_bucket(self):
        s3 = S3Utils()
        bytes_buffer = io.BytesIO()
        file_path = "tests/static_data/answering_machine.ulaw"
        with open(file_path, mode='rb') as file:
            bytes_buffer.write(file.read())

        bucket = "wrong-bucket-name"
        key = "tests-data/answering_machine.ulaw"
        file_object = bytes_buffer.getvalue()

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
        file_path = "tests/static_data/answering_machine.ulaw"
        with open(file_path, mode='rb') as file:
            bytes_buffer.write(file.read())

        bucket = "ds-answering-machine-detection"
        key = "tests-data/answering_machine.ulaw"
        file_object = bytes_buffer.getvalue()

        await s3.upload_object(bucket, key, file_object, encrypted_key)

        await s3.delete_object(bucket, key)
        if not await s3.check_s3_path_exists(bucket, key):
            assert True
        else:
            assert False

    @pytest.mark.asyncio
    async def test_delete_object_with_invalid_key(self):
        s3 = S3Utils()

        bucket = "ds-answering-machine-detection"
        key = "invalid-key"
        try:
            await s3.delete_object(bucket, key)
        except ParamValidationError:
            assert True

    @pytest.mark.asyncio
    async def test_delete_object_with_invalid_bucket(self):
        s3 = S3Utils()

        bucket = "invalid-bucket-name"
        key = "sample-data/answering_machine.ulaw"
        try:
            await s3.delete_object(bucket, key)
        except ClientError:
            assert True

    @pytest.mark.asyncio
    async def test_check_s3_path_exists_with_valid_parameters(self):
        s3 = S3Utils()

        bucket = "ds-answering-machine-detection"
        key = "sample-data/answering_machine.ulaw"
        if await s3.check_s3_path_exists(bucket, key):
            assert True
        else:
            assert False

    @pytest.mark.asyncio
    async def test_check_s3_path_exists_with_invalid_key(self):
        s3 = S3Utils()

        bucket = "ds-answering-machine-detection"
        key = "invalid-key"
        if not await s3.check_s3_path_exists(bucket, key):
            assert True
        else:
            assert False

    @pytest.mark.asyncio
    async def test_check_s3_path_exists_with_invalid_bucket(self):
        s3 = S3Utils()

        bucket = "invalid-bucket-name"
        key = "sample-data/answering_machine.ulaw"
        try:
            await s3.check_s3_path_exists(bucket, key)
        except ClientError:
            assert True