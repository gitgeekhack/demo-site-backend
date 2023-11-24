import os
import pandas

import json_extractor

os.environ['AWS_PROFILE'] = "pareit-staging"
os.environ['AWS_DEFAULT_REGION'] = "us-east-2"

req_id = pandas.read_csv('accuracy_testing_2023_07_18_11_52_37_am.csv')

extractor = json_extractor.ExtractJson(req_id['request_ids'].to_list())
extractor.make_csv()
