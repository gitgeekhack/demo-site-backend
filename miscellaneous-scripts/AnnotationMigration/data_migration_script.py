import asyncio
import os
import traceback
from queue import Queue

import aiofiles
import uuid
from PyPDF2 import PdfFileReader
from tqdm import tqdm
from datetime import datetime, timezone
from manage import logger

from database.queries import insert_document_details, get_document_hash_from_id, \
    insert_project_detail, insert_annotation_user, insert_task_detail, insert_document_task_map, \
    insert_task_status, insert_status, insert_annotation_type, insert_label, insert_label_details, \
    insert_task_label_map, insert_sublabel_detail, insert_annotation_detail
from helper import generate_md5_hash, xml_to_dict, get_pdf_file_path, get_split_dirs, \
    get_project_dirs, create_split_pdf, UnsuccessfulProcess
from database import get_db_connection, close_conn
from dotenv import load_dotenv
from threading import Thread

load_dotenv()
unprocessed_annotations = Queue()
global progress_bar


FIXED_S3_URL = os.getenv('FIXED_S3_URL')
SUCCESSFULLY_PROCESSED_PATH = os.getenv('SUCCESSFULLY_PROCESSED_PATH')
UNSUCCESSFUL_PROCESSED_PATH = os.getenv('UNSUCCESSFUL_PROCESSED_PATH')
RAW_DATA_PATH = os.getenv('RAW_DATA_PATH')

if not FIXED_S3_URL:
    print('Configuration incomplete, Please set FIXED_S3_URL')
    exit(1)
if not SUCCESSFULLY_PROCESSED_PATH:
    print('Configuration incomplete, Please set SUCCESSFULLY_PROCESSED_PATH')
    exit(1)
if not UNSUCCESSFUL_PROCESSED_PATH:
    print('Configuration incomplete, Please set UNSUCCESSFUL_PROCESSED_PATH')
    exit(1)
if not RAW_DATA_PATH:
    print('Configuration incomplete, Please set RAW_DATA_PATH')
    exit(1)


def load_queue():
    """
    Loads queue with files that are remaining to be processed
    """
    global unprocessed_annotations
    global progress_bar
    successfully_processed = []
    if os.path.exists(SUCCESSFULLY_PROCESSED_PATH):
        with open(SUCCESSFULLY_PROCESSED_PATH, 'r') as f:
            successfully_processed = f.readlines()
    with open("incomplete_tasks.txt", 'r') as f:
        valid_process_files = f.readlines()
    successful_files = [s.replace("\n", "") for s in successfully_processed]
    valid_files = [v.replace("\n", "") for v in valid_process_files]
    file_list = os.listdir(RAW_DATA_PATH)
    for file in file_list:
        file_path = os.path.join(RAW_DATA_PATH, file)
        if file_path not in successful_files and os.path.basename(file_path) in valid_files:
            unprocessed_annotations.put(file_path)
    print(f'Queue filled with {unprocessed_annotations.qsize()} files.')
    progress_bar = tqdm(total=unprocessed_annotations.qsize())


async def insert_parent_doc_details(conn, dir_p, pdf_file_path, created_date, correlation_id):
    """
    Inserts parent document details to the Document Detail table
    """
    doc_details = {}
    doc_details["parent_total_pages"] = len(PdfFileReader(open(pdf_file_path, 'rb'), strict=False).pages)
    doc_details["doc_name"] = os.path.basename(dir_p)
    doc_details["hashed_doc_name"] = generate_md5_hash(pdf_file_path) + ".pdf"
    doc_details["parent_doc_id"] = None
    doc_details["doc_s3_url"] = (FIXED_S3_URL + doc_details["doc_name"] + "/" + doc_details["doc_name"])\
        .replace(" ", "+")
    doc_details["parent_page_start"] = None
    doc_details["created_date"] = created_date
    doc_details["updated_date"] = datetime.utcnow()
    parent_doc_id = await insert_document_details(conn, doc_details)
    if not parent_doc_id:
        raise UnsuccessfulProcess("Parent Document details not inserted")
    logger.info("Updated Parent document details for Correlation ID = {}, Document Name = {}, Parent Document ID: {}"
                .format(correlation_id, os.path.basename(dir_p), parent_doc_id))
    return parent_doc_id


