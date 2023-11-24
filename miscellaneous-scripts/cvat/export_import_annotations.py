import requests
import pydash
import os
import re
import time
import zipfile
import urllib

CVAT_PROTO = 'http'
CVAT_DOMAIN = '192.168.12.85:8080'
CVAT_USER = 'user'
CVAT_MAIL = ''
CVAT_PASS = 'user'
CVAT_DATASET_FORMAT = 'CVAT for images 1.1'
DOWNLOAD_SLEEP_SEC = 5
CVAT_IMPORT_FORMAT = 'CVAT 1.1'
IMPORT_SLEEP_SEC = 0.5


def login():
    try:
        url = f'{CVAT_PROTO}://{CVAT_DOMAIN}/api/v1/auth/login'
        payload = {'username': CVAT_USER, 'email': CVAT_MAIL, 'password': CVAT_PASS}
        response = requests.post(url, json=payload)
        result = response.json()
        return result['key']
    except KeyError as e:
        print('Unable to login into CVAT',e)
        return None


def get_project_list_simple(token):
    url = f'{CVAT_PROTO}://{CVAT_DOMAIN}/api/v1/projects?page_size=50&without_tasks=true'
    response = requests.get(url, headers={'Authorization': f'Token {token}'})
    result = response.json()
    target_keys = ['id', 'name']
    projects = list(map(lambda r: {key: r[key] for key in target_keys}, result['results']))
    return projects


def get_project_dict(token):
    projects = get_project_list_simple(token)
    projects_dict = pydash.from_pairs(pydash.map_(projects, lambda x: [x['id'], x['name']]))
    return projects_dict


def get_task(token, task_id):
    url = f'{CVAT_PROTO}://{CVAT_DOMAIN}/api/v1/tasks/{task_id}'
    response = requests.get(url, headers={'Authorization': f'Token {token}'})
    # TODO Error handling
    result = response.json()
    project_dict = get_project_dict(token)
    result['project'] = project_dict[result['project_id']]
    return result


def escape_name(file):
    return re.sub(r'/', '_', file, flags=re.MULTILINE)


def get_task_key(task, ext=None):
    return escape_name(f'{task["project"]}-{task["id"]}{"." + ext if ext is not None else ""}')


def export_task(token, task_id, store_dir):
    task = get_task(token, task_id)
    download_url = f'{CVAT_PROTO}://{CVAT_DOMAIN}/api/v1/tasks/{task_id}/annotations?format={urllib.parse.quote(CVAT_DATASET_FORMAT)}&action=download'

    # Prepare
    # export_doc_dir = str.join(os.sep, [store_dir, doc_part_dir(task['name'])])
    data_file_name = str.join(os.sep, [store_dir, get_task_key(task, 'zip')])

    while True:
        response = requests.get(download_url, headers={'Authorization': f'Token {token}'})
        print('Downloading, code', response.status_code)
        if response.status_code != 202:
            break
        time.sleep(DOWNLOAD_SLEEP_SEC)
    if response.status_code == 404:
        print('Invalid status - 404. Response:', response.content)
        print('Requested url:', download_url)
        raise Exception('Invalid result')

    # Export annotation
    with open(data_file_name, 'wb') as fw:
        fw.write(response.content)

    return data_file_name


def import_annotation(token, task_id, anno_file_path):
    annotation_fp = open(anno_file_path, 'r', encoding='utf-8')
    upload_url = f'{CVAT_PROTO}://{CVAT_DOMAIN}/api/v1/tasks/{task_id}/annotations?format={urllib.parse.quote(CVAT_IMPORT_FORMAT)}'

    files = {'annotation_file': ('annotations.xml', annotation_fp, 'application/xml', {'Expires': '0'})}
    while True:
        response = requests.put(upload_url, headers={'Authorization': f'Token {token}'}, files=files)
        print('Importing, code', response.status_code)
        if response.status_code != 202:
            break
        time.sleep(IMPORT_SLEEP_SEC)
        if response.status_code == 404:
            raise 'Invalid result'

    if response.status_code not in [200, 201, 202]:
        print('Got response error!', response.status_code, response.content)
        raise 'Invalid result'

    print('Imported', response.content)
    return True


token = login()

# store_dir = 'task_export/'
#
# print(export_task(token, 501, store_dir))


anno_file_path = 'annotations.xml'

import_annotation(token, 501, anno_file_path)
