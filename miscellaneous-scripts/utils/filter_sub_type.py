import asyncio
import csv
import glob
import os
import pandas as pd
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from tqdm import tqdm


list_of_labels = ['filename']
DATASET_PATH = "/home/heli/Documents/dataset/"  # path to your dataset
SUMMARY_CSV_PATH = f'/home/heli/Documents/git/PareIT/pareit-miscellaneous-scripts/utils/stats_dataset_type.csv'# path for the summary csv
SUMMARY_BY_TYPE = f'/home/heli/Documents/git/PareIT/pareit-miscellaneous-scripts/utils/sum.csv'
files = glob.glob(os.path.join(DATASET_PATH, '*'))  # gets all file names from dataset
ANNOTATION_FILE = 'annotations.xml'
DELIMINATOR = '</meta>'

async def unzip(root, filename):
    os.chdir(root)
    with zipfile.ZipFile(filename, "r") as zip_ref:
        zip_ref.extractall(os.path.splitext(filename)[0])


async def csv_writer(summary,path):
    with open(path, 'a+', encoding='UTF-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=set().union(*(d.keys() for d in summary)))
        writer.writeheader()
        writer.writerows(summary)

async def get_id_and_doc_type(node):
    for x in node:
        if x.attrib['name'] == 'doc_type':
            return  x.text



async def get_subtype(root_node):
    image_nodes = root_node.findall('image')
    x = []
    for children in image_nodes:
        for child_node in children:
            if child_node.tag == 'box' and child_node.attrib['label'] == 'SPLIT':
                x.append(await get_id_and_doc_type(child_node))
    return x


async def get_document_details(root_dir, filename):
    name = os.path.splitext(filename)[0]
    document_details = {key: None for key in list_of_labels}
    filepath = os.path.join(name, ANNOTATION_FILE)
    tree = ET.parse(os.path.join(root_dir, filepath))
    root_node = tree.getroot()
    document_details['filename'] = root_dir
    x = await get_subtype(root_node)
    d = Counter(x)
    document_details = document_details | d
    return document_details


async def main():
    summary = []
    for file_i in tqdm(files):
        try:
            x = None
            x = list(filter(lambda x: x.startswith('Split_Turn') and (x.endswith('.zip') or x.endswith('.recreated')), os.listdir(file_i)))
            if x:
                await unzip(file_i, x[0])
                document_details = await get_document_details(file_i, x[0].split('.')[0])
                summary.append(document_details)
        except (KeyboardInterrupt, Exception) as e:
            print(e)
    await csv_writer(summary,path=SUMMARY_CSV_PATH)
    summary_type = []
    df = pd.DataFrame(summary)
    for x in df.keys():
        if x != 'filename':
            summary_type.append({'label': x, 'sum': df[x].sum()})
    await csv_writer(summary_type,path=SUMMARY_BY_TYPE)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
