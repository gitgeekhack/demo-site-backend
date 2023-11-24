import asyncio
import csv
import os
import glob
import re
import zipfile
import collections
import xml.etree.ElementTree as ET
from tqdm import tqdm

list_of_labels = ['FILENAME', 'SEC_CHECKBOX', 'SEC_SUBJECT', 'CHECKBOX', 'TEXT_BOX_PAIR', 'MARK', 'HANDWRITTEN', 'SIGNATURE']
DATASET_PATH = "/data/raw_dataset"  # path to your dataset
SUMMARY_CSV_PATH = f'/home/ubuntu/git/pareit-miscellaneous-scripts/checkbox_mark_detection/CheckboxDatasetSummary.csv'  # path for the summary csv
files = glob.glob(os.path.join(DATASET_PATH, '*'))  # gets all file names from dataset
ANNOTATION_FILE = 'annotations.xml'
MODULE_NAME = 'Handwritten_Checkbox'
DELIMINATOR = '</meta>'


async def csv_writer(summary):
    with open(SUMMARY_CSV_PATH, 'a+', encoding='UTF-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=list_of_labels)
        writer.writeheader()
        writer.writerows(summary)


async def unzip(root, filename):
    os.chdir(root)
    with zipfile.ZipFile(filename + '.zip', "r") as zip_ref:
        zip_ref.extractall(filename)


async def get_label_frequency(root_dir, filename, frequency_by_label):
    filepath = os.path.join(filename, ANNOTATION_FILE)
    tree = ET.parse(os.path.join(root_dir, filepath))
    root = tree.getroot()
    xml_to_str = ET.tostring(root, encoding='utf8', method='xml').decode("utf-8")
    xml_to_str = xml_to_str[xml_to_str.index(DELIMINATOR):]
    words = re.findall('\w+', xml_to_str)
    c = collections.Counter(words)
    frequency_by_label['FILENAME'] = root_dir
    for x in frequency_by_label:
        if x in c:
            frequency_by_label[x] = c[x]
    return frequency_by_label


async def main():
    summary = []
    for file_i in tqdm(files):
        for (root, dirs, file) in os.walk(file_i, topdown=True):
            try:
                for f in file:
                    name_without_space = f.strip().replace(' ', '_')
                    filename = f.replace('.zip', '')
                    if name_without_space.startswith(MODULE_NAME) and f.endswith('zip'):
                        frequency_by_label = {key: None for key in list_of_labels}
                        await unzip(root, filename)
                        frequency_by_label = await get_label_frequency(root, filename, frequency_by_label)
                        summary.append(frequency_by_label)
            except (KeyboardInterrupt, Exception) as e:
                print(e)
                await csv_writer(summary)
    await csv_writer(summary)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
