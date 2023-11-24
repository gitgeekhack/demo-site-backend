import xml.etree.ElementTree as ET
import os
import traceback
import glob2
import re
import pydash
from datetime import datetime


BUCKET_STORE_DIR = ''
REQUIRED_LABEL = 'SEC_CARE_PLAN'


def escape_name(file):
    return re.sub(r'/', '_', file, flags=re.MULTILINE)


async def is_latest_anno(tree, updated_xml_path):
    existing_tree = ET.parse(updated_xml_path)
    existing_root_node = existing_tree.getroot()
    meta_info = existing_root_node.find('meta')
    export_info = meta_info.find('dumped')
    existing_time_stamp = export_info.text

    root_node = tree.getroot()
    meta_info = root_node.find('meta')
    export_info = meta_info.find('dumped')
    new_time_stamp = export_info.text

    timestamp1 = datetime.strptime(existing_time_stamp, '%Y-%m-%d %H:%M:%S.%f%z')
    timestamp2 = datetime.strptime(new_time_stamp, '%Y-%m-%d %H:%M:%S.%f%z')

    if timestamp2 > timestamp1:
        return True
    else:
        return False


async def save_updated_xml(tree, xml_path):
    dir_path = os.path.dirname(os.path.dirname(xml_path))
    save_dir = os.path.join(BUCKET_STORE_DIR, dir_path, 'SubSections')
    os.makedirs(save_dir, exist_ok=True)
    updated_xml_path = os.path.join(BUCKET_STORE_DIR, save_dir, 'annotations.xml')

    if os.path.exists(updated_xml_path):
        if await is_latest_anno(tree, updated_xml_path):
            tree.write(updated_xml_path)
            return updated_xml_path.replace(BUCKET_STORE_DIR, "").strip('/')
    else:
        tree.write(updated_xml_path)
        return updated_xml_path.replace(BUCKET_STORE_DIR, "").strip('/')


async def filter_name(xml_path, sec_care_plan):
    tree = ET.parse(os.path.join(BUCKET_STORE_DIR, xml_path))
    root_node = tree.getroot()

    image_nodes = root_node.findall('image')
    for i, img in enumerate(image_nodes):
        to_delete = []
        for child_node in img:
            if child_node.tag == 'box':
                if child_node.attrib['label'] != 'NAME':
                    to_delete.append(child_node)
        for item in to_delete:
            img.remove(item)
        for name in sec_care_plan.get(i, []):
            img.append(name)

    return await save_updated_xml(tree, xml_path)


async def filter_sec_care_plan(xml_path):
    tree = ET.parse(os.path.join(BUCKET_STORE_DIR, xml_path))
    root_node = tree.getroot()

    image_nodes = root_node.findall('image')
    to_add = {}

    for i, img in enumerate(image_nodes):
        to_add[i] = []
        for child_node in img:
            if child_node.tag == 'box':
                if child_node.attrib['label'] == REQUIRED_LABEL:
                    to_add[i].append(child_node)

    return to_add


async def filter_name_and_save(xml_path):
    tree = ET.parse(os.path.join(BUCKET_STORE_DIR, xml_path))
    root_node = tree.getroot()

    image_nodes = root_node.findall('image')
    for i, img in enumerate(image_nodes):
        to_delete = []
        for child_node in img:
            if child_node.tag == 'box':
                if child_node.attrib['label'] != 'NAME':
                    to_delete.append(child_node)
        for item in to_delete:
            img.remove(item)

    return await save_updated_xml(tree, xml_path)


async def get_section_anno_filepath(named_entities_xml_path):
    parent_path = os.path.dirname(os.path.dirname(named_entities_xml_path))
    parent_full_path = os.path.join(BUCKET_STORE_DIR, parent_path)
    all_xml_files = glob2.glob(parent_full_path + '/**/*.xml')
    project_find_key = f'/{escape_name("Sections")}-'
    section_xmls = pydash.filter_(all_xml_files, lambda x: x.find(project_find_key) != -1)
    if section_xmls:
        return section_xmls[0]


async def main(named_entities_xml_path):
    section_xml_path = await get_section_anno_filepath(named_entities_xml_path)

    if section_xml_path:
        sec_care_plan = await filter_sec_care_plan(section_xml_path)
        saved_path = await filter_name(named_entities_xml_path, sec_care_plan)
    else:
        saved_path = await filter_name_and_save(named_entities_xml_path)
    return saved_path


async def get_updated_xmls(section_xmls):
    updated_xmls = []
    for file in section_xmls:
        try:
            saved_path = await main(file)
            if saved_path:
                updated_xmls.append(saved_path)
        except Exception as e:
            print('%s -> %s' % (e, traceback.format_exc()))

    return list(set(updated_xmls))
