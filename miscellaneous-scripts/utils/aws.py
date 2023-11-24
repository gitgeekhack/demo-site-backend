import os
import shutil
import zipfile
import boto3

AWS_PROFILE = "pareit-dev"
AWS_DEFAULT_REGION = "us-east-2"
BUCKET_NAME = 'pareit-dev-datalabeling-anno-hash'  # s3 bucket name

os.environ['AWS_PROFILE'] = AWS_PROFILE
os.environ['AWS_DEFAULT_REGION'] = AWS_DEFAULT_REGION

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')

bucket = s3.Bucket(BUCKET_NAME)

BUCKET_STORE_DIR = ''
SSE_KEY_PATH = '/home/nirav/Nirav/PareIT_keys/s3_sse_key.bin'

SSE_KEY = open(SSE_KEY_PATH, "rb")
KEY = SSE_KEY.read()


def download_split_xml(doc_name):
    for objects in bucket.objects.filter(Prefix=doc_name):
        if 'Split_Turn' in objects.key and ('.recreated' in objects.key or '.zip' in objects.key):
            save_path = os.path.join(BUCKET_STORE_DIR, objects.key)

            download_file(objects.key, save_path)

            with zipfile.ZipFile(save_path, "r") as zip_ref:
                zip_ref.extractall(os.path.splitext(save_path)[0])

            xml_save_path = os.path.join(os.path.splitext(save_path)[0], 'annotations.xml')
            return xml_save_path


def download_file(key, save_path):
    with open(save_path, 'wb') as f:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=key, SSECustomerKey=KEY,
                                        SSECustomerAlgorithm='AES256')
        f.write(response['Body'].read())
