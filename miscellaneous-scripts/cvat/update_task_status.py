import asyncio
import aiofiles
import traceback
from concurrent import futures
from logging_helper import logger
import os
import requests
import pydash
from tqdm import tqdm

CVAT_PROTO = 'http'
CVAT_DOMAIN = ''
CVAT_USER = ''
CVAT_PASS = ''
CVAT_MAIL = ''

CURRENT_STATUS = 'validation'
TARGET_PROJECT = 'Named Entities'
TARGET_STATUS = 'completed'

UNSUCCESSFUL_FILE_PATH = 'unsuccess.txt'


async def login():
    try:
        url = f'{CVAT_PROTO}://{CVAT_DOMAIN}/api/v1/auth/login'
        payload = {'username': CVAT_USER, 'email': CVAT_MAIL, 'password': CVAT_PASS}
        response = requests.post(url, json=payload)
        result = response.json()
        return result['key']
    except KeyError as e:
        print('Unable to login into CVAT', e)
        return None


async def get_project_list_simple(token):
    url = f'{CVAT_PROTO}://{CVAT_DOMAIN}/api/v1/projects?page_size=50&without_tasks=true'
    response = requests.get(url, headers={'Authorization': f'Token {token}'})
    result = response.json()
    target_keys = ['id', 'name']
    projects = list(map(lambda r: {key: r[key] for key in target_keys}, result['results']))
    return projects


async def get_project_dict(token):
    projects = await get_project_list_simple(token)
    projects_dict = pydash.from_pairs(pydash.map_(projects, lambda x: [x['id'], x['name']]))
    return projects_dict


async def get_tasks_custom(token):
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


async def get_tasks_by_status_and_project(token, status=None, projects=None):
    """
    Get tasks information and filter them by status and project
    """
    if type(projects) == str:
        projects = [projects]
    tasks = await get_tasks_custom(token)
    project_dict = await get_project_dict(token)

    if status:
        tasks = pydash.filter_(tasks, lambda t: t['status'] == status)
    if projects:
        for project in projects:
            tasks = pydash.filter_(tasks, lambda t: project_dict[t['project_id']] == project)

    for task in tasks:
        task['project'] = project_dict[task['project_id']]
    return tasks


async def update_job_model(token, job_id, model):
    url = f'{CVAT_PROTO}://{CVAT_DOMAIN}/api/v1/jobs/{job_id}'
    payload = model
    response = requests.patch(url, json=payload, headers={'Authorization': f'Token {token}'})
    if response.status_code != 200 and response.status_code != 201:
        print('Got response error!', response.status_code, response.content)
    result = response.json()
    project = result
    return project


async def update_task_model(token, task_id, model):
    url = f'{CVAT_PROTO}://{CVAT_DOMAIN}/api/v1/tasks/{task_id}'
    payload = model
    response = requests.patch(url, json=payload, headers={'Authorization': f'Token {token}'})
    if response.status_code != 200 and response.status_code != 201:
        print('Got response error!', response.status_code, response.content)
    result = response.json()
    project = result
    return project


async def update_task_status_long_process(token, task):
    try:
        task_id = task['id']
        job_id = task['segments'][0]['jobs'][0]['id']
        task_update_model = {'status': TARGET_STATUS}
        await update_task_model(token, task_id, task_update_model)

        job_update_model = {'status': TARGET_STATUS}
        await update_job_model(token, job_id, job_update_model)
    except Exception as e:
        async with aiofiles.open(UNSUCCESSFUL_FILE_PATH, 'a') as f:
            await f.write(task['name'] + '\n')
        logger.error('%s -> %s' % (e, traceback.format_exc()))


def update_task_status_process_handler(token, task):
    _loop = asyncio.new_event_loop()
    x = _loop.run_until_complete(update_task_status_long_process(token, task))
    return x


async def main():
    token = await login()
    tasks = await get_tasks_by_status_and_project(token, status=CURRENT_STATUS, projects=TARGET_PROJECT)
    print(f'Updating task status from "{CURRENT_STATUS}" --> "{TARGET_STATUS}"')
    print('No of tasks to update status:', len(tasks))

    confirmation = input("Want to proceed? (yes/no)")
    if confirmation == 'yes':
        task_pool = []
        with tqdm(total=len(tasks)) as pbar:
            with futures.ProcessPoolExecutor(os.cpu_count() - 1) as executor:
                for task in tasks:
                    new_future = executor.submit(update_task_status_process_handler, token=token, task=task)
                    new_future.add_done_callback(lambda x: pbar.update())
                    task_pool.append(new_future)
        futures.wait(task_pool)
    else:
        exit(0)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
