import asyncio
import os
import glob2
import pandas as pd
from collections import defaultdict
import pydash
import re
from aws import download_split_xml
import traceback
import aiofiles
import xml.etree.ElementTree as ET
from concurrent import futures
from logging_helper import logger
from tqdm import tqdm


BUCKET_STORE_DIR = ''
TARGET_PROJECT = 'Named Entities'
SUCCESSFUL_FILE_PATH = 'success.txt'
UNSUCCESSFUL_FILE_PATH = 'unsuccess.txt'


def escape_name(project_name):
    return project_name.replace('/', '_')


all_anno_xmls = glob2.glob(BUCKET_STORE_DIR + '/**/*.xml')
print(f'Total annotations files: {len(all_anno_xmls)}')
project_find_key = f'/{escape_name(TARGET_PROJECT)}-'
anno_xmls = pydash.filter_(all_anno_xmls, lambda x: x.find(project_find_key) != -1)
print(f'Matching project annotations files: {len(anno_xmls)}')
anno_xml_names = pydash.map_(anno_xmls, lambda x: x.replace(BUCKET_STORE_DIR, '').strip('/'))


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


async def get_label_counts(file):
    tree = ET.parse(os.path.join(BUCKET_STORE_DIR, file))
    root_node = tree.getroot()
    image_nodes = root_node.findall('image')

    label_counts = defaultdict(int)

    for image in image_nodes:
        for child_node in image:
            if child_node.tag == 'box':
                if len(child_node)==2:
                    sublabels = sorted(child_node, key=lambda x:x.attrib['name'])
                    if sublabels[0].attrib['name'] == 'TokenOrder' and sublabels[0].text in ['singular', 'beginning']:
                        label_counts[sublabels[1].text] += 1
                else:
                    label_counts[child_node.attrib['label']] += 1

    return label_counts


async def get_label_count(file):
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
        doc_type = await get_doc_type(split_xml_path, int(page_start))

        label_counts = await get_label_counts(file)
        label_counts['doc_type'] = doc_type

        async with aiofiles.open(SUCCESSFUL_FILE_PATH, 'a') as f:
            await f.write(file + '\n')
        return label_counts
    except Exception as e:
        async with aiofiles.open(UNSUCCESSFUL_FILE_PATH, 'a') as f:
            await f.write(file + '\n')
        logger.error('%s -> %s' % (e, traceback.format_exc()))


def get_label_count_process_handler(file):
    _loop = asyncio.new_event_loop()
    x = _loop.run_until_complete(get_label_count(file))
    return x


async def main():
    ner_label_counts = defaultdict(dict)
    ner_doc_counts = defaultdict(int)

    tasks = []
    print('Processing files for label counts...')
    with tqdm(total=len(anno_xml_names)) as pbar:
        with futures.ProcessPoolExecutor(os.cpu_count() - 1) as executor:
            for file in anno_xml_names:
                new_future = executor.submit(get_label_count_process_handler, file=file)
                new_future.add_done_callback(lambda x: pbar.update())
                tasks.append(new_future)
    result = futures.wait(tasks)

    print('Generating CSV from label counts...')
    for res in tqdm(result.done):
        label_counts = res.result()
        if label_counts:
            doc_type = label_counts['doc_type']
            del label_counts['doc_type']
            ner_doc_counts[doc_type] += 1
            ner_label_counts[doc_type] = {label: ner_label_counts[doc_type].get(label, 0) + label_counts.get(label, 0)
                for label in set(ner_label_counts[doc_type]).union(label_counts)}

    df = pd.DataFrame.from_dict(dict(ner_label_counts), orient='index', dtype=float)
    df['doc_counts'] = df.index.map(ner_doc_counts)
    df.to_csv('ner_label_counts.csv')
    print('Label count CSV file saved!!!')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
