import requests
import urllib


CVAT_PROTO = 'http'
CVAT_DOMAIN = '192.168.12.85:8080'
CVAT_USER = 'user'
CVAT_MAIL = ''
CVAT_PASS = 'user'
CVAT_IMPORT_FORMAT = 'CVAT 1.1'


def login():
    try:
        url = f'{CVAT_PROTO}://{CVAT_DOMAIN}/api/v1/auth/login'
        payload = {'username': CVAT_USER, 'email': CVAT_MAIL, 'password': CVAT_PASS}
        response = requests.post(url, json=payload)
        result = response.json()
        return result['key']
    except KeyError:
        print('Unable to login into CVAT')
        return None


def get_projects_dict(token):
    url = f'{CVAT_PROTO}://{CVAT_DOMAIN}/api/v1/projects?page_size=50&without_tasks=true'
    response = requests.get(url, headers={'Authorization': f'Token {token}'})
    result = response.json()
    target_keys = ['id', 'name']
    projects = list(map(lambda r: {key: r[key] for key in target_keys}, result['results']))
    project_list = {}
    for i in projects:
        project_list[i['name']] = i['id']
    return project_list


async def create_task(token, task_name, project_name, doc_type):
    try:
        url = f'{CVAT_PROTO}://{CVAT_DOMAIN}/api/v1/tasks'
        payload = {"name": task_name, "labels": [], "project_id": project_name, "subset": doc_type}
        response = requests.post(url, json=payload, headers={'Authorization': f'Token {token}'})
        result = response.json()
        target_keys = ['id', 'name', 'project_id', 'created_date', 'updated_date']
        task = {key: result[key] for key in target_keys}
        return task
    except (KeyError, TypeError):
        print('Unable to create CVAT Task')
        return None


async def upload_images(token, task, files):
    try:
        url = f'{CVAT_PROTO}://{CVAT_DOMAIN}/api/v1/tasks/{task["id"]}/data'
        payload = {"image_quality": 70, "use_zip_chunks": True, "use_cache": True}
        res = requests.post(url, files=files, headers={'Authorization': f'Token {token}'}, data=payload)
        return res.json()
    except TypeError:
        print('Unable to Upload images to task')
        return None


async def upload_annotation(token, task, annotation_file_path):
    upload_url = f'{CVAT_PROTO}://{CVAT_DOMAIN}/api/v1/tasks/{task["id"]}/' \
                 f'annotations?format={urllib.parse.quote(CVAT_IMPORT_FORMAT)}'
    annotation_file = open(annotation_file_path, 'r')
    files = {'annotation_file': ('annotations.xml', annotation_file, 'application/xml', {'Expires': '0'})}
    while True:
        response = requests.put(upload_url, headers={'Authorization': f'Token {token}'}, files=files)
        if response.status_code != 202:
            break
    annotation_file.close()

    if response.status_code != 200 and response.status_code != 201 and response.status_code != 202:
        print('Got response error!', response.status_code, response.content)
