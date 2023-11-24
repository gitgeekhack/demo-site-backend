import os
from aws import download_file
import zipfile
from upload_data import CreateTasksUploadData
from retrieve_task_information import RetrieveTaskDetails
from app.database.common_queries import insert_task_details
from app.database.conn_mgr import get_db_connection, close_conn

BUCKET_STORE_DIR = '/home/nirav/Nirav/S3MountRawData/precision_test'


obj = CreateTasksUploadData()
retrieve_task_details = RetrieveTaskDetails()


async def process_task_creation(parent_name, doc_type, page_start, page_end, annotation_file_path):
    images_s3_key = f'{parent_name}/{page_start}-{page_end}/images.gz'
    images_local_arch = os.path.join(BUCKET_STORE_DIR, parent_name, f'{page_start}-{page_end}', 'images.gz')

    if not os.path.exists(images_local_arch):
        download_file(images_s3_key, images_local_arch)

    with zipfile.ZipFile(images_local_arch, 'r') as zip_images:
        extract_path = os.path.join(os.path.dirname(images_local_arch), 'images')
        zip_images.extractall(extract_path)
        zip_iamges_file_names = zip_images.namelist()
        images_sorted = sorted(zip_iamges_file_names, key=lambda x: int(os.path.splitext(x)[0][-4:]))
        zip_images_files = [os.path.join(extract_path, name) for name in images_sorted if
                            name.startswith('images/') and name.endswith('jpg')]

    task_name = os.path.splitext(parent_name)[0] + f'.{page_start}-{page_end}' + os.path.splitext(parent_name)[1]
    task_id = await obj.upload_images_and_annotation(zip_images_files, task_name, 'Named Entities', annotation_file_path, doc_type)

    conn = get_db_connection()
    try:
        task_details = retrieve_task_details.get_task_details(task_id)
        is_inserted = insert_task_details(conn, task_details, parent_name, page_start, page_end)
        # if is_inserted:
        #     print(f'Task: {task_details["TaskName"]} successfully inserted in database.')
    except Exception:
        print('Database insertion failed...')
    finally:
        close_conn(conn)

    print(f'Task: {task_details["TaskName"]} created successfully.')
