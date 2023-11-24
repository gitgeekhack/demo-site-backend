import requests
from app.constant import CVAT_PROTO, CVAT_DOMAIN, CVAT_MAIL, CVAT_PASS, CVAT_USER, CVAT_IMPORT_FORMAT
import urllib
import pydash


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


def get_tasks_custom(token):
    """
    Retrieve tasks information from CVAT through custom endpoint
    """
    url = f'{CVAT_PROTO}://{CVAT_DOMAIN}/api/v1/taskscustom/list'
    response = requests.get(url, headers={'Authorization': f'Token {token}'})
    try:
        result = response.json()
    except Exception as ex:
        print('Exception:', str(ex))
        raise ex
    if 'error' in result and result['error'] is not None:
        raise Exception(result['error'])
    if 'count' not in result or result['count'] == 0:
        return []
    target_keys = ['id', 'name', 'status', 'project_id', 'created_date', 'updated_date', 'segments', 'subset']
    tasks = list(map(lambda r: {key: r[key] for key in target_keys}, result['results']))
    return tasks


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


def delete_task(token, task_id):
    url = f'{CVAT_PROTO}://{CVAT_DOMAIN}/api/v1/tasks/{task_id}'
    response = requests.delete(url, headers={'Authorization': f'Token {token}'})
