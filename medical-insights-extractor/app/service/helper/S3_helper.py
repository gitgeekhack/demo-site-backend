import io
import boto3


class S3HelperAsync:
    def __init__(self):
        self.client = boto3.client('s3')

    async def upload_object(self, bucket, key, file_object):
        """
        The Upload Object method uploads required file object to the given s3 bucket
        :param bucket: The s3 bucket name
        :param key: the key is the s3 folder path
        :param file_object: A binary file object.
        :return: url <str>: returns the s3 url of the uploaded object
        """
        file_object = io.BytesIO(file_object)
        self.client.upload_fileobj(file_object, bucket, key, ExtraArgs={"ServerSideEncryption": "AES256"})
