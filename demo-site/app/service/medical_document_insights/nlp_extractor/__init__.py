import boto3
from botocore.config import Config
from app.constant import BotoClient

bedrock_client = boto3.client(service_name='bedrock-runtime', region_name=BotoClient.AWS_DEFAULT_REGION, config=Config(BotoClient.read_timeout))