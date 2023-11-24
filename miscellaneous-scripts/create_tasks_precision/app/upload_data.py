import os
import glob
import time
from cvat_utils import upload_images, login, create_task, upload_annotation, get_projects_dict


class CreateTasksUploadData:
    def __init__(self):
        self.token = login()
        self.project_dict = get_projects_dict(self.token)

    async def __get_data_with_files_from_local(self, file_keys):
        files = {}
        file_index = 0
        for file_path in file_keys:
            local_file = await self.__get_file_from_path(file_path)
            file_key = "client_files[{}]".format(file_index)
            files[file_key] = local_file
            file_index += 1
        return files

    async def __get_file_from_path(self, file_path):
        file_name = os.path.basename(file_path)
        return file_name, open(file_path, "rb")

    async def upload_images_and_annotation(self, images, task_name, proj_name, annotation_file_path, doc_type):
        files = await self.__get_data_with_files_from_local(images)

        task = await create_task(self.token, task_name, self.project_dict[proj_name], doc_type)
        response = await upload_images(self.token, task, files)
        if response:
            time.sleep(0.5)
            await upload_annotation(self.token, task, annotation_file_path)
            return task['id']