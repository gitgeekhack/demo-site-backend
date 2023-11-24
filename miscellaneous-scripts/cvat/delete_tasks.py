import time
import requests
import pydash
from tqdm import tqdm
import urllib

CVAT_PROTO = 'http'
CVAT_DOMAIN = '192.168.12.85:8080'
CVAT_USER = 'user'
CVAT_PASS = 'user'
CVAT_MAIL = ''


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


def get_tasks_custom(token):
    """
    Retrieve tasks information from CVAT thru custom endpoint
    """
    url = f'{CVAT_PROTO}://{CVAT_DOMAIN}/api/v1/taskscustom/list'
    response = requests.get(url, headers={'Authorization': f'Token {token}'})
    # TODO Error handling
    try:
        result = response.json()
    except Exception as ex:
        print('Exception:', str(ex))
        raise ex
    if 'error' in result and result['error'] is not None:
        # raise Exception(result['error'])
        pass
    if 'count' not in result or result['count'] == 0:
        return []
    target_keys = ['id', 'name', 'status', 'project_id', 'created_date', 'updated_date', 'segments', 'subset']
    tasks = list(map(lambda r: {key: r[key] for key in target_keys}, result['results']))
    return tasks


def get_tasks(token, assignee=None, reviewer=None, status=None, project=None, name=None):
    """
    Get tasks information and filter them by different properties
    """
    projects = get_project_dict(token)
    tasks = get_tasks_custom(token)

    if assignee is not None:
        print('Filterint tasks by "assignee"')
        tasks = pydash.filter_(tasks, lambda t: \
            t['segments'][0]['jobs'][0]['assignee']['username'] == assignee \
            if t['segments'][0]['jobs'][0]['assignee'] is not None else False)
    if reviewer is not None:
        print('Filterint tasks by "reviewer"')
        tasks = pydash.filter_(tasks, lambda t: \
            t['segments'][0]['jobs'][0]['reviewer']['username'] == reviewer \
            if t['segments'][0]['jobs'][0]['reviewer'] is not None else False)
    if status is not None:
        print('Filterint tasks by "status"')
        tasks = pydash.filter_(tasks, lambda t: t['status'] == status)
    if project is not None:
        print('Filterint tasks by "project"')
        tasks = pydash.filter_(tasks, lambda t: projects[t['project_id']] == project)
    if name is not None:
        print('Filterint tasks by "name"')
        tasks = pydash.filter_(tasks, lambda t: t['name'] == name)

    for task in tasks:
        task['project'] = projects[task['project_id']]
    return tasks


def paginate(func, token, **kwargs):
    page = 1
    results = []
    # print(f'Paginating "{func.__name__}"..')
    while True:
        # print(f'Page {page} for "{func.__name__}"')
        # TODO Rewrite to fetch 'next':None status
        result = func(token, page=page, **kwargs)
        # print(result)
        if result is None or len(result) == 0:
            break
        results.append(result)
        page += 1
    # print('Pages end')
    return pydash.flatten(results)


def get_tasks_page(token, page=1, assignee=None, reviewer=None, status=None, project=None, name=None):
    url = f'{CVAT_PROTO}://{CVAT_DOMAIN}/api/v1/tasks?page_size=50&page={page}'
    if assignee is not None:
        url = url + f'&assignee={urllib.parse.quote(assignee)}'
    if reviewer is not None:
        url = url + f'&reviewer={urllib.parse.quote(reviewer)}'
    if status is not None:
        url = url + f'&jobStatus={urllib.parse.quote(status)}'
    if project is not None:
        url = url + f'&projectName={urllib.parse.quote(project)}'
    if name is not None:
        url = url + f'&name={urllib.parse.quote(name)}'
    response = requests.get(url, headers={'Authorization': f'Token {token}'})
    # TODO Error handling
    result = response.json()
    if 'count' not in result or result['count'] == 0:
        return []
    target_keys = ['id', 'name', 'status', 'project_id', 'created_date', 'updated_date', 'segments', 'subset']
    tasks = list(map(lambda r: {key: r[key] for key in target_keys}, result['results']))
    return tasks


def get_tasks_w_pagination(token, assignee=None, reviewer=None, status=None, project=None, name=None):
    projects = get_project_dict(token)
    tasks = paginate(get_tasks_page, token,
                     assignee=assignee, reviewer=reviewer, status=status, project=project, name=name)
    for task in tasks:
        task['project'] = projects[task['project_id']]
    return tasks



token = login()
print('Login successful, token:', token)
tasks = get_tasks(token, project='Split/Turn')
for task in tqdm(tasks):
    try:
        task_id = task['id']
        url = f'{CVAT_PROTO}://{CVAT_DOMAIN}/api/v1/tasks/{task_id}'
        response = requests.delete(url, headers={'Authorization': f'Token {token}'})
    except Exception as e:
        time.sleep(2)
        print(e)
