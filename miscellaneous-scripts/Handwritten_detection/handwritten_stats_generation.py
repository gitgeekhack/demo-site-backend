import asyncio
import os
import xmltodict
from tqdm import tqdm
import json
from dotenv import load_dotenv

load_dotenv()

DATASET_DIR = os.getenv('DATASET_DIR')
PROJECT_KEYWORDS = ['Split_Turn','Document Structure', 'Handwritten_Checkbox', 'Named Entities', 'Sections']

class HandwrittenDataStats:
    LAYOUTS = ['TITLE', 'SUBTITLE', 'CONTENT', 'FORM', 'HEADER_FOOTER', 'OTHER', 'TABLE', 'QUESTIONNAIRE', 'REP_HEADER_FOOTER']
    SECTIONS = ['Impression', 'SEC_CARE_PLAN', 'SEC_DIAGNOSIS', 'SEC_GEN_INFO', 'SEC_OBJECTIVE', 'SEC_PMH_BAD', 'SEC_PMH_GOOD', 'SEC_REVIEW', 'SEC_SUBJECTIVE']

    def __init__(self, dir_path):
        self.dir_path = dir_path

    def __xml_to_dict(self, xml_path):
        """
        Converts xml file to dictionary
        """
        with open(xml_path, 'r', encoding='utf-8') as file:
            my_xml = file.read()
        my_dict = xmltodict.parse(my_xml)
        return my_dict

    async def __get_split_dirs(self):
        """
        Retrieves the list of split directories for a parent document
        """
        split_dirs = [i for i in os.listdir(self.dir_path) if os.path.isdir(os.path.join(self.dir_path, i)) and not i.startswith('Split_Turn')]
        return split_dirs

    async def __get_xml_paths_by_projects(self, split_dir_path):
        """
        A Split directory may contain various project directories which have their annotations inside.
        This function retrieves the paths for those xml annotation files.
        """
        project_xml_paths = {project.rsplit("-")[0].replace(" ", "_") + "_xml_path": os.path.join(split_dir_path, project, "annotations.xml")
                    for project in os.listdir(split_dir_path)
                    if project.rsplit("-")[0] in PROJECT_KEYWORDS and os.path.isdir(os.path.join(split_dir_path, project))
                    and os.path.exists(os.path.join(split_dir_path, project, "annotations.xml"))}
        return project_xml_paths

    async def __get_doc_type(self, box_annots):
        """
        This function gives out document type of split pdf using its annotations.
        """
        box_attributes = [box_annots['attribute']] if isinstance(box_annots['attribute'], dict) else box_annots['attribute']
        for attr in box_attributes:
            if attr["@name"] == 'doc_type':
                return attr["#text"]

    async def __create_split_doctype_mapping(self, split_turn_path):
        """
        Creates a mapping for each split document and its doc type from the Split/Turn project
        """
        split_turn_dict = self.__xml_to_dict(split_turn_path)
        split_doc_type = {}
        images = [split_turn_dict["annotations"]["image"]] if isinstance(split_turn_dict["annotations"]["image"], dict) else split_turn_dict["annotations"]["image"]
        for image in images:
            if 'box' in image.keys():
                boxes = [image['box']] if isinstance(image['box'], dict) else image['box']
                for box in boxes:
                    if box['@label'] == 'SPLIT':
                        doc_type = await self.__get_doc_type(box)
                        split_doc_type[int(image["@id"]) + 1] = doc_type
        return split_doc_type

    async def __coinciding_bboxes_iou(self, box_a, box_b):  # boxA-small, boxB-big
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

    async def __get_handwritten_checkbox_stats(self, hw_bbox, sec_checkbox_bboxes):
        """
        This function provides a statistics for handwritten and section checkbox coincidence
        """
        iou_stats = [await self.__coinciding_bboxes_iou(hw_bbox, box) for box in sec_checkbox_bboxes]
        max_iou = max(iou_stats)
        is_coincide = False
        coinciding_checkbox_coords = None
        if 0.6 < max_iou <= 1:
            is_coincide = True
            coinciding_checkbox_coords = sec_checkbox_bboxes[iou_stats.index(max_iou)]
            return is_coincide, coinciding_checkbox_coords
        else:
            return is_coincide, coinciding_checkbox_coords

    async def __get_sec_checkbox_bboxes(self, boxes):
        """
        Intakes all the bounding box annotations and returns a list of bounding boxes of section checkbox
        """
        sec_checkbox_boxes = []
        for box in boxes:
            if box["@label"] == 'SEC_CHECKBOX':
                sec_checkbox_boxes.append([float(box["@xtl"]), float(box["@ytl"]), float(box["@xbr"]), float(box["@ybr"])])
        return sec_checkbox_boxes

    async def __modify_layout_details(self, layout_details):
        """
        Modifies the layout details into a dictionary
        """
        layouts = []
        for l in layout_details:
            req_details = {}
            req_details["label"] = l[1]
            req_details["co-ordinates"] = l[2]
            layouts.append(req_details)
        return layouts

    async def __get_required_layouts(self, layout_boxes, hw_bbox):
        """
        Gets the required layouts that coincide with the given handwritten bounding box
        """
        layout_dets = []
        for box in layout_boxes:
            bbox_cords = [float(box["@xtl"]), float(box["@ytl"]), float(box["@xbr"]), float(box["@ybr"])]
            iou = await self.__coinciding_bboxes_iou(hw_bbox, bbox_cords)
            if iou > 0.7:
                layout_dets.append([iou, box['@label'], bbox_cords])
            else:
                continue
        req_layouts = self.__modify_layout_details(layout_dets)
        return req_layouts

    async def __get_coinciding_layouts(self, layout_annots, page_number, hw_bbox):
        """
        Gets all the details of the layouts coinciding with the given handwritten bbox on the particular page
        """
        images = [layout_annots["annotations"]["image"]] if isinstance(layout_annots["annotations"]["image"], dict) else layout_annots["annotations"]["image"]
        for image_annots in images:
            if image_annots["@id"] == page_number:
                if 'box' in image_annots.keys():
                    layout_bboxes = [image_annots['box']] if isinstance(image_annots['box'], dict) else image_annots['box']
                    required_layout_details = self.__get_required_layouts(layout_bboxes, hw_bbox)
                    return required_layout_details

    async def __modify_section_details(self, section_details):
        """
        Modifies the required section details into a dictionary
        """
        sections = []
        for s in section_details:
            req_details = {}
            req_details["label"] = s[1]
            req_details["co-ordinates"] = s[2]
            sections.append(req_details)
        return sections

    async def __get_required_sections(self, section_boxes, hw_bbox):
        """
        Gets the required secrtions which coincide with the given handwritten bounding box
        """
        section_dets = []
        for box in section_boxes:
            bbox_cords = [float(box["@xtl"]), float(box["@ytl"]), float(box["@xbr"]), float(box["@ybr"])]
            iou = await self.__coinciding_bboxes_iou(hw_bbox, bbox_cords)
            if iou > 0.7:
                section_dets.append([iou, box['@label'], bbox_cords])
            else:
                continue
        required_sections = self.__modify_section_details(section_dets)
        return required_sections

    async def __get_coinciding_sections(self, section_annots, page_number, hw_bbox):
        """
        Gets all the details of the sections coinciding with the particular handwritten bounding box on the given page
        """
        images = [section_annots["annotations"]["image"]] if isinstance(section_annots["annotations"]["image"], dict) else section_annots["annotations"]["image"]
        for image_annots in images:
            if image_annots["@id"] == page_number:
                if 'box' in image_annots.keys():
                    section_bboxes = [image_annots['box']] if isinstance(image_annots['box'], dict) else image_annots['box']
                    required_section_details = self.__get_required_sections(section_bboxes, hw_bbox)
                    return required_section_details

    async def __get_required_handwritten_info(self, box, bbox_details, sec_checkbox_bboxes, layout_annots, section_annots, page_number):
        """
        If the bounding box label is found to be handwritten, it extracts extra required information and appends it to the dictionary
        """
        if box["@label"] == 'HANDWRITTEN':
            hw_bbox_coords = [float(box["@xtl"]), float(box["@ytl"]), float(box["@xbr"]), float(box["@ybr"])]
            if sec_checkbox_bboxes:
                is_coincide, coinciding_checkbox = await self.__get_handwritten_checkbox_stats(hw_bbox_coords,
                                                                                               sec_checkbox_bboxes)
                bbox_details["coincides with section checkbox?"] = is_coincide
                if is_coincide:
                    bbox_details["sec_checkbox co-ordinates"] = coinciding_checkbox
            if layout_annots:
                coinciding_bbox_by_label = await self.__get_coinciding_layouts(layout_annots, page_number, hw_bbox_coords)
                bbox_details["coinciding_layouts"] = coinciding_bbox_by_label
            if section_annots:
                coinciding_section_by_label = await self.__get_coinciding_sections(section_annots, page_number, hw_bbox_coords)
                bbox_details["coinciding_sections"] = coinciding_section_by_label
        return bbox_details

    async def __get_hw_bbox_details(self, boxes, layout_annots, section_annots, page_number):
        """
        Intakes bounding box annotations and returns a list of dictionaries containing
        all the required details of bounding boxes.
        """
        bboxes = []
        sec_checkbox_bboxes = await self.__get_sec_checkbox_bboxes(boxes)
        # get layout bounding boxes by label for the current page
        for box in boxes:
            bbox_details = {}
            bbox_details['bbox_co-ordinates'] = [float(box["@xtl"]), float(box["@ytl"]), float(box["@xbr"]), float(box["@ybr"])]
            bbox_details["label"] = box["@label"]
            modified_bbox_details = self.__get_required_handwritten_info(box, bbox_details, sec_checkbox_bboxes, layout_annots, section_annots, page_number)
            bboxes.append(modified_bbox_details)
        return bboxes

    async def generate_by_page_info(self, handwritten_annots, layout_annots, section_annots, split_dir, doctype_by_split):
        """
        Generates page by page info for each split pdf in the form of a list that contains dictionaries
        which contain required information for each page.
        """
        by_page_info = []
        for image_annots in handwritten_annots:
            curr_page_info = {}
            doc_details = {}
            doc_details["doc_name"] = os.path.basename(self.dir_path)
            doc_details["split_start"] = int(split_dir.rsplit("-")[0])
            doc_details["split_end"] = int(split_dir.rsplit("-")[1])

            curr_page_info["parent"] = doc_details
            curr_page_info["page_width"] = int(image_annots["@width"])
            curr_page_info["page_height"] = int(image_annots["@height"])
            curr_page_info['doc_type'] = doctype_by_split[int(split_dir.rsplit("-")[0])]
            curr_page_info["split_page_no"] = int(image_annots["@id"]) + 1

            page_number = image_annots["@id"]
            bbox_details = []
            if 'box' in image_annots.keys():
                boxes = [image_annots['box']] if isinstance(image_annots['box'], dict) else image_annots['box']
                bbox_details = await self.__get_hw_bbox_details(boxes, layout_annots, section_annots, page_number)
            if bbox_details:
                curr_page_info["bbox_details"] = bbox_details
            by_page_info.append(curr_page_info)
        return by_page_info

    async def get_required_stats(self):
        """
        Gets all the required stats for a parent document and returns lists for each split pdf,
        which further contain dictionaries by page information
        """
        split_turn_path = os.path.join(self.dir_path, [i for i in os.listdir(self.dir_path) if i.startswith('Split_Turn') and os.path.isdir(os.path.join(self.dir_path, i))][0], "annotations.xml")
        doctype_by_split = None
        if split_turn_path:
            doctype_by_split = await self.__create_split_doctype_mapping(split_turn_path)

        split_dirs = await self.__get_split_dirs()
        by_split_info = []
        for split_dir in split_dirs:
            project_xml_paths = await self.__get_xml_paths_by_projects(os.path.join(self.dir_path, split_dir))
            layout_annots = None
            section_annots = None
            if 'Document_Structure_xml_path' in project_xml_paths.keys():
                layout_annots = self.__xml_to_dict(project_xml_paths['Document_Structure_xml_path'])
            if 'Sections_xml_path' in project_xml_paths.keys():
                section_annots = self.__xml_to_dict(project_xml_paths['Sections_xml_path'])
            if 'Handwritten_Checkbox_xml_path' in project_xml_paths.keys():
                handwritten_annots = self.__xml_to_dict(project_xml_paths['Handwritten_Checkbox_xml_path'])
                handwritten_images = [handwritten_annots["annotations"]["image"]] if isinstance(handwritten_annots["annotations"]["image"], dict) else handwritten_annots["annotations"]["image"]
                split_info_by_page = await self.generate_by_page_info(handwritten_images, layout_annots, section_annots,split_dir, doctype_by_split) # list
                by_split_info.append(split_info_by_page)

        return by_split_info # split dictionary

async def main():
    docs = os.listdir(DATASET_DIR)
    progress_bar = tqdm(total=len(docs))
    doc_split_info = {}
    for doc in docs:
        doc_path = os.path.join(DATASET_DIR, doc)
        handwritten_obj = HandwrittenDataStats(doc_path)
        doc_info_by_split = await handwritten_obj.get_required_stats()
        if doc_info_by_split:
            doc_split_info[doc] = doc_info_by_split
        progress_bar.update()
    write_data = json.dumps(doc_split_info)
    with open("handwritten_stats.json", "w") as write_file:
        write_file.write(write_data)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


