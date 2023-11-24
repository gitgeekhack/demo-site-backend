import xml.etree.ElementTree as ET
import glob
import os
import asyncio
import zipfile
import cv2
import math
import numpy as np
import json
from tqdm import tqdm

# defining constants
# DATASET_PATH = "/home/vivek/Downloads/temp_document/"  # path to your dataset
# files = glob.glob(os.path.join(DATASET_PATH, '*'))  # gets all file names from dataset

SAVE_CROP_IMAGES_PATH = './train_cropped_images/'  # path to cropped sections images
SAVE_COCO_JSON_PATH = './train_checkbox_mark_dataset.json'  # path to coco_dataset json

LAYOUT_STRUCTURE = 'QUESTIONNAIRE'
ANNOTATION_FILE = 'annotations.xml'  # annotation file

MODULE_NAMES = ['Handwritten_Checkbox', 'Sections', 'Document Structure']

# applicable labels of the sections
SECTIONS_LABELS = ['SEC_REVIEW', 'SEC_PMH', 'SEC_DIAGNOSIS', 'SEC_SUBJECTIVE', 'SENT_PROGNOSIS', 'SEC_OBJECTIVE',
                   'SEC_CARE_PLAN']

# required labels of the checkbox/mark
CHECKBOX_LABELS = ['CHECKBOX', 'TEXT_BOX_PAIR', 'MARK']

img_id = 0  # storing unique id of image
annotation_id = 0  # storing unique id of annotation

# categories for the coco dataset
categories = [
    {
        "id": 0,
        "name": 'CHECKBOX_CHECKED',
        "supercategory": 'CHECKBOX',
    },
    {
        "id": 1,
        "name": 'CHECKBOX_UNCHECKED',
        "supercategory": 'CHECKBOX',
    },
    {
        "id": 2,
        "name": 'TEXT_BOX_PAIR',
        "supercategory": '',
    },
    {
        "id": 3,
        "name": 'MARKED_TEXT',
        "supercategory": '',
    }
]

# categories name
categories_name = [i['name'] for i in categories]

# categories IDs
categories_id = {
    'CHECKBOX_CHECKED': 0,
    'CHECKBOX_UNCHECKED': 1,
    'TEXT_BOX_PAIR': 2,
    'MARKED_TEXT': 3
}

# crop image segment of sections from the page
async def crop_image_segment(img_file, x1, y1, x2, y2, save_file_name):
    img = cv2.imread(img_file)
    cropped_image = img[math.floor(y1):math.ceil(y2), math.floor(x1):math.ceil(x2)]  # crop the image
    height = cropped_image.shape[0]
    width = cropped_image.shape[1]
    cv2.imwrite(save_file_name, cropped_image)
    return {'image_path': save_file_name, 'image_height': height, 'image_width': width}


# calculating the IOU of bounding boxes
async def calculate_iou(box_a, box_b):  # boxA-small, boxB-big
    box_a = tuple(np.array(box_a) * 1000)
    box_b = tuple(np.array(box_b) * 1000)

    x_a = max(box_a[0], box_b[0])
    y_a = max(box_a[1], box_b[1])
    x_b = min(box_a[2], box_b[2])
    y_b = min(box_a[3], box_b[3])

    intersect_area = max(0, x_b - x_a + 1) * max(0, y_b - y_a + 1)
    box_a_area = (box_a[2] - box_a[0] + 1) * (box_a[3] - box_a[1] + 1)
    iou = intersect_area / float(box_a_area)
    return iou


# getting bounding box of the label
async def get_bounding_box(attribute):
    return {'label': attribute['label'],
            'sub_label': attribute['sub_label'],
            'bbox': [float(attribute['xtl']),
                     float(attribute['ytl']),
                     float(attribute['xbr']),
                     float(attribute['ybr']),
                     ],
            'image': attribute['image']
            }


