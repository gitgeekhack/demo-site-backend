import asyncio
import xml.etree.ElementTree as ET
from collections import Counter
import csv
import numpy as np
import glob
import os
import zipfile
from tqdm import tqdm

DATASET_PATH = "D:/PareIT/Combined/"  # path to your dataset
SUMMARY_CSV_PATH = f'D:/Git/PareIT/pareit-miscellaneous-scripts/RelevantCheckBoxDatasetSummary.csv'  # path for the summary csv
files = glob.glob(os.path.join(DATASET_PATH, '*'))  # gets all file names from dataset

ANNOTATION_FILE = 'annotations.xml'  # annotation file

MODULE_NAMES = ['Handwritten_Checkbox', 'Sections', 'Document Structure']

LAYOUT_STRUCTURE = 'QUESTIONNAIRE'

# considered sections from the QUESTIONNAIRE label
sections_labels = ['SEC_REVIEW', 'SEC_PMH', 'SEC_DIAGNOSIS', 'SEC_SUBJECTIVE', 'SENT_PROGNOSIS', 'SEC_OBJECTIVE',
                   'SEC_CARE_PLAN']

# labels that contains checkbox and marks
checkbox_labels = ['FILENAME', 'SEC_CHECKBOX', 'SEC_SUBJECT', 'CHECKBOX', 'TEXT_BOX_PAIR', 'MARK']

count_labels = dict(zip(checkbox_labels, [None] * len(checkbox_labels)))

# function for writing in CSV
async def csv_writer(summary):
    with open(SUMMARY_CSV_PATH, 'a+', encoding='UTF-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=checkbox_labels)
        writer.writeheader()
        writer.writerows(summary)

# function for getting label and coordinates of the bounding boxes
async def get_bounding_box(attribute):
    return {'label': attribute['label'],
            'bbox': [float(attribute['xtl']),
                     float(attribute['ytl']),
                     float(attribute['xbr']),
                     float(attribute['ybr']),
                     ]
            }


async def bounding_box_per_label(filepath):
    tree = ET.parse(filepath)
    image_elements = tree.findall('image')
    label_bbox_map = []
    if image_elements:
        for idx, i in enumerate(image_elements):
            box = i.findall('box')
            bbox_per_label = []
            if box:
                for b in box:
                    bbox_per_label.append(await get_bounding_box(b.attrib))
            label_bbox_map.append({'page_no': idx, 'bbox_with_label': bbox_per_label})
    return label_bbox_map


# function for finding IOU between bounding boxes
async def boxes_overlap(boxA, boxB):  # boxA-small, boxB-big

    boxA = tuple(np.array(boxA) * 1000)
    boxB = tuple(np.array(boxB) * 1000)

    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)
    iou = interArea / float(boxAArea)
    return iou


async def unzip(root, filename):
    os.chdir(root)
    with zipfile.ZipFile(filename, "r") as zip_ref:
        zip_ref.extractall(os.path.splitext(filename)[0])


async def main():
    summary = []
    count_labels = dict(zip(checkbox_labels, [None] * len(checkbox_labels)))
    for file_i in tqdm(files):
        for (root, dirs, file) in os.walk(file_i, topdown=True):
            try:
                z = [i for i in file for j in MODULE_NAMES if i.startswith(j) and i.strip().endswith('.zip')]
                z = list(set(z))
                if len(z) == 3:
                    z.sort()
                    extractor_coroutines = [unzip(root, list(z)[i]) for i in range(0,3)]
                    await asyncio.gather(*extractor_coroutines)

                    file_path = os.path.join(root, os.path.splitext(list(z)[0])[0])
                    ds = await bounding_box_per_label(os.path.join(file_path, ANNOTATION_FILE))

                    file_path = os.path.join(root, os.path.splitext(list(z)[1])[0])
                    hw = await bounding_box_per_label(os.path.join(file_path, ANNOTATION_FILE))

                    file_path = os.path.join(root, os.path.splitext(list(z)[2])[0])
                    sc = await bounding_box_per_label(os.path.join(file_path, ANNOTATION_FILE))

                    sections_labels_iou = []
                    iou_labels = []
                    for i in range(0, len(ds)):
                        bb = [x['bbox'] for x in ds[i]['bbox_with_label'] if x['label'] == LAYOUT_STRUCTURE]
                        for x in bb:
                            sections_labels_iou.extend(
                                [y['bbox'] for y in sc[i]['bbox_with_label'] if y['label'] in sections_labels if
                                 await boxes_overlap(y['bbox'], x) > 0.7])
                        for x in sections_labels_iou:
                            iou_labels.extend(
                                [y['label'] for y in hw[i]['bbox_with_label'] if y['label'] in checkbox_labels if
                                 await boxes_overlap(y['bbox'], x) > 0.7])
                        if Counter(iou_labels):
                            count_labels = dict(Counter(iou_labels).items())
                            count_labels['FILENAME'] = root
                            summary.append(count_labels)
            except (KeyboardInterrupt, Exception) as e:
                print(e)
                await csv_writer(summary)
    await csv_writer(summary)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())