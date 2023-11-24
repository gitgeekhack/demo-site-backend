import glob
import extract_analysis_output
import os
import boto3
from tqdm import tqdm

os.environ['AWS_PROFILE'] = "pareit-staging"
os.environ['AWS_DEFAULT_REGION'] = "us-east-2"

BUCKET_NAME = f"{os.environ['AWS_PROFILE']}-nationalbi"
SAVE_PATH = "S3 Folder/"

s3_client = boto3.client('s3')


class ExtractJson:

    def __init__(self, req_ids):
        for req_id in tqdm(req_ids):
            s3 = boto3.client('s3')
            bucket_name = f"{os.environ['AWS_PROFILE']}-nationalbi"
            folder_prefix = req_id
            contents = s3.list_objects_v2(
                Bucket=bucket_name,
                Prefix=folder_prefix
            )['Contents']
            for objects in contents:
                # files.append(objects['Key'])
                file_path = objects['Key']
                if not os.path.exists(f"{SAVE_PATH}{'/'.join(file_path.split('/')[:-1])}"):
                    os.makedirs(f"{SAVE_PATH}{'/'.join(file_path.split('/')[:-1])}")

                with open(f"{SAVE_PATH}{file_path}", 'wb') as f:
                    response = s3_client.get_object(Bucket=BUCKET_NAME, Key=file_path)
                    f.write(response['Body'].read())
        self.file_paths = self.__find_json()

    def __find_json(self):
        files = glob.glob(os.path.join(os.getcwd(), 'S3 Folder/**/entity-extraction.json'), recursive=True)
        return files

    def make_csv(self):
        entity = extract_analysis_output.MakeCsv()
        entity.extract(self.file_paths)