# getting bounding box per label from 'annotation.xml' file
async def bounding_box_per_label(filepath):
    tree = ET.parse(filepath)
    image_elements = tree.findall('image')

    label_bbox_map = []
    if image_elements:
        for idx, i in enumerate(image_elements):
            box = i.findall('box')
            bbox_per_label = []
            if box:
                # iterate through box tree, find labels and sub-label
                for b in box:
                    try:
                        # 'attribute' tag contains sub-label
                        b.attrib['sub_label'] = b.findall('attribute')
                    except Exception:
                        b.attrib['sub_label'] = None
                    b.attrib['image'] = i.attrib
                    bbox_per_label.append(await get_bounding_box(b.attrib))
            label_bbox_map.append({'page_no': idx, 'bbox_with_label': bbox_per_label})
    return label_bbox_map


# unzip the archive files
async def unzip(root, filename):
    os.chdir(root)
    with zipfile.ZipFile(filename, "r") as zip_ref:
        zip_ref.extractall(os.path.splitext(filename)[0])


# resetting the coordinates of checkboxes after cropping the image
async def reset_checkbox_coordinates(checkbox_coord, section_coord):
    xtl = checkbox_coord[0] - section_coord[0]
    ytl = checkbox_coord[1] - section_coord[1]
    xbr = checkbox_coord[2] - section_coord[0]
    ybr = checkbox_coord[3] - section_coord[1]
    return [xtl, ytl, xbr, ybr]


# get the checked labels from 'MARK' and 'CHECKBOX' categories
async def get_checked_category_label(sub_label_value):
    name_lst = []  # list contains checked labels
    for idx, name in enumerate(sub_label_value['name']):
        if name == 'marked_text' or name == 'is_positive' or name == 'is_negative':
            name_lst.append('MARKED_TEXT')
        if name == 'checked' and sub_label_value['bool_values'][idx] == 'true':
            name_lst.append('CHECKBOX_CHECKED')

        elif name == 'checked' and sub_label_value['bool_values'][idx] == 'false':
            name_lst.append('CHECKBOX_UNCHECKED')

    sub_label_value['name'] = name_lst
    return sub_label_value


# coinciding sections with the questionnaire layout structure
async def get_coinciding_sections_coordinates(ds, sc, hw):
    sections_bbox = []  # contains section coordinates
    hw_bbox_with_label = 0  # contains bbox with labels of handwritten/checkbox

    # finding the bounding box that contains 'Questionnaire' Layout Structure
    for i in range(0, len(ds)):
        questionnaire_bbox = [x['bbox'] for x in ds[i]['bbox_with_label'] if
                              x['label'] == LAYOUT_STRUCTURE]

        # finding the bounding box that contains applicable sections in questionnaire using IOU
        for x in questionnaire_bbox:
            sections_bbox.extend(
                [y['bbox'] for y in sc[i]['bbox_with_label'] if y['label'] in SECTIONS_LABELS if
                 await calculate_iou(y['bbox'], x) > 0.7])

        hw_bbox_with_label = hw[i]['bbox_with_label']
    return sections_bbox, hw_bbox_with_label


# fill coco annotations json
async def fill_coco_annotations(category_id, xtl, ytl, xbr, ybr, width, height, image_name, coco_annotations):
    global img_id, annotation_id
    annotation = {
        "id": annotation_id,
        "image_id": img_id,
        "image_name": image_name,
        "category_id": category_id,
        "bbox": [xtl, ytl, width, height],
        "area": width * height,
        "segmentation": [
            [xtl, ytl, xtl, ytl + ybr, xtl + xbr, ytl + ybr, xtl + xbr, ybr]],
        # derived segmentation coordinates from bounding box. Please refer
        # https://www.section.io/engineering-education/understanding-coco-dataset/#segmentation
        "iscrowd": 0,
    }
    coco_annotations.append(annotation)
    annotation_id += 1


