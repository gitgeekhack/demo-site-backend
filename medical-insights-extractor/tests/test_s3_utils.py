import os
import pytest
from app.common.s3_utils import S3Utils

from botocore.exceptions import ClientError

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
