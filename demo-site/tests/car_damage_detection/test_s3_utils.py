import os
import io
import pytest
from botocore.exceptions import ClientError

os.chdir('../../')
from app.common.s3_utils import S3Utils

pytest_plugins = ('pytest_asyncio',)


class TestS3Utils:
    @pytest.mark.asyncio
    async def test_upload_object_with_valid_parameters(self):
        s3 = S3Utils()
        bytes_buffer = io.BytesIO()
        file_path = "tests/data/image/Nissan-frontside-view.jpg"
        with open(file_path, mode='rb') as file:
            bytes_buffer.write(file.read())
        bucket = "ds-car-damage-identification"
        key = "tests-data/Nissan-frontside-view.jpg"
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
        file_path = "tests/data/image/Nissan-frontside-view.jpg"
        with open(file_path, mode='rb') as file:
            bytes_buffer.write(file.read())
        bucket = "ds-car-damage-identification"
        key = "tests-data/Nissan-frontside-view.jpg"
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
        file_path = "tests/data/image/Nissan-frontside-view.jpg"
        with open(file_path, mode='rb') as file:
            bytes_buffer.write(file.read())
        bucket = "ds-car-damage-identification"
        key = "tests-data/Nissan-frontside-view.jpg"
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