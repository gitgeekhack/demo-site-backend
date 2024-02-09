import os
from concurrent.futures import ThreadPoolExecutor

import requests
from tqdm import tqdm

url = "http://av4amd.avatar.tech:8081/api/v1/amd"
ext = '.wav'

target = './data/validate/'


def get_files(dir_name):
    list_of_file = os.listdir(dir_name)
    complete_file_list = list()
    for file in list_of_file:
        complete_path = os.path.join(dir_name, file)
        if os.path.isdir(complete_path):
            complete_file_list = complete_file_list + get_files(complete_path)
        else:
            complete_file_list.append(complete_path)

    return complete_file_list


files = get_files(target)


def send_request(file_path):
    name = file_path.split('\\')[-1]
    actual = file_path.split('\\')[-2].split('/')[-1]
    try:
        files = [
            ('file', (name, open(file_path, 'rb'), 'audio/wav'))
        ]
        headers = {
            'Authorization': 'Bearer D85718A11A3B6'
        }
        response = requests.request("POST", url, files=files, headers=headers)
        response = response.json()
        if response['is_human_answer']:
            predict = 'HA'
        else:
            predict = 'NON_HA'
        return [name, actual, predict, '', 'success']

    except Exception as e:
        return [name, actual, '', str(e), 'failed']


def run(targets):
    with ThreadPoolExecutor(16) as executor:
        results = list(tqdm(executor.map(send_request, targets), total=len(targets), desc="sending requests"))
    return results


out = run(files)

import pandas as pd

df = pd.DataFrame(
    columns=['File', 'actual', 'predicted', 'Error', 'Request Status'],
    data=out)
df['is_correct'] = df.apply(lambda x: x['actual'] == x['predicted'], axis=1)
df.to_csv('server_validate_test.csv', index=False)