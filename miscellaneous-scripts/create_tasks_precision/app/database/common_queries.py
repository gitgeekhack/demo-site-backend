import socket
from app.database.conn_mgr import get_db_connection, close_conn
from app.database.read_sql_properties import sqlconfig


CVAT_PORT = 8100
CVAT_TASK_URL_FORMAT = 'http://{}:{}/tasks/{}'


def insert_task_status(conn, task_id, status_id):
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



def insert_status(conn, status):
    """
    The method inserts status of task into StatusMaster table if not exists.

    :param status: Status of task
    :return: id of status newly inserted or already present in table
    """

    cursor = conn.cursor()

    query = sqlconfig['get_status_id']
    values = (status,)
    cursor.execute(query, values)
    data = cursor.fetchone()
    if data:
        status_id = data[0]
    else:
        query = sqlconfig['insert_status']
        cursor.execute(query, values)
        conn.commit()
        status_id = cursor.fetchone()[0]


    return status_id


def insert_annotation_user(conn, username):
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


def get_document_name(conn, doc_name):
    """
    The method returns primary key id for given document name from DocumentDetail table.

    :param doc_name: Document name
    :return: id of matched record in DocumentDetail table
    """

    cursor = conn.cursor()
    query = sqlconfig['get_document_name']
    values = (doc_name,doc_name)
    cursor.execute(query, values)
    data = cursor.fetchone()

    if data:
        return data[0]


def get_document_id(conn, doc_name):
    """
    The method returns primary key id for given document name from DocumentDetail table.

    :param doc_name: Document name
    :return: id of matched record in DocumentDetail table
    """
    cursor = conn.cursor()
    query = sqlconfig['get_document_id']
    values = (doc_name,)
    cursor.execute(query, values)
    data = cursor.fetchone()
    if data:
        return data[0]


def insert_label(label):
    """
    The method inserts annotation label into LabelMaster table if not exists.

    :param label: Annotation label
    :return: id of label newly inserted or already present in table
    """
    conn = get_db_connection()
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

    close_conn(conn)
    return label_id


def insert_annotation_type(annotation_type):
    """
    The method inserts type of annotation into AnnotationTypeMaster table if not exists.

    :param annotation_type: Type of annotation
    :return: id of annotation type newly inserted or already present in table
    """
    conn = get_db_connection()
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

    close_conn(conn)
    return annotation_type_id


def insert_label_details(annotation_type_id, page_no, label_id):
    """
    The method inserts annotation label details into LabelDetail table.

    :param annotation_type_id: id of annotation type reference from AnnotationTypeMaster table
    :param page_no: page number on which annotation is present
    :param label_id: id of label reference from LabelMaster table
    :return: id of label details inserted
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = sqlconfig['insert_label_detail']
    values = (annotation_type_id, page_no, label_id)
    cursor.execute(query, values)
    label_detail_id = cursor.fetchone()[0]
    conn.commit()
    close_conn(conn)
    return label_detail_id


def insert_sublabel_detail(label_detail_id, sublabels):
    """
    The method inserts sublabel details into SublabelDetail table.

    :param label_detail_id: id of label details reference from LabelDetail table
    :param sublabels: list of sublabels for a given annotation label
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = sqlconfig['insert_sublabel_detail']
    for sublabel in sublabels:
        values = (sublabel['Name'], sublabel['Value'], sublabel['Type'])
        cursor.execute(query, values)
        sublabel_detail_id = cursor.fetchone()[0]

        label_sublabel_map_query = sqlconfig['insert_label_sublabel_map']
        label_sublabel_map_values = (label_detail_id, sublabel_detail_id)
        cursor.execute(label_sublabel_map_query, label_sublabel_map_values)

    conn.commit()
    close_conn(conn)


