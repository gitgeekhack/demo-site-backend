import asyncio
import os
import cv2
from tqdm import tqdm
import numpy as np

IMAGES_PATH = os.getenv('IMAGES_PATH')
ANNOTATED_LABELS_PATH = os.getenv('ANNOTATED_LABELS_PATH')
TARGET_PATH = os.getenv('TARGET_PATH')

os.makedirs(TARGET_PATH, exist_ok=True)

labels = ['TITLE', 'CONTENT', 'FORM', 'TABLE','OTHER', 'QUESTIONNAIRE']


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
    iou = intersect_area / float(box_a_area)
    return iou


async def process_form_boxes(annot_forms, textract_forms):
    """
    If form annotation found for both annotated and textract extracted, to keep annotation boxes for the particular case
    Args:
        annot_forms: Annotated forms
        textract_forms: Textract annotated forms

    Returns:Filtered forms after removing the redundant ones

    """
    textract_coinciding_indexes = set()
    filtered_textract_forms = []

    if annot_forms and textract_forms:
        for t_form in textract_forms:
            iou = [await coinciding_bboxes_iou(t_form, t_box) for t_box in annot_forms]
            coinciding_ious = [i for i in iou if i > 0.5]
            if coinciding_ious:
                textract_coinciding_indexes.add(textract_forms.index(t_form))

        for i in range(len(textract_forms)):
            if i not in textract_coinciding_indexes:
                filtered_textract_forms.append(textract_forms[i])

    if not filtered_textract_forms:
        return [*annot_forms, *textract_forms]
    else:
        return [*annot_forms, *filtered_textract_forms]


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


async def save_bounding_boxes(file_name, height, width, bboxes_dict):
    """
    Saves bounding boxes in yolo format for obtained merged boxes
    Args:
        file_name: To be saved filename
        height: height of the image
        width: width of the image
        form_merged_boxes: merged form boxes
        table_merged_boxes: merged table boxes
    """
    annots = []
    for key, value in bboxes_dict.items():
        for bbox in value:
            bbox = [*bbox[0], *bbox[1]]
            xtl, ytl, xbr, ybr = await convert_to_yolo_bbox(height, width, bbox)
            annots.append(f'{labels.index(key) - 1} {xtl} {ytl} {xbr} {ybr}\n')
    with open(os.path.join(TARGET_PATH, file_name), "w") as write_file:
        write_file.writelines(annots)


async def __is_boxes_overlap(source, target):
    """
    This method finds the boxes are overlapped or not
    """

    tl1, br1 = source
    tl2, br2 = target

    if tl1[0] >= br2[0] or tl2[0] >= br1[0]:
        return False
    if tl1[1] >= br2[1] or tl2[1] >= br1[1]:
        return False
    return True


async def __get_all_overlaps(boxes, bounds, index):
    """
    This method is used to get all the overlapping bounding boxes
    """

    overlaps = []
    for a in range(len(boxes)):
        if a != index:
            if await __is_boxes_overlap(bounds, boxes[a]):
                overlaps.append(a)
    return overlaps


async def merge_boxes(boxes):
    """
    This method is used to merge the bounding boxes using margin
    """

    merge_margin = 25
    finished = False

    while not finished:
        finished = True

        index = len(boxes) - 1
        while index >= 0:
            curr = boxes[index]

            tl = curr[0][:]
            br = curr[1][:]
            tl[0] -= merge_margin
            tl[1] -= merge_margin
            br[0] += merge_margin
            br[1] += merge_margin

            overlaps = await __get_all_overlaps(boxes, [tl, br], index)

            if len(overlaps) > 0:
                con = []
                overlaps.append(index)
                for ind in overlaps:
                    tl, br = boxes[ind]
                    con.append([tl])
                    con.append([br])
                con = np.array(con)

                x, y, w, h = cv2.boundingRect(con.astype(int))

                w -= 1
                h -= 1
                merged = [[x, y], [x + w, y + h]]

                overlaps.sort(reverse=True)
                for ind in overlaps:
                    del boxes[ind]
                boxes.append(merged)

                finished = False
                break

            index -= 1
    return boxes


async def reformat_bounding_boxes(boxes):
    reformatted = []
    for box in boxes:
        reformatted.append([[box[0], box[1]], [box[2], box[3]]])
    return reformatted


async def main():
    label_files = os.listdir(ANNOTATED_LABELS_PATH)
    for file_name in tqdm(label_files):
        file_path = os.path.join(ANNOTATED_LABELS_PATH, file_name)
        image_path = os.path.join(IMAGES_PATH, file_name.replace(".txt", ".jpg"))

        image = cv2.imread(image_path)
        height, width, _ = image.shape
        with open(file_path, "r") as annot_file:
            annot_data = [i.replace("\n", "") for i in annot_file.readlines()]

        annot_boxes = await get_bounding_boxes(annot_data, height, width)

        reformatted_title_boxes = await reformat_bounding_boxes(annot_boxes['TITLE'])
        reformatted_content_boxes = await reformat_bounding_boxes(annot_boxes['CONTENT'])
        reformatted_form_boxes = await reformat_bounding_boxes(annot_boxes['FORM'])
        reformatted_table_boxes = await reformat_bounding_boxes(annot_boxes['TABLE'])        
        reformatted_other_boxes = await reformat_bounding_boxes(annot_boxes['OTHER'])
        reformatted_ques_boxes = await reformat_bounding_boxes(annot_boxes['QUESTIONNAIRE'])

        merged_title_content = await merge_boxes([*reformatted_title_boxes, *reformatted_content_boxes])
        only_title_bboxes = []
        for r in reformatted_title_boxes:
            if r in merged_title_content:
                merged_title_content.remove(r)
                only_title_bboxes.append(r)

        annot_boxes['TITLE'].clear()
        annot_boxes['CONTENT'] = merged_title_content
        annot_boxes['FORM'] = reformatted_form_boxes
        annot_boxes['TABLE'] = reformatted_table_boxes
        annot_boxes['OTHER'] = reformatted_other_boxes
        annot_boxes['QUESTIONNAIRE'] = reformatted_ques_boxes
        await save_bounding_boxes(file_name, height, width, annot_boxes)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
