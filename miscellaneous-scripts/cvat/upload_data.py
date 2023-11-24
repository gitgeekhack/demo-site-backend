import os
import glob
import time
from cvat_utils import upload_images, login, create_task, upload_annotation


async def get_data_with_files_from_local(file_keys):
    files = {}
    file_index = 0
    for file_path in file_keys:
        local_file = await get_file_from_path(file_path)
        file_key = "client_files[{}]".format(file_index)
        files[file_key] = local_file
        file_index += 1
    return files


async def get_file_from_path(file_path):
    file_name = os.path.basename(file_path)
    return file_name, open(file_path, "rb")


async def upload_images_and_annotation(images_folder, task_name, proj_name, annotation_file_path):
    images = glob.glob(os.path.join(images_folder, '*.jpg'))
    files = await get_data_with_files_from_local(images)

    token = await login()
    task = await create_task(token, task_name, proj_name)
    response = await upload_images(token, task, files)
    if response:
        time.sleep(0.5)
        await upload_annotation(token, task, annotation_file_path)
