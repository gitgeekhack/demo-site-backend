"""
    Note:
    following environment variables will be required to run this file:
        RAW_DATASET_PATH <str>: full path of dataset folder
        SAVE_DATASET_PATH <str>: full path to save generated dataset folder
"""

import asyncio
import shutil
from queue import Queue
import os
import traceback
import aiofiles
from tqdm import tqdm
from glob import glob
from dsutils import get_annotation_full_path
from dsutils.cvat import CVATHelper
from dsutils.design_patterns import AsyncObject
import datetime

date_time = datetime.datetime.now().strftime('%m%d%Y_%H%M')
RAW_DATASET_PATH = os.getenv('RAW_DATASET_PATH')
SAVE_DATASET_PATH = os.getenv('SAVE_DATASET_PATH')

SUCCESSFUL_FILES = os.path.join(os.getcwd(), f'successful_files{date_time}.txt')
UNSUCCESSFUL_FILES = os.path.join(os.getcwd(), f'unsuccessful_files{date_time}.txt')

PROJECTS = ['Handwritten_Checkbox']

HANDWRITTEN_LABELS = ['CHECKBOX','HANDWRITTEN','SIGNATURE','TEXT_BOX_PAIR', 'MARK']

ENCODED_LABELS = {'HANDWRITTEN': 0, 'SIGNATURE': 1, 'CHECKBOX_CHECKED': 2, 'CHECKBOX_UNCHECKED': 3, 'TEXT_BOX_PAIR': 4, 'MARK': 5}


if not RAW_DATASET_PATH:
    print('Configuration incomplete, Please set RAW_DATASET_PATH')
    exit(1)
if not SAVE_DATASET_PATH:
    print('Configuration incomplete, Please set SAVE_DATASET_PATH')
    exit(1)
if not SUCCESSFUL_FILES:
    print('Configuration incomplete, Please set SUCCESSFUL_FILES')
    exit(1)
if not UNSUCCESSFUL_FILES:
    print('Configuration incomplete, Please set UNSUCCESSFUL_FILES')
    exit(1)

is_dirs_available = [SAVE_DATASET_PATH, os.path.join(SAVE_DATASET_PATH, 'images'), os.path.join(SAVE_DATASET_PATH, 'labels')]

for path in is_dirs_available:
    if not os.path.exists(path):
        os.makedirs(path)

global progress_bar


