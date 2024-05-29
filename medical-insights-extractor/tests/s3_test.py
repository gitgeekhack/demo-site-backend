import os
import shutil
import pytest
from app.common.s3_utils import S3Utils

from botocore.exceptions import ClientError

pytest_plugins = ('pytest_asyncio',)

target_path = "data/data_s3_utils/target"


class TestS3Utils:
    @pytest.mark.asyncio
    async def test_download_object_with_valid_parameters(self):
        os.mkdir(target_path)
        bucket = "medical-insights-extractor-ds"
        key = "sample-data/sample1/request/operative_report.pdf"
        download_path = "data/data_s3_utils/target/operative_report.pdf"
        encrypted_key = eval(os.environ["S3_ENCRYPTION_KEY"])

        s3 = S3Utils()
        await s3.download_object(bucket, key, download_path, encrypted_key)
        assert sum(len(files) for _, _, files in os.walk(target_path)) == 1
        if os.path.exists(target_path):
            shutil.rmtree(target_path)

    @pytest.mark.asyncio
    async def test_download_object_with_invalid_encryption_key(self):
        os.mkdir(target_path)
        bucket = "medical-insights-extractor-ds"
        key = "sample-data/sample1/request/operative_report.pdf"
        download_path = "data/data_s3_utils/target/operative_report.pdf"
        encrypted_key = "wrong-encrypted-key"

        s3 = S3Utils()
        try:
            await s3.download_object(bucket, key, download_path, encrypted_key)
        except ClientError:
            assert True
        if os.path.exists(target_path):
            shutil.rmtree(target_path)