async def insert_split_doc_details(conn, split_dir_p, pdf_file_path, parent_doc_id, created_date, correlation_id):
    """
    Creates split pdf and stores in the same directory and inserts its details to Document Detail table
    """
    doc_details = {}
    split_name = os.path.basename(split_dir_p)
    split_start = int(split_name.rsplit("-")[0])
    split_end = int(split_name.rsplit("-")[-1])
    doc_details["parent_total_pages"] = split_end - split_start + 1
    create_split_pdf(pdf_file_path, split_dir_p, split_start, split_end)
    split_pdf_file_path = split_dir_p + "/" + split_name + "." + os.path.basename(pdf_file_path)
    logger.info("Generated and saved split pdf: {}".format(os.path.basename(split_pdf_file_path)))
    doc_details["doc_name"] = split_name + "." + os.path.basename(pdf_file_path)
    doc_details["hashed_doc_name"] = generate_md5_hash(split_pdf_file_path) + ".pdf"
    doc_details["parent_doc_id"] = parent_doc_id
    doc_details["doc_s3_url"] = None
    doc_details["parent_page_start"] = split_start
    doc_details["created_date"] = created_date
    doc_details["updated_date"] = datetime.utcnow()
    split_doc_id = await insert_document_details(conn, doc_details)
    if not split_doc_id:
        raise UnsuccessfulProcess("Split Document Details not inserted for split: {}, Parent Document: {}".format(split_name, os.path.basename(pdf_file_path)))
    logger.info("Updated Split document details for Correlation ID = {}, Document Name = {}, Split Document ID: {}"
                .format(correlation_id, split_name + "." + os.path.basename(pdf_file_path), split_doc_id))
    return split_doc_id


async def update_task_status(conn, task_id, created_date, correlation_id):
    """
    Updates task status to TaskStatus table
    """
    status_details = {}
    status_details["status"] = "completed"
    status_details["created_date"] = created_date
    status_details["updated_date"] = datetime.utcnow()
    status_id = await insert_status(conn, status_details)
    await insert_task_status(conn, task_id, status_id)
    logger.info("Updated Task Status for Correlation ID: {}, Status ID: {}, Task Detail ID: {}".format(correlation_id, status_id, task_id))


async def update_sublabel_details(conn, label_detail_id, label_name, attributes, created_date, label_sublabel_details):
    """
    Updates sublabel details to the SublabelDetail Table
    """
    all_sublabel_details = []
    sublabels = [attributes] if isinstance(attributes, dict) else attributes
    coros = []

    async def sublabel_insert(sublabel):
        sublabel_details = {}
        sublabel_details["Name"] = sublabel["@name"]
        sublabel_details["Value"] = sublabel["#text"] if '#text' in sublabel.keys() else "None"
        sublabel_details["Type"] = label_sublabel_details[label_name][sublabel_details["Name"]]
        sublabel_details["created_date"] = created_date
        sublabel_details["updated_date"] = datetime.utcnow()
        all_sublabel_details.append(sublabel_details)

    for sublabel in sublabels:
        coros.append(sublabel_insert(sublabel))
    await asyncio.gather(*coros)
    await insert_sublabel_detail(conn, label_detail_id, all_sublabel_details)


async def update_annotation_details(conn, label_detail_id, box_details, created_date):
    """
    Updates annotation details to AnnotationDetail table
    """
    annotation_details = {}
    annotation_details["X0"] = box_details["@xtl"]
    annotation_details["Y0"] = box_details["@ytl"]
    annotation_details["X1"] = box_details["@xbr"]
    annotation_details["Y1"] = box_details["@ybr"]
    await insert_annotation_detail(conn, label_detail_id, annotation_details, created_date)


