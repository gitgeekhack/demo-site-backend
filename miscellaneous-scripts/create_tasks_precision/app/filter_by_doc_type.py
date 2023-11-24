import re
import aiofiles
import traceback
import glob2
import os
import pydash
from aws import download_split_xml
import xml.etree.ElementTree as ET
from concurrent import futures
import asyncio
import pandas as pd
from tqdm import tqdm


BUCKET_STORE_DIR = ''
# required_doc_types = ['Anesthesia']
required_doc_types = None
SPLIT_LABEL = 'SPLIT'
UNSUCCESSFUL_FILE_PATH = 'unsuccess.txt'


def escape_name(file):
    return re.sub(r'/', '_', file, flags=re.MULTILINE)


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
                if child_node.tag == 'box' and child_node.attrib['label'] == SPLIT_LABEL:
                    doc_type = await __get_id_and_doc_type(child_node)
                    return doc_type


async def filter_xmls_long_process(file):
    try:
        parent_name = file.split('/', 1)[0]
        all_anno_xmls = glob2.glob(os.path.join(BUCKET_STORE_DIR, parent_name) + '/**/*.xml')
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
                return [parent_name, doc_type, page_start, page_end, file]
        else:
            return [parent_name, doc_type, page_start, page_end, file]

    except Exception as e:
        async with aiofiles.open(UNSUCCESSFUL_FILE_PATH, 'a') as f:
            await f.write(file + '\n')
        print('%s -> %s' % (e, traceback.format_exc()))


def filter_xmls_process_handler(file):
    _loop = asyncio.new_event_loop()
    x = _loop.run_until_complete(filter_xmls_long_process(file))
    return x


async def filter(xml_files):
    task = []
    print("Filtering annotations by document types...")
    with tqdm(total=len(xml_files)) as pbar:
        with futures.ProcessPoolExecutor(os.cpu_count()-1) as executor:
            for file in xml_files:
                new_future = executor.submit(filter_xmls_process_handler, file=file)
                new_future.add_done_callback(lambda x: pbar.update())
                task.append(new_future)

    result = futures.wait(task)
    df = pd.DataFrame(columns=['parent_doc', 'doc_type', 'page_start', 'page_end', 'filepath', 'pages'])
    for x in result.done:
        if x.result():
            row = x.result()
            row.append(int(row[3])-int(row[2])+1)
            df.loc[len(df)] = row
    df.to_csv('filtered_subsections.csv', index=False)