def insert_annotation_detail(label_detail_id, annotations):
    """
    The method inserts annotation details into AnnotationDetail table.

    :param label_detail_id: id of label details reference from LabelDetail table
    :param annotations: dict of key-value pair for each annotation co-ordinate point
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = sqlconfig['insert_annotation_detail']
    for key, val in annotations.items():
        values = (key, val)
        cursor.execute(query, values)
        annotation_detail_id = cursor.fetchone()[0]

        label_annotation_map_query = sqlconfig['insert_label_annotation_map']
        label_annotation_map_values = (label_detail_id, annotation_detail_id)
        cursor.execute(label_annotation_map_query, label_annotation_map_values)

    conn.commit()
    close_conn(conn)


def insert_task_label_map(label_detail_id, task_name):
    """
    The method inserts task id and its associated label detail id in TaskLabelMap table.

    :param label_detail_id: primary key id of LabelDetailID table
    :param task_name: name of the CVAT task
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = sqlconfig['get_task_id']
    values = (task_name,)
    cursor.execute(query, values)
    task_detail_id = cursor.fetchone()[0]

    task_label_map_query = sqlconfig['insert_task_label_map']
    task_label_map_values = (task_detail_id, label_detail_id)
    cursor.execute(task_label_map_query, task_label_map_values)
    conn.commit()
    close_conn(conn)


def get_hash_from_docname(doc_name):
    """
    The method gives hash of given document from database.

    :param doc_name: name of the document
    :return: hash for corresponding document
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = sqlconfig['get_hash_from_docname']
    values = (doc_name,)
    cursor.execute(query, values)
    data = cursor.fetchone()
    close_conn(conn)
    if data:
        return data[0]


def insert_annotations(task_details, doc_info):
    """
    The method inserts annotations of completed task in database.

    :param task_details: details of a CVAT task
    :param doc_info: details of a document
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = sqlconfig['get_task_id']
    values = (task_details['TaskName'],)
    cursor.execute(query, values)
    data = cursor.fetchone()
    close_conn(conn)

    if not data:
        # if Task not present in database then insert
        if doc_info['start'] and doc_info['end']:
            parent_doc_name = f'{str(doc_info["start"])}-{str(doc_info["end"])}.{doc_info["orig_name"]}'
        else:
            parent_doc_name = doc_info["orig_name"]
        doc_hash = get_hash_from_docname(parent_doc_name)
        task_details['Status'] = 'annotation'
        insert_task_details(task_details, doc_hash)
        task_details['Status'] = 'completed'

    if task_details['Labels']:
        for label in task_details['Labels']:
            label_id = insert_label(label['LabelName'])
            annotation_type_id = insert_annotation_type(label['AnnotationType'])
            label_detail_id = insert_label_details(annotation_type_id, label['PageNo'], label_id)
            if label['SubLabels']:
                insert_sublabel_detail(label_detail_id, label['SubLabels'])
            insert_annotation_detail(label_detail_id, label['Annotations'])
            insert_task_label_map(label_detail_id, task_details['TaskName'])


def add_annotation_file_s3_url(url, task_id):
    """
    The method adds S3 url of annotation zip file in TaskDetail table.

    :param url: S3 url of annotation zip file
    :param task_id: id of a cvat task
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = sqlconfig['update_annotation_file_url']
    values = (url, task_id)
    cursor.execute(query, values)
    conn.commit()
    close_conn(conn)


def update_task_details(task_details, url):
    """
    The method updates details of a completed CVAT task in various database tables.

    :param task_details: details of a CVAT task
    :param url: S3 url of annotation zip file
    :return: boolean is task details updated or not
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = sqlconfig['get_task_id']
    values = (task_details['TaskName'],)
    cursor.execute(query, values)
    data = cursor.fetchone()
    if data:
        task_id = data[0]

        if task_details['Assignee']:
            assignee_id = insert_annotation_user(task_details['Assignee'])
            query = sqlconfig['update_assignee_id']
            values = (assignee_id, task_id)
            cursor.execute(query, values)

        if task_details['Reviewer']:
            reviewer_id = insert_annotation_user(task_details['Reviewer'])
            query = sqlconfig['update_reviewer_id']
            values = (reviewer_id, task_id)
            cursor.execute(query, values)

        if url:
            add_annotation_file_s3_url(url, task_id)

        status_id = insert_status(task_details['Status'])
        insert_task_status(task_id, status_id)

        conn.commit()
        close_conn(conn)
        return True

    close_conn(conn)
    return False


