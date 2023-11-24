import asyncio
import os
from itertools import groupby
import cv2
from tqdm import tqdm

IMAGES_PATH = os.getenv('IMAGES_PATH')
LABELS_PATH = os.getenv('LABELS_PATH')

async def yolobbox2bbox(size, bbox):
    """
    Converts yolo bounding box to normal bounding box
    Args:
        size: shape of the image (width, height)
        bbox: YOlo bbox co-ordinates

    Returns: Normal bounding box co-ordinates

    """
    x1 = int((bbox[0] - bbox[2] / 2) * size[0])
    x2 = int((bbox[0] + bbox[2] / 2) * size[0])
    y1 = int((bbox[1] - bbox[3] / 2) * size[1])
    y2 = int((bbox[1] + bbox[3] / 2) * size[1])

    if x1 < 0:
        x1 = 0
    if x2 > size[0] - 1:
        x2 = size[0] - 1
    if y1 < 0:
        y1 = 0
    if y2 > size[1] - 1:
        y2 = size[1] - 1
    return x1, y1, x2, y2


async def get_required_boxes(data, size, label_index):
    """
    Returns required label's bounding boxes referenced by the label index
    """
    hf_boxes = []
    for annot in data:
        annot_list = annot.split(" ")
        if int(annot_list[0]) == label_index:
            normal_bbox = await yolobbox2bbox(size, [float(i) for i in annot_list[1:]])
            hf_boxes.append(normal_bbox)
    return hf_boxes


async def get_header_footer_boxes(group):
    """
    Returns all the header footer bounding boxes for a split images group
    """
    all_header_footer_boxes = []
    for g_file in group:
        image_path = os.path.join(IMAGES_PATH, g_file.replace(".txt", ".jpg"))
        image = cv2.imread(image_path)
        h, w, _ = image.shape
        with open(os.path.join(LABELS_PATH, g_file), "r") as read_file:
            data = read_file.readlines()
        hf_boxes = await get_required_boxes(data, (w, h), 4)
        all_header_footer_boxes.extend(hf_boxes)
    return all_header_footer_boxes


async def get_bounding_boxes(annots, ht, wd):
    """
    Gets normal bounding boxes out of yolo co-ordinates with the bifurcation of form and tables
    Args:
        annots: yolo annotations
        ht: height of the image
        wd: width of the image
        req_labels: Label indexes for which annotations needs to be converted

    Returns: Dictionary of forms and tables bounding boxes

    """
    bboxes = {k: [] for k in labels}
    for annot in annots:
        yolo_annots = annot.rsplit(" ")
        yolo_bbox = [float(i) for i in yolo_annots[1:]]
        box_coords = await yolobbox2bbox((wd, ht), yolo_bbox)
        bboxes[labels[int(yolo_annots[0])]].append(box_coords)
    return bboxes


async def coinciding_bboxes_iou(box_a, box_b):  # boxA-small, boxB-big
    """
    Calculates the iou for two bounding boxes to check if the smaller box lies inside the bigger one
    :param box_a: Co-ordinates of the smaller bounding box
    :param box_b: Co-ordinates of the bigger bounding box
    :return: iou for the given bounding boxes
    """
    x_a = max(box_a[0], box_b[0])
    y_a = max(box_a[1], box_b[1])
    x_b = min(box_a[2], box_b[2])
    y_b = min(box_a[3], box_b[3])

    intersect_area = max(0, x_b - x_a + 1) * max(0, y_b - y_a + 1)
    box_a_area = (box_a[2] - box_a[0] + 1) * (box_a[3] - box_a[1] + 1)
    if box_a_area>0:
        iou = intersect_area / float(box_a_area)
        return iou
    else:
        return 0


async def get_header_footer_coinciding_boxes(bifurcated_boxes, hf_boxes):
    """
    Filters bounding boxes coinciding with Header Footer based on IOU
    """
    hf_coincides = []
    for key, values in bifurcated_boxes.items():
        if values and key not in ['HEADER_FOOTER', 'REP_HEADER_FOOTER']:
            for bbox in values:
                ious = [await coinciding_bboxes_iou(bbox, hf_box) for hf_box in hf_boxes]
                index = [ious.index(i) for i in ious if i > 0.7]
                if index: 
                    hf_coincides.append([labels.index(key), *bbox])
    return hf_coincides


