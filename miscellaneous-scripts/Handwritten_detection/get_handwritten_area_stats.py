# generate stats related to handwritten data in csv
# stats format
# Image_name  |	height |    width   |	Handwritten perc  |	Signature perc |	Total Perc (Handwritten + Signature)

import os
import cv2
import pandas as pd
import asyncio
from tqdm import tqdm

REQUIRED_COLUMNS = ['Image_name', 'Height', 'Width', 'Handwritten Percentage', 'Signature Percentage',
                                   'Total Percentage (Handwritten + Signature)']

class HandwrittenStatsExtraction:

    def __calculate_iou(self, bbox1, bbox2):
        """
        The asynchronous method implements the intersection over union (IoU) between bbox1 and bbox2

        :param bbox1: first box, list object with coordinates (x1, y1, x2, y2)
        :param bbox2: second box, list object with coordinates (x1, y1, x2, y2)
        :return iou: intersection over union (IoU) of the 2 given boxes

        """
        x1 = max(bbox1[0], bbox2[0])
        y1 = max(bbox1[1], bbox2[1])
        x2 = min(bbox1[2], bbox2[2])
        y2 = min(bbox1[3], bbox2[3])
        inter_area = max(0, abs(x2 - x1 + 1)) * max(0, abs(y2 - y1 + 1))
        box1_area = (abs(bbox1[2] - bbox1[0]) + 1) * (abs(bbox1[3] - bbox1[1]) + 1)
        box2_area = (abs(bbox2[2] - bbox2[0]) + 1) * (abs(bbox2[3] - bbox2[1]) + 1)
        if float(box1_area + box2_area - inter_area) > 0:
            iou = inter_area / float(box1_area + box2_area - inter_area)
            return iou
        else:
            return None


    async def __get_bigger_bbox(self, bbox, bboxes):
        """
        Calculates the iou for the given bbox with other bboxes and extracts the bigger bounding box from them
        """
        iou_comp = [self.__calculate_iou(bbox[1:], comp_bbox[1:]) for comp_bbox in bboxes]
        coinciding_iou = [i for i in iou_comp if i is not None and i > 0.7 and i != 1]
        if len(coinciding_iou) == 0:
            return bbox
        else:
            max_iou_index = iou_comp.index(max(coinciding_iou))
            bbox1_area = abs(bbox[3] - bbox[1]) * abs(bbox[4] - bbox[2])
            bbox2_area = abs(bboxes[max_iou_index][3] - bboxes[max_iou_index][1]) * abs(bboxes[max_iou_index][4] -
                                                                                        bboxes[max_iou_index][2])
            if bbox1_area > bbox2_area:
                return bbox
            else:
                return bboxes[max_iou_index]


    async def __calculate_handwritten_area(self, data, height, width):
        """
        Intakes labels of the image as data, height and width of the image and gives out handwritten and signature area
        """
        handwritten_area = 0
        sign_area = 0
        bboxes = []
        filtered_bboxes = []
        for dt in data:
            i, x, y, w, h = map(float, dt.split(' '))
            l = int((x - w / 2) * width)
            r = int((x + w / 2) * width)
            t = int((y - h / 2) * height)
            b = int((y + h / 2) * height)
            bboxes.append([i, l, t, r, b])

        if len(bboxes) == 1:
            filtered_bboxes.append(bboxes[0])

        else:
            for bbox in bboxes:
                bigger_bbox = await self.__get_bigger_bbox(bbox, bboxes)
                filtered_bboxes.append(bigger_bbox)

        area_bboxes = []
        for bbox in filtered_bboxes:
            if bbox not in area_bboxes:
                area_bboxes.append(bbox)

        for bbox in area_bboxes:
            area = abs(bbox[3] - bbox[1]) * abs(bbox[4] - bbox[2])
            if bbox[0] == 0:
                handwritten_area = handwritten_area + area
            else:
                sign_area = sign_area + area
        return handwritten_area, sign_area


    async def get_handwritten_statistics(self, img_path):
        """
        Intakes image path and retrieves stats for the image as row dataframe
        """
        req_details = []

        img = cv2.imread(img_path)
        height, width, _ = img.shape
        img_area = height * width

        image_name = os.path.basename(img_path)
        req_details.extend([image_name, height, width])

        with open(labels_dir + image_name.replace("jpg", "txt"), 'r') as read_file:
            data = read_file.readlines()
            total_hw_area, total_sig_area = await self.__calculate_handwritten_area(data, height, width)
            hw_area_perc = (total_hw_area/img_area) * 100
            sig_area_perc = (total_sig_area/img_area) * 100
            total_perc = hw_area_perc + sig_area_perc
            req_details.extend([hw_area_perc, sig_area_perc, total_perc])
            row = pd.DataFrame([req_details], columns=REQUIRED_COLUMNS)
        return row


    async def main(self):
        stats_df = pd.DataFrame(columns=REQUIRED_COLUMNS)
        rows = []
        for image in images:
            img_path = images_dir + image
            row = await self.get_handwritten_statistics(img_path)
            rows.append(row)
            progress_bar.update()

        for row in rows:
            stats_df = pd.concat([stats_df, row])
        stats_df.to_csv("Handwritten_stats_data.csv")


if __name__ == "__main__":
    images_dir = os.getenv('IMAGE_DIR')
    labels_dir = os.getenv('LABEL_DIR')
    images = os.listdir(images_dir)

    handwritten_obj = HandwrittenStatsExtraction()

    progress_bar = tqdm(total=len(images))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(handwritten_obj.main())