async def modify_label_sublabel_details(labels_obj):
    """
    Creates a mapping for the labels, its sublabels and their input types
    """
    sublabel_input_types = {}
    labels = [labels_obj] if isinstance(labels_obj, dict) else labels_obj
    for label in labels:
        if label["attributes"]:
            sublabel_input_types[label["name"]] = {}
            attribute_labels = [label["attributes"]["attribute"]] if isinstance(label["attributes"]["attribute"],
                                                                                dict) else label["attributes"][
                "attribute"]
            for attribute in attribute_labels:
                sublabel_input_types[label["name"]][attribute['name']] = attribute["input_type"]
    return sublabel_input_types


async def insert_box_details(conn, task_detail_id, image, xml_obj):
    """
    Inserts label details to LabelDetail table if box entity found in image
    """
    label_details = {}
    page_number = int(image["@id"]) + 1
    coros = []

    async def insert_box_op(box_details):
        annotation_type = 'rectangle'
        label_details["annotation_type_id"] = await insert_annotation_type(conn, annotation_type)
        label_details["page_number"] = page_number
        label_details["label_id"] = await insert_label(conn, box_details['@label'])
        created_date = xml_obj["meta"]["task"]["created"]
        label_details["created_date"] = created_date
        label_details["updated_date"] = datetime.utcnow()
        label_detail_id = await insert_label_details(conn, label_details)
        if not label_detail_id:
            raise UnsuccessfulProcess("Label Detail not inserted for Task Id: {}".format(task_detail_id))
        await insert_task_label_map(conn, task_detail_id, label_detail_id)
        label_sublabel_details = await modify_label_sublabel_details(xml_obj["meta"]["task"]["labels"]["label"])
        if 'attribute' in box_details.keys():
            await update_sublabel_details(conn, label_detail_id, box_details['@label'], box_details["attribute"],
                                          created_date, label_sublabel_details)
        await update_annotation_details(conn, label_detail_id, box_details, created_date)

    if 'box' in image.keys():
        boxes = [image['box']] if isinstance(image['box'], dict) else image['box']
        for box in boxes:
            coros.append(insert_box_op(box))

    await asyncio.gather(*coros)


async def insert_polyline_details(conn, task_detail_id, image, xml_obj):
    """
        Inserts label details to LabelDetail table if polyline entity found in image
    """
    label_details = {}
    page_number = int(image["@id"]) + 1
    coros = []

    async def insert_polyline_op(polyline_details):
        annotation_type = 'polyline'
        label_details["annotation_type_id"] = await insert_annotation_type(conn, annotation_type)
        label_details["page_number"] = page_number
        label_details["label_id"] = await insert_label(conn, polyline_details['@label'])
        created_date = xml_obj["meta"]["task"]["created"]
        label_details["created_date"] = created_date
        label_details["updated_date"] = datetime.utcnow()
        label_detail_id = await insert_label_details(conn, label_details)
        if not label_detail_id:
            raise UnsuccessfulProcess("Label Detail not inserted for Task Id: {}".format(task_detail_id))

        await insert_task_label_map(conn, task_detail_id, label_detail_id)
        label_sublabel_details = await modify_label_sublabel_details(xml_obj["meta"]["task"]["labels"]["label"])
        if 'attribute' in polyline_details.keys():
            await update_sublabel_details(conn, label_detail_id, polyline_details['@label'],
                                          polyline_details["attribute"], created_date, label_sublabel_details)
        points = polyline_details["@points"].rsplit(";")
        polyline_details["@xtl"] = float(points[0].rsplit(",")[0])
        polyline_details["@ytl"] = float(points[0].rsplit(",")[1])
        polyline_details["@xbr"] = float(points[1].rsplit(",")[0])
        polyline_details["@ybr"] = float(points[1].rsplit(",")[1])
        await update_annotation_details(conn, label_detail_id, polyline_details, created_date)

    if 'polyline' in image.keys():
        polylines = [image['polyline']] if isinstance(image['polyline'], dict) else image['polyline']
        for polyline in polylines:
            coros.append(insert_polyline_op(polyline))

    await asyncio.gather(*coros)