async def sort_cordinates(coordinate1, coordinate2) -> tuple:
    """
    Sorting method finds the minimum and maximum among the two coordinates
    :param coordinate1: float value
    :param coordinate2: float value
    :return: max and min coordinates
    """
    if coordinate1 > coordinate2:
        max_coord, min_coord = coordinate1, coordinate2
        return max_coord, min_coord
    else:
        max_coord, min_coord = coordinate2, coordinate1
        return max_coord, min_coord
    
    
async def convert_to_yolo_bbox(height, width, bbox) -> tuple:
    """
    The method takes input as a tuple of bounding box for annotation in CVAT
    :param height: height of the image
    :param width: width of the image
    :param bbox: tuple of bounding box
    :return: tuple (x,y,w,h) converted coordinate to yolo format
    """

    x_max, x_min = await sort_cordinates(bbox[0], bbox[2])
    y_max, y_min = await sort_cordinates(bbox[1], bbox[3])
    dw = 1. / width
    dh = 1. / height
    x = (x_min + x_max) / 2.0
    y = (y_min + y_max) / 2.0
    w = x_max - x_min
    h = y_max - y_min
    x = round(x * dw, 6)
    w = round(w * dw, 6)
    y = round(y * dh, 6)
    h = round(h * dh, 6)
    return x, y, w, h


async def get_yolo_bboxes(height, width, coinciding_ones):
    """
    Converts bounding boxes to yolo format
    """
    for annots in coinciding_ones:
        yolo_bbox = await convert_to_yolo_bbox(height, width, annots[1:])
        coinciding_ones[coinciding_ones.index(annots)] = " ".join([str(annots[0]), *[str(y) for y in yolo_bbox]]) + "\n"
    return coinciding_ones


async def get_actual_coinciding_ones(coinciding, rep_hf):
    """
    Filters out layout bounding boxes that coincide with the Header Footer Bounding box
    """
    actual = []
    for coin in coinciding:
        ious = [await coinciding_bboxes_iou(coin[1:], rep) for rep in rep_hf]
        index = [ious.index(i) for i in ious if i > 0.9]
        if index:
            actual.append(coin)
    return actual


async def process_group(group):
    hf_boxes = await get_header_footer_boxes(group)
    all_boxes_coiniciding_hf = []
    for file in group:
        image_path = os.path.join(IMAGES_PATH, file.replace(".txt", ".jpg"))
        image = cv2.imread(image_path)
        h, w, _ = image.shape
        file_path = os.path.join(LABELS_PATH, file)
        with open(file_path, "r") as read_file:
            all_data = read_file.readlines()
        separated_bboxes = await get_bounding_boxes(all_data, h, w)
        hf_coinciding_boxes = await get_header_footer_coinciding_boxes(separated_bboxes, hf_boxes)
        all_boxes_coiniciding_hf.extend(hf_coinciding_boxes)
    
    for file in group:
        image_path = os.path.join(IMAGES_PATH, file.replace(".txt", ".jpg"))
        image = cv2.imread(image_path)
        h, w, _ = image.shape
        file_path = os.path.join(LABELS_PATH, file)
        with open(file_path, "r") as read_file:
            prev_data = read_file.readlines()

        annot_indexes = [int(annot.rsplit(" ")[0]) for annot in prev_data]
        rep_hf_boxes = await get_required_boxes(prev_data, (w, h), 8)
        if rep_hf_boxes:
            actual_ones = await get_actual_coinciding_ones(all_boxes_coiniciding_hf, rep_hf_boxes)
            actual_yolo = await get_yolo_bboxes(h, w, actual_ones)

            if 8 in annot_indexes:
                with open(file_path, "a") as app_file:
                    app_file.writelines(actual_yolo)

async def main():
    for group in tqdm(res, desc="Processing split group..."):
        await process_group(group)

if __name__=="__main__":
    label_files = os.listdir(LABELS_PATH)
    label_files.sort()
    res = [list(i) for j, i in groupby(label_files,
                                       lambda a: "".join(("".join(a.split(".")[:-1])).split("_")[:-1]))]
    labels = ['TITLE', 'SUBTITLE', 'CONTENT', 'FORM', 'HEADER_FOOTER', 'OTHER', 'TABLE', 'QUESTIONNAIRE',
              'REP_HEADER_FOOTER']

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

