import asyncio
import os
import glob2
import pandas as pd
import pydash
import re
from app.task_helper import process_task_creation
from app.filter_update_xml import get_updated_xmls
import traceback
import aiofiles
from concurrent import futures
from app.filter_by_doc_type import filter
from tqdm import tqdm


BUCKET_STORE_DIR = ''
TARGET_PROJECT = 'Named Entities'
SUCCESSFUL_FILE_PATH = 'success.txt'
UNSUCCESSFUL_FILE_PATH = 'unsuccess.txt'


def escape_name(file):
    return re.sub(r'/', '_', file, flags=re.MULTILINE)


all_anno_xmls = glob2.glob(BUCKET_STORE_DIR + '/**/*.xml')
print(f'Total annotations in bucket: {len(all_anno_xmls)}')
project_find_key = f'/{escape_name(TARGET_PROJECT)}-'
anno_xmls = pydash.filter_(all_anno_xmls, lambda x: x.find(project_find_key) != -1)
print(f'Matching project annotations in bucket: {len(anno_xmls)}')
anno_xml_names = pydash.map_(anno_xmls, lambda x: x.replace(BUCKET_STORE_DIR, '').strip('/'))


async def task_creation_long_process(file_info):
    try:
        await process_task_creation(file_info['parent_doc'], file_info['doc_type'], file_info['page_start'],
                                    file_info['page_end'], os.path.join(BUCKET_STORE_DIR, file_info['filepath']))
        async with aiofiles.open(SUCCESSFUL_FILE_PATH, 'a') as f:
            await f.write(file_info[4] + '\n')
    except Exception as e:
        async with aiofiles.open(UNSUCCESSFUL_FILE_PATH, 'a') as f:
            await f.write(file_info[4] + '\n')
        print('%s -> %s' % (e, traceback.format_exc()))


def task_creation_process_handler(file):
    _loop = asyncio.new_event_loop()
    x = _loop.run_until_complete(task_creation_long_process(file))
    return x


async def main():
    task = []
    updated_xmls = await get_updated_xmls(anno_xml_names)
    await filter(updated_xmls)
    # exit(0)
    filtered_updated_xmls = pd.read_csv('filtered_subsections.csv')
    print("Tasks to create:", len(filtered_updated_xmls))

    with tqdm(total=len(filtered_updated_xmls)) as pbar:
        with futures.ProcessPoolExecutor(os.cpu_count()-1) as executor:
            for file in filtered_updated_xmls.iterrows():
                new_future = executor.submit(task_creation_process_handler, file=file[1])
                new_future.add_done_callback(lambda x: pbar.update())
                task.append(new_future)

    result = futures.wait(task)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
