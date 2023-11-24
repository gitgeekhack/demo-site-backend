import os

import boto3

AWS_PROFILE = "pareit-dev"
AWS_DEFAULT_REGION = "us-east-2"
BUCKET_NAME = 'pareit-dev-datalabeling-anno-hash'  # s3 bucket name
FILE_PATH = "/home/ubuntu/git/pareit-miscellaneous-scripts/stats/all_s3_objects_08122022.txt"  # path to the txt file to save s3 objects path

os.environ['AWS_PROFILE'] = AWS_PROFILE
os.environ['AWS_DEFAULT_REGION'] = AWS_DEFAULT_REGION

s3 = boto3.resource('s3')
bucket = s3.Bucket(BUCKET_NAME)

with open(FILE_PATH, 'w') as fp:
    for obj in bucket.objects.all():
        fp.write("%s\n" % obj.key)
