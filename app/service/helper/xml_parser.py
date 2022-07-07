import asyncio

import xmltodict
import fitz
import aiofiles
from app import logger


async def get_bounding_boxes_from_page(uuid, page_image, bounding_box_data, width_ratio, height_ratio, dynamic_blocks):
    """
        reads bounding boxes from single page and stores in dictionary
        Parameters:
            page_image <dict>: annotation data dictionary for single page
            bounding_box_data <dict>: Python dictionary which contains page wise annotation label and
                                      its corresponding bounding box
            width_ratio <float>: pdf to image width ratio
            height_ratio <float>: pdf to image height ratio
    """
    try:
        page_no = int(page_image['@id'])

        if page_image['box']:
            bounding_box_data[page_no] = {}
        if not isinstance(page_image['box'], list):
            page_image['box'] = [page_image['box']]

        # iterating through all annotation of a page
        for box in page_image['box']:
            # dynamic data
            if 'attribute' in box.keys():
                box['@xtl'] = width_ratio * float(box['@xtl'])
                box['@ytl'] = height_ratio * float(box['@ytl'])
                box['@xbr'] = width_ratio * float(box['@xbr'])
                box['@ybr'] = height_ratio * float(box['@ybr'])
                if page_no not in dynamic_blocks.keys():
                    dynamic_blocks[page_no] = [[page_image['@name'], [box]]]
                else:
                    dynamic_blocks[page_no].append([page_image['@name'], [box]])
            # static data
            else:
                bounding_box_data[page_no][box['@label']] = \
                    [width_ratio * float(box['@xtl']), height_ratio * float(box['@ytl']),
                     width_ratio * float(box['@xbr']), height_ratio * float(box['@ybr'])]

    except KeyError as e:
        logger.warning(f'Request ID: [{uuid}]  -> {e}')

    return dynamic_blocks


async def find_rectangle_boxes(uuid, annotation_file, sample_file):
    """
        reads bounding box data from annotation file(.xml) and saves to dictionary with labels
        Parameters:
            annotation_file <.xml file>: annotation file with path
            sample_file <.pdf file>: pdf file for mapping bounding box from annotation_file
        Returns:
            static_bounding_boxes <dict>: Python dictionary which contains page wise annotation label and
                                      its corresponding bounding box
    """
    doc = fitz.open(sample_file)

    async with aiofiles.open(annotation_file, mode='r') as file:
        my_xml = await file.read()

    my_dict = xmltodict.parse(my_xml)

    pdf_width = float(doc[0].bound().x1)
    pdf_height = float(doc[0].bound().y1)

    if isinstance(my_dict['annotations']['image'], dict):
        my_dict['annotations']['image'] = [my_dict['annotations']['image']]

    image_width = float(my_dict['annotations']['image'][0]['@width'])
    image_height = float(my_dict['annotations']['image'][0]['@height'])

    width_ratio = pdf_width / image_width
    height_ratio = pdf_height / image_height

    static_bounding_boxes = {}
    dynamic_blocks = {}

    try:
        # iterating through all pages of pdf
        get_bounding_box_coroutines = [get_bounding_boxes_from_page(uuid, page_image, static_bounding_boxes,
                                                                    width_ratio, height_ratio, dynamic_blocks)
                                       for page_image in my_dict['annotations']['image']]

        await asyncio.gather(*get_bounding_box_coroutines)

    except KeyError as e:
        logger.warning(f'Request ID: [{uuid}]  -> {e}')

    return static_bounding_boxes, dynamic_blocks
