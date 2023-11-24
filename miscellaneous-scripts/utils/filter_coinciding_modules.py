import asyncio
import xml.etree.ElementTree as ET
from collections import Counter
import csv
import numpy as np
import tqdm
import glob
import os
import zipfile
from tqdm import tqdm

DATASET_PATH = "D:/PareIT/Combined/"  # path to your dataset
SUMMARY_CSV_PATH = f'D:/Git/PareIT/pareit-miscellaneous-scripts/CoincidingCheckBoxDatasetSummary.csv'  # path for the summary csv
files = glob.glob(os.path.join(DATASET_PATH, '*'))  # gets all file names from dataset
ANNOTATION_FILE = 'annotations.xml'

ALL_SUB_MODULE_NAMES = ['FILENAME', 'SEC_REVIEW', 'SEC_OTHER', 'SEC_PMH', 'SEC_DIAGNOSIS', 'SEC_GEN_INFO',
                        'SEC_SUBJECTIVE',
                        'SENT_PROGNOSIS', 'SEC_OBJECTIVE', 'SEC_CARE_PLAN']


PRIMARY_LABEL_CATEGORY = 'QUESTIONNAIRE'
MODULE_NAMES = ['Sections', 'Document Structure']
count_labels = dict(zip(ALL_SUB_MODULE_NAMES, [None] * len(ALL_SUB_MODULE_NAMES)))


async def csv_writer(summary):
    with open(SUMMARY_CSV_PATH, 'a+', encoding='UTF-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=ALL_SUB_MODULE_NAMES)
        writer.writeheader()
        for summ in summary:
            print(summ)
            writer.writerow(summ)


async def cal_iou(ground_truth, pred):
    # coordinates of the area of intersection.
    ix1 = np.maximum(ground_truth[0], pred[0])
    iy1 = np.maximum(ground_truth[1], pred[1])
    ix2 = np.minimum(ground_truth[2], pred[2])
    iy2 = np.minimum(ground_truth[3], pred[3])

    # Intersection height and width.
    i_height = np.maximum(iy2 - iy1 + 1, np.array(0.))
    i_width = np.maximum(ix2 - ix1 + 1, np.array(0.))

    area_of_intersection = i_height * i_width

    # Ground Truth dimensions.
    gt_height = ground_truth[3] - ground_truth[1] + 1
    gt_width = ground_truth[2] - ground_truth[0] + 1

    # Prediction dimensions.
    pd_height = pred[3] - pred[1] + 1
    pd_width = pred[2] - pred[0] + 1

    area_of_union = gt_height * gt_width + pd_height * pd_width - area_of_intersection

    iou = area_of_intersection / area_of_union

    return iou


'''
xmax === xbr
xmin === xtl
ymin === ytl
ymax === ybr
'''


async def get_bounding_box(attribute):
    return {'label': attribute['label'],
            'bbox': [float(attribute['xtl']), float(attribute['ytl']), float(attribute['xbr']),
                     float(attribute['ybr']), ]}


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


async def unzip(root, filename):
    os.chdir(root)
    with zipfile.ZipFile(filename, "r") as zip_ref:
        zip_ref.extractall(os.path.splitext(filename)[0])


async def main():
    summary = []
    sc = ds = []
    for file_i in tqdm(files):
        count_labels = dict(zip(ALL_SUB_MODULE_NAMES, [None] * len(ALL_SUB_MODULE_NAMES)))
        for (root, dirs, file) in os.walk(file_i, topdown=True):
            try:
                z = [i for i in file for j in MODULE_NAMES if i.startswith(j) and i.strip().endswith('.zip')]
                z = list(set(z))
                if len(z) == 2:
                    z.sort()
                    await unzip(root, list(z)[0])
                    await unzip(root, list(z)[1])
                    file_path = os.path.join(root, os.path.splitext(list(z)[0])[0])
                    ds = await bounding_box_per_label(os.path.join(file_path, ANNOTATION_FILE))
                    file_path = os.path.join(root, os.path.splitext(list(z)[1])[0])
                    sc = await bounding_box_per_label(os.path.join(file_path, ANNOTATION_FILE))

                    iou_labels = []
                    for i in range(0, len(ds)):
                        bb = [x['bbox'] for x in ds[i]['bbox_with_label'] if x['label'] == PRIMARY_LABEL_CATEGORY]
                        for x in bb:
                            iou_labels.extend(
                                [y['label'] for y in sc[i]['bbox_with_label'] if await cal_iou(y['bbox'], x) > 0.8])
                        if Counter(iou_labels):
                            count_labels['FILENAME'] = file_i
                            count_labels = dict(count_labels.items() | Counter(iou_labels).items())
                            summary.append(count_labels)
            except (KeyboardInterrupt, Exception) as e:
                print(e)
                await csv_writer(summary)
    await csv_writer(summary)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())