async def update_label_details(conn, task_detail_id, xml_obj, correlation_id, project_name):
    """
    Inserts label details to LabelDetail table
    """
    image_annotations = xml_obj["image"]
    image_labels = [image_annotations] if isinstance(image_annotations, dict) else image_annotations
    for image in image_labels:
        await insert_box_details(conn, task_detail_id, image, xml_obj)
        await insert_polyline_details(conn, task_detail_id, image, xml_obj)
    logger.info("All Label details, its sublabel and annotation details inserted for Document with Correlation ID: {} for project: {}, Task Detail ID: {}"
                .format(correlation_id, project_name, task_detail_id))


async def update_task_details(conn, parent_doc_id, project_dir_path, xml_obj, correlation_id):
    """
    Updates task details to TaskDetail table
    """
    task_details = {}
    doc_hash = await get_document_hash_from_id(conn, parent_doc_id)
    task_server_id = xml_obj["meta"]["task"]["name"].rsplit(".")[0]
    doc_name = xml_obj["meta"]["task"]["name"].replace(task_server_id + ".", "")
    task_name = task_server_id.replace("id", doc_hash)
    project_name = project_dir_path.rsplit("/")[-1].rsplit("-")[0].replace("_", "/")

    task_details["task_name"] = xml_obj["meta"]["task"]["name"]
    task_details["project_id"] = await insert_project_detail(conn, project_name)
    if xml_obj["meta"]["task"]["assignee"]:
        task_details["assignee_id"] = \
            await insert_annotation_user(conn, xml_obj["meta"]["task"]["assignee"]["username"])
    task_details["reviewer_id"] = -1
    task_details["task_url"] = (FIXED_S3_URL + doc_name + "/" +
                                project_dir_path.rsplit("/")[-1] + ".zip").replace(" ", "+")  # project directory name
    task_details["task_id"] = xml_obj["meta"]["task"]["id"]
    created_date = xml_obj["meta"]["task"]["created"]
    task_details["created_date"] = created_date
    task_details["updated_date"] = datetime.utcnow()
    task_detail_id = await insert_task_detail(conn, task_details)
    if not task_detail_id:
        raise UnsuccessfulProcess("Task Detail not inserted for Parent Document ID: {}".format(parent_doc_id))
    logger.info("Updated Task Details for Document: {}, Correlation ID: {}".format(doc_name, correlation_id))
    await update_task_status(conn, task_detail_id, created_date, correlation_id)
    await insert_document_task_map(conn, parent_doc_id, task_detail_id)
    logger.info("Updated Document Task Map for Document: {}, Task: {}, Correlation ID: {}, Task Detail ID: {}"
                .format(doc_name, project_name, correlation_id, task_detail_id))
    return task_detail_id


async def update_project_details_from_xml(conn, parent_doc_id, project_dir_path, xml_dict, correlation_id):
    """
    Extracts details from xml using different processes and updates the required tables
    """
    xml_obj = xml_dict["annotations"]
    task_detail_id = await update_task_details(conn, parent_doc_id, project_dir_path, xml_obj, correlation_id)
    project_name = project_dir_path.rsplit("/")[-1].rsplit("-")[0].replace("_", "/")
    await update_label_details(conn, task_detail_id, xml_obj, correlation_id, project_name)


