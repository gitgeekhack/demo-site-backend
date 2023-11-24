import uuid

import psycopg2
from database import get_db_connection, close_conn, sqlconfig
import asyncio
from manage import logger


async def insert_document_details(conn, doc_details):
    """
    The method inserts details of document into DocumentDetail table.

    :param doc_details: dict containing various information related to document
    :return: id of the new document inserted in DocumentDetail table
    """
    total_pages = doc_details['parent_total_pages']
    doc_name = doc_details['doc_name']
    doc_hash = doc_details['hashed_doc_name']
    parent_doc_id = doc_details['parent_doc_id']
    s3_url = doc_details["doc_s3_url"]
    parent_page_start = doc_details["parent_page_start"]
    created_date = doc_details["created_date"]
    updated_date = doc_details["updated_date"]

    cursor = conn.cursor()
    query = sqlconfig['insert_document_detail']
    values = (total_pages, doc_name, doc_hash, parent_doc_id, s3_url, parent_page_start, created_date, updated_date)
    try:
        cursor.execute(query, values)
    except psycopg2.errors.UniqueViolation as e:
        conn.rollback()
        logger.info("Duplicate file detected: Document name {} Document hash: {}".format(doc_name, doc_hash))
        doc_hash = f'Duplicate_{doc_hash.replace(".pdf","")}_{str(uuid.uuid4())[:8]}.pdf'
        values = (total_pages, doc_name, doc_hash, parent_doc_id, s3_url, parent_page_start, created_date, updated_date)
        logger.info("New document hash generated for Document: {} Document hash: {}".format(doc_name, doc_hash))
        cursor.execute(query, values)
    document_id = cursor.fetchone()[0]
    conn.commit()
    return document_id


async def insert_task_detail(conn, task_details):
    """
    :param task_details: a dictionary containing all the task details
    :return: id of last inserted task record in TaskDetail table
    """
    task_name = task_details["task_name"]
    project_id = task_details["project_id"]
    assignee_id = task_details["assignee_id"] if "assignee_id" in task_details.keys() else -1
    reviewer_id = task_details["reviewer_id"]
    task_url = task_details["task_url"]
    cvat_task_id = task_details["task_id"]
    created_date = task_details["created_date"]
    updated_date = task_details["updated_date"]

    cursor = conn.cursor()
    query = sqlconfig['insert_task_detail']
    values = (task_name, project_id, assignee_id, reviewer_id, task_url, created_date, updated_date, cvat_task_id)
    cursor.execute(query, values)
    task_id = cursor.fetchone()[0]
    conn.commit()
    return task_id


async def get_document_hash_from_id(conn, doc_id):
    """
    The method returns document hash name from DocumentDetail table using its primary key DocumentDetailID.

    :param doc_id: primary key id of DocumentDetail table
    :return: DocumentMaskedName(document hash name) corresponding to doc_id
    """
    cursor = conn.cursor()
    query = sqlconfig['get_document_hash_name_from_id']
    values = (doc_id,)
    cursor.execute(query, values)
    document_name = cursor.fetchone()[0]
    return document_name


async def insert_project_detail(conn, project_name):
    """
    The method inserts project name into ProjectDetail table if not exists.

    :param project_name: Name of the project
    :return: id of project newly inserted or already present in table
    """
    cursor = conn.cursor()

    query = sqlconfig['get_project_id']
    values = (project_name,)
    cursor.execute(query, values)
    data = cursor.fetchone()
    if data:
        project_id = data[0]
    else:
        query = sqlconfig['insert_project_detail']
        cursor.execute(query, values)
        conn.commit()
        project_id = cursor.fetchone()[0]

    return project_id


async def insert_annotation_user(conn, username):
    """
    The method inserts Annotation username into AnnotationUserDetail table if not exists.

    :param username: Username of Annotation user
    :return: id of annotation user newly inserted or already present in table
    """
    cursor = conn.cursor()

    query = sqlconfig['get_annotation_user_id']
    values = (username,)
    cursor.execute(query, values)
    data = cursor.fetchone()
    if data:
        user_id = data[0]
    else:
        query = sqlconfig['insert_annotation_user_detail']
        cursor.execute(query, values)
        conn.commit()
        user_id = cursor.fetchone()[0]

    return user_id


async def insert_document_task_map(conn, document_id, task_id):
    """
    The method inserts document id and its associated task id in DocumentTaskMap table.

    :param document_id: id of document
    :param task_id: id of task
    """
    cursor = conn.cursor()
    query = sqlconfig['insert_document_task_map']
    values = (document_id, task_id)
    cursor.execute(query, values)
    conn.commit()


async def insert_task_status(conn, task_id, status_id):
    """
    The method inserts task id and its associated status id in TaskStatus table.

    :param task_id: id of task
    :param status_id: id of status
    """
    cursor = conn.cursor()
    query = sqlconfig['insert_task_status']
    values = (task_id, status_id)
    cursor.execute(query, values)
    conn.commit()


