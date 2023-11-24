from app.cvat_utils import login, get_tasks_custom, get_project_dict, delete_task
from app.aws_helper import save_to_s3
from app.constant import CVAT_PROTO, CVAT_DOMAIN, CVAT_DATASET_FORMAT
from app.retrieve_task_information import RetrieveTaskDetails
from app.database.common_queries import insert_annotations, update_task_details
from app.database.conn_mgr import get_db_connection, close_conn
from app.logging_helper import logger
import requests
import pydash
import re
import os
import traceback
import urllib
import aiofiles


store_dir = './export_dir'
retrieve_task_details = RetrieveTaskDetails()
SUCCESSFUL_FILE_PATH = 'success.txt'
UNSUCCESSFUL_FILE_PATH = 'unsuccess.txt'


class ExportTasks:
    def __init__(self):
        self.token = login()
        self.project_dict = get_project_dict(self.token)

    async def escape_name(self, file):
        return re.sub(r'/', '_', file, flags=re.MULTILINE)

    async def get_task_key(self, project, task_id, ext=None):
        return await self.escape_name(f'{project}-{task_id}{"." + ext if ext is not None else ""}')

    async def __get_parent_doc_info(self, task_name):
        doc_info = os.path.splitext(task_name)
        split_info = os.path.splitext(doc_info[0])
        parent_doc_name = split_info[0]+doc_info[1]
        split_range_info = split_info[1].strip('.')
        return parent_doc_name, split_range_info

    async def export_task(self, task):
        download_url = f'{CVAT_PROTO}://{CVAT_DOMAIN}/api/v1/tasks/{task["id"]}/annotations?format={urllib.parse.quote(CVAT_DATASET_FORMAT)}&action=download'
        parent_doc_name, page_split_range = await self.__get_parent_doc_info(task['name'])
        save_path = os.path.join(store_dir, parent_doc_name, page_split_range)
        os.makedirs(save_path, exist_ok=True)

        filepath = str.join(os.sep, [save_path,
                                           await self.get_task_key(self.project_dict[task['project_id']], task['id'], 'zip')])

        while True:
            response = requests.get(download_url, headers={'Authorization': f'Token {self.token}'})
            if response.status_code != 202:
                break
        if response.status_code == 404:
            print('Invalid status - 404. Response:', response.content)
            print('Requested url:', download_url)
            raise Exception('Invalid result')

        with open(filepath, 'wb') as fw:
            fw.write(response.content)

        return filepath, parent_doc_name, page_split_range

    async def get_tasks_by_status_and_project(self, statuses=None, projects=None, reviewers=None):
        """
        Get tasks information and filter them by status and project
        """
        tasks = get_tasks_custom(self.token)

        if statuses:
            tasks = pydash.filter_(tasks, lambda t: t['status'] in statuses)
        if projects:
            tasks = pydash.filter_(tasks, lambda t: self.project_dict[t['project_id']] in projects)
        if reviewers:
            tasks = pydash.filter_(tasks, lambda t: \
                t['segments'][0]['jobs'][0]['reviewer']['username'] in reviewers \
                    if t['segments'][0]['jobs'][0]['reviewer'] is not None else False)

        for task in tasks:
            task['project'] = self.project_dict[task['project_id']]
        return tasks

    async def export_task_long_process(self, task):
        try:
            filepath, parent_doc_name, page_split_range = await self.export_task(task)
            s3_url = await save_to_s3(filepath, parent_doc_name, page_split_range)

            conn = get_db_connection()
            try:
                task_details = retrieve_task_details.get_task_details(task['id'])
                insert_annotations(conn, task_details)
                is_updated = update_task_details(conn, task_details, s3_url)
                conn.commit()
            except Exception as e:
                logger.warning('Database insertion failed!!!')
                logger.warning('%s -> %s' % (e, traceback.format_exc()))
            finally:
                close_conn(conn)

            # delete_task(self.token, task['id'])
            async with aiofiles.open(SUCCESSFUL_FILE_PATH, 'a') as f:
                await f.write(task['name'] + '\n')
        except Exception as e:
            async with aiofiles.open(UNSUCCESSFUL_FILE_PATH, 'a') as f:
                await f.write(task['name'] + '\n')
            logger.error('%s -> %s' % (e, traceback.format_exc()))
