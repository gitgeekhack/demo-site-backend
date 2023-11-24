import os
import shutil
import base64
import zipfile
import boto3

os.environ['AWS_PROFILE'] = 'pareit-dev'
os.environ['AWS_REGION'] = 'us-east-2'
AWS_REGION = os.getenv('AWS_REGION', 'us-east-2')
BUCKET_NAME = 'pareit-dev-datalabeling-anno-hash'  # s3 bucket name

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')

bucket = s3.Bucket(BUCKET_NAME)

BUCKET_STORE_DIR = './precision_test'
SSE_KEY_PATH = './s3_sse_key.bin'

SSE_KEY = open(SSE_KEY_PATH, "rb")
KEY = SSE_KEY.read()


async def save_to_s3(filepath, parent_doc_name, page_split_range):
    s3_save_path_folder = os.path.join(parent_doc_name, page_split_range)
    await save_recreated_file(s3_save_path_folder)

    with open(filepath, 'rb') as f:
        file_obj = f.read()
    s3_key = os.path.join(s3_save_path_folder, os.path.basename(filepath))
    s3_client.put_object(Body=file_obj, Bucket=BUCKET_NAME, Key=s3_key, SSECustomerKey=KEY,
                         SSECustomerAlgorithm='AES256')

    splits = s3_client.meta.endpoint_url.split('//')
    info = splits[1].split('.')
    info.insert(1, AWS_REGION)
    s3_file_url = '%s//%s.%s/%s' % (splits[0], BUCKET_NAME, '.'.join(info), s3_key)
    return s3_file_url.replace(' ', '+')


async def save_recreated_file(s3_save_path_folder):
    object_keys = [obj.key for obj in bucket.objects.filter(Prefix=s3_save_path_folder)]
    is_recreated_present = False
    for key in object_keys:
        if 'Named Entities' in key and key.endswith('.recreated'):
            is_recreated_present = True
            break

    if not is_recreated_present:
        for key in object_keys:
            if 'Named Entities' in key and key.endswith('.zip'):
                recreated_key = os.path.splitext(key)[0] + '.recreated'

                response = s3_client.get_object(Bucket=BUCKET_NAME, Key=key, SSECustomerKey=KEY,
                                                SSECustomerAlgorithm='AES256')
                file_obj = response['Body'].read()
                s3_client.put_object(Body=file_obj, Bucket=BUCKET_NAME, Key=recreated_key, SSECustomerKey=KEY,
                                     SSECustomerAlgorithm='AES256')