async def process_files():
    """
    Processes files one by one from the queue
    """
    global progress_bar
    global unprocessed_annotations
    while not unprocessed_annotations.empty():
        conn = get_db_connection()
        dir_path = unprocessed_annotations.get()
        correlation_id = str(uuid.uuid4())
        try:
            logger.info("Processing document: {} -> Correlation ID: {}"
                        .format(os.path.basename(dir_path), correlation_id))
            pdf_file_path = get_pdf_file_path(dir_path)
            parent_project_dirs = get_project_dirs(dir_path)
            if parent_project_dirs:
                split_turn_xml_path = parent_project_dirs + "/" + "annotations.xml"
                xml_dict = xml_to_dict(split_turn_xml_path)
                created_date = xml_dict["annotations"]["meta"]["task"]["created"]
                parent_doc_id = \
                    await insert_parent_doc_details(conn, dir_path, pdf_file_path, created_date, correlation_id)
                await update_project_details_from_xml(conn, parent_doc_id, parent_project_dirs, xml_dict, correlation_id)
            else:
                created_date = datetime.now(timezone.utc)
                parent_doc_id = \
                    await insert_parent_doc_details(conn, dir_path, pdf_file_path, created_date, correlation_id)
            logger.info("Parent Document details inserted for {}, Correlation ID: {}"
                        .format(os.path.basename(dir_path), correlation_id))
            split_dirs_path = get_split_dirs(dir_path)
            valid_projects = ['RE Turn', 'RE Sections', 'RE Document Structure', 'RE Entities', 'RE Costs&Time',
                              'Named Entities', 'Medical Entities', 'Handwritten_Checkbox', 'Sections',
                              'Document Structure', 'Split_Turn']
            inserted_split_doc_ids = []
            async def insert_split_doc_data(split_dir_path):
                split_doc_id = await insert_split_doc_details(conn, split_dir_path, pdf_file_path,
                                                              parent_doc_id, created_date, correlation_id)
                logger.info("Split Document details inserted for {}, Correlation ID: {}"
                            .format(os.path.basename(split_dir_path) + "." + os.path.basename(dir_path), correlation_id))
                split_project_dirs = [project_dir for project_dir in os.listdir(split_dir_path)
                                      for name in valid_projects if os.path.isdir(split_dir_path + "/" + project_dir)
                                      and project_dir.startswith(name)]

                async def insert_split_proj_details(split_project_dir_name):
                    split_xml_path = split_dir_path + "/" + split_project_dir_name + "/annotations.xml"
                    split_xml_dict = xml_to_dict(split_xml_path)
                    await update_project_details_from_xml(conn, split_doc_id,
                                                          split_dir_path + "/" + split_project_dir_name,
                                                          split_xml_dict, correlation_id)

                split_proj_coros = []
                for split_project_dir in split_project_dirs:
                    split_proj_coros.append(insert_split_proj_details(split_project_dir))
                inserted_split_doc_ids.append(split_doc_id)
                await asyncio.gather(*split_proj_coros)

            split_dir_coros = []
            for split_dir_path in split_dirs_path:
                split_dir_coros.append(insert_split_doc_data(split_dir_path))

            await asyncio.gather(*split_dir_coros)
            async with aiofiles.open(SUCCESSFULLY_PROCESSED_PATH, 'a+') as f:
                await f.write(dir_path + '\n')
            logger.info("Complete details for {} updated, Document detail ID: {}, Corresponding Split Doc IDs: {}".format(os.path.basename(dir_path), parent_doc_id,inserted_split_doc_ids))
            progress_bar.update()
        except (UnsuccessfulProcess,Exception, KeyboardInterrupt) as e:
            logger.error(f'%s -> %s for Correlation ID: %s', e, traceback.format_exc(), correlation_id)
            progress_bar.update()
            async with aiofiles.open(UNSUCCESSFUL_PROCESSED_PATH, 'a+') as f:
                await f.write(dir_path + '\n')
        close_conn(conn)


async def main():
    print(f"{datetime.utcnow().isoformat()} started a thread\n")
    file_coroutines = [process_files() for _ in range(2)]
    await asyncio.gather(*file_coroutines)


def make_faster():
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
    logger.info(f'Migration Completed')
    exit(1)

load_queue()

thread_list = []
for i in range(48):
    thr = Thread(target=make_faster)
    thread_list.append(thr)

for t in thread_list:
    t.start()

for t in thread_list:
    t.join()


