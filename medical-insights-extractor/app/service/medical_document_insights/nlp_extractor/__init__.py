import boto3
from botocore.config import Config
from app.constant import AWS

bedrock_client = boto3.client(service_name='bedrock-runtime', region_name=AWS.BotoClient.AWS_DEFAULT_REGION,
                              config=Config(read_timeout=AWS.BotoClient.read_timeout,
                                            connect_timeout=AWS.BotoClient.connect_timeout))