def get_document_name_from_hash(doc_hash):
    """
    The method returns original name of document from DocumentDetail table using document hash.

    :param doc_hash: hash of the document name
    :return: original name of the document corresponding to given document hash if present else None
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = sqlconfig['get_document_name_from_hash']
    values = (doc_hash,)
    cursor.execute(query, values)
    data = cursor.fetchone()
    close_conn(conn)
    if data:
        return data[0]


def insert_project(conn, project_name):
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


def insert_task(conn, task_name, project_id, assignee_id, reviewer_id, task_url, cvat_task_id, cvat_host_ip):
    """
    The method inserts Task details into TaskDetail table.

    :param task_name: CVAT task name
    :param project_id: Project id of task
    :param assignee_id: assignee id of task
    :param reviewer_id: reviewer id of task
    :param task_url: CVAT url of task
    :param cvat_task_id: CVAT task id of task
    :param cvat_host_ip: ip address of current CVAT host machine
    :return: id of last inserted task record in TaskDetail table
    """

    cursor = conn.cursor()
    query = sqlconfig['insert_task_detail']
    values = (task_name, project_id, assignee_id, reviewer_id, task_url, cvat_task_id, cvat_host_ip)
    cursor.execute(query, values)
    task_id = cursor.fetchone()[0]
    conn.commit()

    return task_id


def insert_document_task_map(conn, document_id, task_id):
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



def insert_task_details(conn, task_details, doc_name, page_start, page_end):
    """
    The method inserts task details in the Database tables.

    :param task_details: Details of a task
    :param doc_name: Document name
    :return: boolean is task data inserted in database or not
    """
    document_name = get_document_name(conn, doc_name)
    document_id = None
    if document_name:
        split_doc_name = f'{page_start}-{page_end}.{document_name}'
        document_id = get_document_id(conn, split_doc_name)
    if document_id:
        # Updating master tables
        project_id = insert_project(conn, task_details['Project'])
        status_id = insert_status(conn, task_details['Status'])

        assignee_id, reviewer_id = -1, -1
        if task_details['Assignee']:
            assignee_id = insert_annotation_user(conn, task_details['Assignee'])
        if task_details['Reviewer']:
            reviewer_id = insert_annotation_user(conn, task_details['Reviewer'])

        cvat_host_ip = socket.gethostbyname(socket.gethostname())  # finding current machine's IP address
        cvat_task_url = CVAT_TASK_URL_FORMAT.format(cvat_host_ip, CVAT_PORT, task_details["TaskID"])
        # Inserting Task details
        task_id = insert_task(conn, task_details['TaskName'], project_id, assignee_id,
                              reviewer_id, cvat_task_url, task_details['TaskID'], cvat_host_ip)

        # Inserting Task status
        insert_task_status(conn, task_id, status_id)

        # Inserting Document-Task mapping
        insert_document_task_map(conn, document_id, task_id)

        return True

    return False

def get_parent_doc_id(doc_hash):
    """
    The method returns parent document id of document from DocumentDetail table using document hash.

    :param doc_hash: hash of the document name
    :return: id of parent document of given document
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = sqlconfig['get_parent_doc_id']
    values = (doc_hash,)
    cursor.execute(query, values)
    parent_doc_id = cursor.fetchone()[0]
    close_conn(conn)
    return parent_doc_id


def get_document_name_from_id(doc_id):
    """
    The method returns document hash name from DocumentDetail table using its primary key DocumentDetailID.

    :param doc_id: primary key id of DocumentDetail table
    :return: DocumentMaskedName(document hash name) corresponding to doc_id
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = sqlconfig['get_document_hash_name_from_id']
    values = (doc_id,)
    cursor.execute(query, values)
    document_name = cursor.fetchone()[0]
    close_conn(conn)
    return document_name


def get_parent_doc(doc_name):
    """
    The method returns parent document name if available in database.

    :param doc_name: split document name
    :return: parent document name or None
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = sqlconfig['get_parent_doc']
    values = (doc_name,)
    cursor.execute(query, values)
    data = cursor.fetchone()
    close_conn(conn)
    if data:
        return data[0]


def get_page_range(doc_hash):
    """
    The method return start and end page of parent document for given split document.

    :param doc_hash: Split document hash name
    :return: start page of split in parent doc, end page of split in parent doc
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = sqlconfig['get_parent_doc_pages']
    values = (doc_hash,)
    cursor.execute(query, values)
    start_page, total_pages = cursor.fetchone()
    end_page = start_page + total_pages - 1
    close_conn(conn)
    return start_page, end_page