# generate coco dataset of checkbox/mark detection
async def generate_coco_dataset(coco_images, coco_annotations, ds, sections_bbox, root, hw_bbox_with_label):
    global img_id, annotation_id
    checkboxes_bbox = []  # store the checkboxes labels and bboxes section wise

    # finding the checkboxes/marks falls in the applicable sections using the IOU and transform it
    # into COCO dataset
    for sec_coord in sections_bbox:
        checkbox_bbox_coord = []  # stores bbox data of checkboxes

        image_path = glob.glob(os.path.join(root, "*/**/**/**.jpg"))
        if image_path:
            img_path = os.path.join(root, 'images/images', ds[0]['bbox_with_label'][0]['image']['name'])
        else:
            img_path = os.path.join(root, 'images', ds[0]['bbox_with_label'][0]['image']['name'])

        # crop the segment of sections and store into the local system
        image_info = await crop_image_segment(
            img_path,
            sec_coord[0], sec_coord[1], sec_coord[2], sec_coord[3],
            f'{SAVE_CROP_IMAGES_PATH}{str(img_id)}.jpg')

        # collect the cropped image into collections
        image = {
            'file_name': image_info['image_path'],
            'height': image_info['image_height'],
            'width': image_info['image_width'],
            'id': img_id,
        }

        # finding the checkbox/marks falls into sections
        for y in hw_bbox_with_label:
            if y['label'] in CHECKBOX_LABELS:
                if await calculate_iou(y['bbox'], sec_coord) > 0.7:
                    sub_label_value = {}
                    names = []
                    bool_values = []

                    for z in y['sub_label']:
                        names.append(z.attrib['name'])
                        bool_values.append(z.text)

                    sub_label_value['name'] = names
                    sub_label_value['bool_values'] = bool_values

                    sub_label_value = await get_checked_category_label(sub_label_value)
                    # resetting the coordinates of the checkbox/mark bbox
                    xtl, ytl, xbr, ybr = await reset_checkbox_coordinates(y['bbox'], sec_coord)

                    # store the checkbox bbox information into 'checkbox_bbox_coord' list
                    checkbox_bbox_coord.append({'label': y['label'], 'bbox': y['bbox']})
                    width, height = xbr - xtl, ybr - ytl

                    if y['label'] == 'CHECKBOX' or y['label'] == 'MARK':
                        await fill_coco_annotations(categories_id[sub_label_value['name'][0]], xtl, ytl, xbr, ybr,
                                                    width, height, image_info['image_path'], coco_annotations)
                    else:
                        await fill_coco_annotations(categories_id[y['label']], xtl, ytl, xbr, ybr, width, height,
                                                    image_info['image_path'], coco_annotations)

        checkboxes_bbox.append(checkbox_bbox_coord)
        coco_images.append(image)
        img_id += 1


async def main():
    coco_images = []  # storing collections of the COCO images
    coco_annotations = []  # storing collections of COCO annotations

    # open 'train.txt' file
    txt_file = open('./train.txt', "r", encoding='utf-8-sig')
    file_content = txt_file.readlines()
    file_list = [file.replace('"', '').strip() for file in file_content]

    for file_i in tqdm(file_list):
        for (root, dirs, file) in os.walk(file_i, topdown=True):
            try:
                get_modules_files = [i for i in file for j in MODULE_NAMES if
                                     i.startswith(j) and i.strip().endswith('.zip')]

                get_modules_files = list(set(get_modules_files))
                if len(get_modules_files) == 3:
                    get_modules_files.sort()  # sorting the modules file names

                    # extract zip files of the modules
                    extractor_coroutines = [unzip(root, list(get_modules_files)[i]) for i in range(0, 3)]
                    await asyncio.gather(*extractor_coroutines)

                    # getting the bounding box per labels using the 'annotation.xml' files
                    file_path = os.path.join(root, os.path.splitext(list(get_modules_files)[0])[0])
                    ds = await bounding_box_per_label(os.path.join(file_path, ANNOTATION_FILE))

                    file_path = os.path.join(root, os.path.splitext(list(get_modules_files)[1])[0])
                    hw = await bounding_box_per_label(os.path.join(file_path, ANNOTATION_FILE))

                    file_path = os.path.join(root, os.path.splitext(list(get_modules_files)[2])[0])
                    sc = await bounding_box_per_label(os.path.join(file_path, ANNOTATION_FILE))

                    sections_bbox, hw_bbox_with_label = await get_coinciding_sections_coordinates(ds, sc, hw)

                    await generate_coco_dataset(coco_images, coco_annotations, ds, sections_bbox, root,
                                                hw_bbox_with_label)

            except Exception as e:
                print(e)

    # prepares the coco_dataset
    coco_dataset = {
        'categories': categories,
        'annotations': coco_annotations,
        'images': coco_images
    }

    # store the coco_dataset into the json
    with open(os.path.join(SAVE_COCO_JSON_PATH), 'w') as outfile:
        json.dump(coco_dataset, outfile)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
