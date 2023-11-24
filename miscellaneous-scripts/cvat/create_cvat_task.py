import glob
import os
from zipfile import ZipFile
import asyncio

from tqdm import tqdm

from upload_data import upload_images_and_annotation
import shutil


async def process_zip(zip_file, task_name, images_folder):
    annotation_dir = os.path.join(os.path.dirname(zip_file), os.path.basename(zip_file).split('.')[0])
    with ZipFile(zip_file, 'r') as z:
        z.extractall(annotation_dir)

    proj_name = os.path.basename(zip_file).split('.')[0].replace('_', '/').split('-')[0]
    annotation_file_path = os.path.join(annotation_dir, 'annotations.xml')

    await upload_images_and_annotation(images_folder, task_name, proj_name, annotation_file_path)
    shutil.rmtree(annotation_dir, ignore_errors=True)


async def create_cvat_task(images_file, zip_files):
    parent_dir = os.path.dirname(images_file[0])
    with ZipFile(images_file[0], 'r') as z:
        z.extractall(parent_dir)

    sub_folder = os.path.join(parent_dir, 'images')
    images_folder = os.path.join(sub_folder, os.listdir(sub_folder)[0])
    task_name = os.path.basename(os.path.dirname(parent_dir)) + '.' + os.path.basename(parent_dir)

    process_zip_coroutines = [process_zip(zip_file, task_name, images_folder) for zip_file in zip_files]
    await asyncio.gather(*process_zip_coroutines)
    shutil.rmtree(os.path.dirname(images_folder), ignore_errors=True)


async def process_file(dir,file):
    if os.path.isdir(os.path.join(dir, file)):
        images_file = glob.glob(os.path.join(dir, file, '*.gz'))
        zip_files = glob.glob(os.path.join(dir, file, '*.zip'))
        if images_file and zip_files:
            await create_cvat_task(images_file, zip_files)


async def main():
    file_l = []
    try:
        with open("/home/heli/Documents/git/pareIT-internal/upload_files.txt") as file:
            lines = file.readlines()
            lines = [os.path.dirname(line.strip()) for line in lines]
        for path in tqdm(set(lines)):
            files = os.listdir(path)
            process_file_coroutines = [process_file(path,file) for file in files]
            await asyncio.gather(*process_file_coroutines)
            print('Completed')
    except Exception as e:
        print(e)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
