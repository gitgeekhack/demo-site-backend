import boto3
from botocore.config import Config
from app.constant import MedicalInsights

textract_client = boto3.client(service_name='textract', region_name=MedicalInsights.AWS_DEFAULT_REGION, config=Config(MedicalInsights.read_timeout))