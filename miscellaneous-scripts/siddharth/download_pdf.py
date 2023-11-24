import boto3
import os

# Create an S3 client
os.environ['AWS_PROFILE'] = "pareit-dev"
os.environ['AWS_DEFAULT_REGION'] = "us-east-2"

s3_client = boto3.client('s3')

# Specify the bucket name and object key
bucket_name = 'pareit-dev-datalabeling-anno-hash'
object_key = 'https://pareit-dev-datalabeling-anno.s3.us-east-2.amazonaws.com/8524e0daefe38f505571c6827a45aba2b9c69562_hash.pdf/8524e0daefe38f505571c6827a45aba2b9c69562_hash.pdf'.replace(
    'https://pareit-dev-datalabeling-anno.s3.us-east-2.amazonaws.com/', '')

# Specify the local file path where the object will be downloaded
local_file_path = 'https://pareit-dev-datalabeling-anno.s3.us-east-2.amazonaws.com/8524e0daefe38f505571c6827a45aba2b9c69562_hash.pdf/8524e0daefe38f505571c6827a45aba2b9c69562_hash.pdf'.replace(
    'https://pareit-dev-datalabeling-anno.s3.us-east-2.amazonaws.com/', './test/')

# Download the file from S3
SSE_KEY = open("s3_sse_key.bin", "rb")
KEY = SSE_KEY.read()
extra_args = {
    'SSECustomerAlgorithm': 'AES256',
    'SSECustomerKey': KEY
}
s3_client.download_file(bucket_name, object_key, local_file_path, ExtraArgs=extra_args)

print(f"File downloaded successfully to: {local_file_path}")
