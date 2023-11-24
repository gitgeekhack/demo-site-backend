import asyncio
import os
from aws import download_split_xml
import glob2
import pydash
import re
import xml.etree.ElementTree as ET
from task_helper import process_task_creation
import traceback
import aiofiles
from concurrent import futures
from tqdm import tqdm

BUCKET_STORE_DIR = '/home/nirav/Nirav/S3MountRawData/precision_test'
project = 'Named Entities'
UNSUCCESSFUL_FILE_PATH = 'unsuccess.txt'


def escape_name(file):
    return re.sub(r'/', '_', file, flags=re.MULTILINE)


anno_xmls = glob2.glob(BUCKET_STORE_DIR + '/**/*.xml')
project_find_key = f'/{escape_name(project)}-'
anno_xmls = pydash.filter_(anno_xmls, lambda x: x.find(project_find_key) != -1)
anno_xml_names = pydash.map_(anno_xmls, lambda x: x.replace(BUCKET_STORE_DIR, '').strip('/'))


required_doc_types = ['Hosp Records', 'Hospital Records', 'Imaging Record', 'Emergency', 'Admission_Sheet', 'Discharge_Summary']
# required_doc_types = ['Orthropaedic']


async def __get_id_and_doc_type(node):
    for x in node:
        if x.attrib['name'] == 'doc_type':
            return x.text


async def get_doc_type(split_xml_path, page_start):
    tree = ET.parse(split_xml_path)
    root_node = tree.getroot()

    image_nodes = root_node.findall('image')
    for img in image_nodes:
        if int(img.attrib['id']) == page_start - 1:
            for child_node in img:
                if child_node.tag == 'box' and child_node.attrib['label'] == 'SPLIT':
                    doc_type = await __get_id_and_doc_type(child_node)
                    return doc_type


async def task_creation_long_process(file):
    try:
        parent_name = file.split('/', 1)[0]
        all_anno_xmls = glob2.glob(os.path.join(BUCKET_STORE_DIR, parent_name) + '/*.xml')
        project_find_key = f'/{escape_name("Split/Turn")}-'
        split_anno_xmls = pydash.filter_(all_anno_xmls, lambda x: x.find(project_find_key) != -1)

        if not split_anno_xmls:
            split_xml_path = download_split_xml(parent_name)
        else:
            split_xml_path = split_anno_xmls[0]

        page_start = file.split('/')[1].split('-')[0]
        page_end = file.split('/')[1].split('-')[1]
        doc_type = await get_doc_type(split_xml_path, int(page_start))
        if required_doc_types:
            if doc_type in required_doc_types:
                await process_task_creation(parent_name, doc_type, page_start, page_end,
                                            os.path.join(BUCKET_STORE_DIR, file))
        else:
            await process_task_creation(parent_name, doc_type, page_start, page_end,
                                        os.path.join(BUCKET_STORE_DIR, file))
    except Exception as e:
        async with aiofiles.open(UNSUCCESSFUL_FILE_PATH, 'a') as f:
            await f.write(file + '\n')
        print('%s -> %s' % (e, traceback.format_exc()))


def task_creation_process_handler(file):
    _loop = asyncio.new_event_loop()
    x = _loop.run_until_complete(task_creation_long_process(file))
    return x


async def main():
    task = []

    with futures.ProcessPoolExecutor(os.cpu_count() - 1) as executor:
        for file in tqdm(anno_xml_names):
            new_future = executor.submit(task_creation_process_handler, file=file)
            task.append(new_future)

    result = futures.wait(task)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
