import io
import boto3


class S3Utils:
    def __init__(self):
        self.client = boto3.client(service_name='s3', region_name='ap-south-1')

    async def download_object(self, bucket, key, download_path):

        bytes_buffer = io.BytesIO()
        self.client.download_fileobj(Bucket=bucket, Key=key, Fileobj=bytes_buffer)
        file_object = bytes_buffer.getvalue()

        with open(download_path, 'wb') as file:
            file.write(file_object)

        return True

    async def upload_object(self, bucket, key, file_object, encrypted_key):

        file_object = io.BytesIO(file_object)
        self.client.upload_fileobj(file_object, bucket, key,
                                   ExtraArgs={
                                       "SSECustomerAlgorithm": "AES256",
                                       "SSECustomerKey": encrypted_key
                                   })
        url = f's3://{bucket}/{key}'
        return url

    async def check_s3_path_exists(self, aws_bucket, key):

        response = self.client.list_objects_v2(Bucket=aws_bucket, Prefix=key)
        if 'Contents' not in response or len(response['Contents']) < 1:
            return []
        else:
            return response


s3_utils = S3Utils()