class HandwrittenDatasetGeneration(AsyncObject):
    async def __init__(self):
        self.files_q = Queue()

    async def __get_annotations_boxes(self, image, categories):
        """ This method iterates through boxes and returns required labels bounding boxes """
        annotation_boxes = []
        if isinstance(image['box'], dict):
            image['box'] = [image['box']]
        for box in image['box']:
            if box['@label'] in categories:
                annotation_boxes.append(box)
        return annotation_boxes

    async def __get_sublabel(self, checkbox):
        """ This method identifies the sub-label of CHECKBOX label """

        if checkbox['@label'] == 'CHECKBOX':
            if checkbox['attribute']['@name'] == 'checked':
                if checkbox['attribute']['#text'] == 'true':
                    return 'CHECKBOX_CHECKED'
                else:
                    return 'CHECKBOX_UNCHECKED'
        else:
            return checkbox['@label']

    async def __get_required_annotations(self, annotation_objects, annotation_file_path):
        """ This method filters all annotations for required annotation labels """

        annotations = {'Handwritten_Checkbox': []}
        labels = {'Handwritten_Checkbox': HANDWRITTEN_LABELS}

        for key, obj in annotation_objects.items():
            categories = labels[key]

            images = obj.annotations['annotations']['image']
            if isinstance(obj.annotations['annotations']['image'], dict):
                images = [obj.annotations['annotations']['image']]

            try:
                for img in images:
                    image_name = os.path.basename(img['@name'])
                    split_path = "/".join(annotation_file_path.rsplit("/")[:-2])
                    image_path = glob(f'{split_path}/**/{image_name}', recursive=True)[0]

                    annotation_boxes = await self.__get_annotations_boxes(img, categories)
                    annotations[key].append({'img_path': image_path, 'height': img['@height'], 'width': img['@width'],
                                                 'boxes': annotation_boxes})
            except Exception:
                pass

        return annotations

    async def __get_handwritten_checkbox_annotations(self, handwritten_anno, handwritten_checkbox):
        """ This method stores images and labels to a directory """
        for index, handwritten in enumerate(handwritten_anno["Handwritten_Checkbox"]):
            for hw in handwritten['boxes']:
                if hw['@label'] in HANDWRITTEN_LABELS:
                    hw_bbox = [float(hw['@xtl']), float(hw['@ytl']),
                                     float(hw['@xbr']), float(hw['@ybr'])]

                    image_path = handwritten['img_path']

                    hw["@label"] = await self.__get_sublabel(hw)
                    if hw["@label"] is None:
                        continue
                    else:
                        save_image_path = await self.__process_image(image_path, index)

                        await self.__process_label(save_image_path, ENCODED_LABELS[hw['@label']], hw_bbox, float(handwritten['width']), float(handwritten['height']), handwritten_checkbox)


    async def __process_image(self, image_path, index):
        """ This method process an image and stores locally """

        img_path = image_path.replace(RAW_DATASET_PATH, '')
        img_path = os.path.join(SAVE_DATASET_PATH, os.path.join("images", "_".join(img_path.split('/')[1:3]) + f'_hw-{index}.jpg'))

        shutil.copy(image_path, img_path)
        return img_path

    async def __process_label(self, image_path, label, bbox, width, height, handwritten_annotation):
        """ This method stores label of the image locally """

        label_path = image_path.replace('images', 'labels')
        label_path = label_path.replace('jpg', 'txt')

        xtl, ytl, xbr, ybr = await handwritten_annotation.to_yolo_bbox(height, width, bbox)

        async with aiofiles.open(label_path, 'a+') as f:
            await f.write(f'{label} {xtl} {ytl} {xbr} {ybr}\n')

    async def __generate_dataset(self):
        """ This method generates datasets and stores locally """

        global progress_bar
        while not self.files_q.empty():
            file_dir = self.files_q.get()

            try:
                annotation_objects = {}

                annotation_file_path = await get_annotation_full_path(file_dir, 'Handwritten_Checkbox')
                annotation_objects['Handwritten_Checkbox'] = await CVATHelper(annotation_file_path)

                annotations = await self.__get_required_annotations(annotation_objects, annotation_file_path)
                await self.__get_handwritten_checkbox_annotations(annotations, annotation_objects["Handwritten_Checkbox"])

                with open(SUCCESSFUL_FILES, "a+") as write_file:
                    write_file.write(file_dir + "\n")

            except Exception as e:
                print('%s -> %s' % (e, traceback.format_exc()))

                with open(UNSUCCESSFUL_FILES, "a+") as write_file:
                    write_file.write(file_dir + "\n")
            progress_bar.update()

    async def filter_annotation_path_by_project(self, project, raw_dataset) -> list or None:
        """
        The method returns all annotation filepath in the given project Eg: Split_Turn

        :param project: name of the project
        :param raw_dataset: path to raw dummydataset
        :return: list of annotation files in the project
        """
        dataset_path = raw_dataset + "/**/*/annotations.xml"
        sub_dir_dataset = raw_dataset + "/***/**/*/annotations.xml"
        paths = [os.path.dirname(os.path.dirname(file)) for file in glob(dataset_path) if project in file]
        paths_sub_dir = [os.path.dirname(os.path.dirname(file)) for file in glob(sub_dir_dataset) if project in file]
        paths.extend(paths_sub_dir)
        if paths:
            return paths
        else:
            return None

    async def filter_common_annotation_by_projects(self, projects, raw_dataset) -> list:
        """
        The method find common annotation files between the project name using intersection.
        Eg: Document Structure and Split_Turn

        :param projects: list of project names
        :param raw_dataset: path to raw dummydataset
        :return: list of annotation files with all projects
        """
        annotation_files = await self.filter_annotation_path_by_project(projects[0], raw_dataset)

        return annotation_files

    async def __fill_queue(self):
        """ fill queue with files which are not already processed """

        global progress_bar
        file_list = await self.filter_common_annotation_by_projects(PROJECTS, RAW_DATASET_PATH)
        files = []
        if os.path.exists(SUCCESSFUL_FILES):
            async with aiofiles.open(SUCCESSFUL_FILES, 'r') as f:
                files = await f.readlines()

        processed_items = [file.strip() for file in files]
        queue_list = []
        for file in file_list:
            if file not in processed_items:
                self.files_q.put(file)
                queue_list.append(file)
        print(f'Queue filled with {self.files_q.qsize()} files.')
        progress_bar = tqdm(total=self.files_q.qsize())

    async def generate(self):
        try:
            await self.__fill_queue()
            if not self.files_q.empty():
                await self.__generate_dataset()
                print('Done!!!')
        except Exception as e:
            print('%s -> %s' % (e, traceback.format_exc()))


async def main():
    dataset = await HandwrittenDatasetGeneration()
    await dataset.generate()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