async def insert_status(conn, status_details):
    """
    The method inserts status of task into StatusMaster table if not exists.

    :param status_details: Status details of task
    :return: id of status newly inserted or already present in table
    """
    cursor = conn.cursor()
    status = status_details["status"]
    created_date = status_details["created_date"]
    updated_date = status_details["updated_date"]

    query = sqlconfig['get_status_id']
    values = (status,)
    cursor.execute(query, values)
    data = cursor.fetchone()
    if data:
        status_id = data[0]
    else:
        values = (status, created_date, updated_date)
        query = sqlconfig['insert_status']
        cursor.execute(query, values)
        conn.commit()
        status_id = cursor.fetchone()[0]

    return status_id


async def insert_annotation_type(conn, annotation_type):
    """
    The method inserts type of annotation into AnnotationTypeMaster table if not exists.

    :param annotation_type: Type of annotation
    :return: id of annotation type newly inserted or already present in table
    """
    cursor = conn.cursor()

    query = sqlconfig['get_annotation_type_id']
    values = (annotation_type,)
    cursor.execute(query, values)
    data = cursor.fetchone()
    if data:
        annotation_type_id = data[0]
    else:
        query = sqlconfig['insert_annotation_type']
        cursor.execute(query, values)
        conn.commit()
        annotation_type_id = cursor.fetchone()[0]

    return annotation_type_id


async def insert_label(conn, label):
    """
    The method inserts annotation label into LabelMaster table if not exists.

    :param label: Annotation label
    :return: id of label newly inserted or already present in table
    """
    cursor = conn.cursor()

    query = sqlconfig['get_label_id']
    values = (label,)
    cursor.execute(query, values)
    data = cursor.fetchone()
    if data:
        label_id = data[0]
    else:
        query = sqlconfig['insert_label']
        cursor.execute(query, values)
        conn.commit()
        label_id = cursor.fetchone()[0]

    return label_id


async def insert_label_details(conn, label_details):
    """
    The method inserts annotation label details into LabelDetail table.

    :param label_details: details to be inserted into LabelDetail Table
    :return: id of label details inserted
    """
    annotation_type_id = label_details["annotation_type_id"]
    page_no = label_details["page_number"]
    label_id = label_details["label_id"]
    created_date = label_details["created_date"]
    updated_date = label_details["updated_date"]

    cursor = conn.cursor()
    query = sqlconfig['insert_label_detail']
    values = (annotation_type_id, page_no, label_id, created_date, updated_date)
    cursor.execute(query, values)
    label_detail_id = cursor.fetchone()[0]
    conn.commit()
    return label_detail_id


async def insert_task_label_map(conn, task_detail_id, label_detail_id):
    """
    The method inserts task id and its associated label detail id in TaskLabelMap table.

    :param label_detail_id: primary key id of LabelDetail table
    :param task_detail_id: primary key id of TaskDetail table
    """
    cursor = conn.cursor()

    task_label_map_query = sqlconfig['insert_task_label_map']
    task_label_map_values = (task_detail_id, label_detail_id)
    cursor.execute(task_label_map_query, task_label_map_values)
    conn.commit()


async def insert_sublabel_detail(conn, label_detail_id, sublabels):

    """
    The method inserts sublabel details into SublabelDetail table.

    :param label_detail_id: id of label details reference from LabelDetail table
    :param sublabels: list of sublabels for a given annotation label
    :return: id of sublabel details inserted
    """
    cursor = conn.cursor()
    query = sqlconfig['insert_sublabel_detail']

    async def insert_op(sublabel):
        values = (sublabel['Name'], sublabel['Value'], sublabel['Type'], sublabel["created_date"], sublabel["updated_date"])
        cursor.execute(query, values)
        sublabel_detail_id = cursor.fetchone()[0]

        label_sublabel_map_query = sqlconfig['insert_label_sublabel_map']
        label_sublabel_map_values = (label_detail_id, sublabel_detail_id)
        cursor.execute(label_sublabel_map_query, label_sublabel_map_values)

    coros = []
    for sublabel in sublabels:
        coros.append(insert_op(sublabel))

    await asyncio.gather(*coros)
    conn.commit()


async def insert_annotation_detail(conn, label_detail_id, annotations, created_date):
    """
    The method inserts annotation details into AnnotationDetail table.

    :param label_detail_id: id of label details reference from LabelDetail table
    :param annotations: dict of key-value pair for each annotation co-ordinate point
    :return: ids of annotation details inserted
    """
    cursor = conn.cursor()
    query = sqlconfig['insert_annotation_detail']

    async def insert_op(key, val):
        values = (key, val, created_date, created_date)
        cursor.execute(query, values)
        annotation_detail_id = cursor.fetchone()[0]

        label_annotation_map_query = sqlconfig['insert_label_annotation_map']
        label_annotation_map_values = (label_detail_id, annotation_detail_id)
        cursor.execute(label_annotation_map_query, label_annotation_map_values)

    coros = []
    for key, val in annotations.items():
        coros.append(insert_op(key, val))

    await asyncio.gather(*coros)
    conn.commit()
