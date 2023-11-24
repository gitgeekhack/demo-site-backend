import psycopg2

DB_HOST="localhost"
DB_PORT="5432"
DB_USER="postgres"
DB_PASS="Mtech123#"
DB_NAME="random"


def get_db_connection():
    """get connection of annotation tracking database"""

    conn = psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASS,
                            host=DB_HOST, port=DB_PORT)
    return conn


conn = get_db_connection()


def get_main_doc_ids(doc_names):
    query = 'Select "DocumentDetailID" from public."DocumentDetail" where "DocumentName" in %s'
    cursor = conn.cursor()
    cursor.execute(query, [tuple(doc_names)])
    main_doc_id_list = [main_doc_id[0] for main_doc_id in cursor.fetchall()]
    print("No. of Parent Documents to be deleted: ", len(main_doc_id_list))
    return main_doc_id_list

def get_split_doc_ids(parent_doc_ids):
    query = 'Select "DocumentDetailID" from public."DocumentDetail" where "ParentDocumentID" in %s'
    cursor = conn.cursor()
    cursor.execute(query, [tuple(parent_doc_ids)])
    child_doc_ids = [split_doc_id[0] for split_doc_id in cursor.fetchall()]
    print("No. of split Documents to be deleted: ", len(child_doc_ids))
    return child_doc_ids

def get_task_detail_ids(parent_doc_ids, child_doc_ids):
    all_doc_ids = parent_doc_ids + child_doc_ids
    query = 'Select "TaskDetailID" from public."DocumentTaskMap" where "DocumentDetailID" in %s'
    cursor = conn.cursor()
    cursor.execute(query,[tuple(all_doc_ids)])
    task_detail_id_list = [task_detail_id[0] for task_detail_id in cursor.fetchall()]
    print("No. of tasks to be deleted: ",len(task_detail_id_list))
    return task_detail_id_list

def get_label_detail_ids(task_details_id):
    query = 'Select "LabelDetailID" from public."TaskLabelMap" where "TaskDetailID" in %s'
    cursor = conn.cursor()
    cursor.execute(query,[tuple(task_details_id)])
    label_details_id = [label_detail_id[0] for label_detail_id in cursor.fetchall()]
    print("No. of Label details to be deleted: ", len(label_details_id))
    return label_details_id

def get_sublabel_ids(label_details_id):
    query = 'Select "SublabelDetailID" from "LabelSublabelMap" where "LabelDetailID" in %s'
    cursor = conn.cursor()
    cursor.execute(query, [tuple(label_details_id)])
    sublabel_details_id = [sublabel_detail_id[0] for sublabel_detail_id in cursor.fetchall()]
    print("No. of Sublabel details to be deleted: ", len(sublabel_details_id))
    return sublabel_details_id

def get_annot_ids(label_details_id):
    query = 'Select * from "LabelAnnotationMap" where "LabelDetailID" in %s'
    cursor = conn.cursor()
    cursor.execute(query, [tuple(label_details_id)])
    annot_details_id = [annot_detail_id[0] for annot_detail_id in cursor.fetchall()]
    print("No. of Annotation details to be deleted: ", len(annot_details_id))
    return annot_details_id

def create_del_queries(annot_detail_ids, sublabel_detail_ids, label_detail_ids, task_detail_ids, doc_ids):
    del_annot_details = f'Delete from public."AnnotationDetail" where "AnnotationDetailID" in {tuple(annot_detail_ids)};\n'
    del_sublabel_details = f'Delete from public."SublabelDetail" where "SublabelDetailID" in {tuple(sublabel_detail_ids)};\n'
    del_label_annot_maps = f'Delete from public."LabelAnnotationMap" where "LabelDetailID" in {tuple(label_detail_ids)};\n'
    del_label_sublabel_maps = f'Delete from public."LabelSublabelMap" where "LabelDetailID" in {tuple(label_detail_ids)};\n'
    del_label_ids = f'Delete from public."LabelDetail" where "LabelDetailID" in {tuple(label_detail_ids)};\n'
    del_task_label_maps = f'Delete from public."TaskLabelMap" where "TaskDetailID" in {tuple(task_detail_ids)};\n'
    del_task_details = f'Delete from public."TaskDetail" where "TaskDetailID" in {tuple(task_detail_ids)};\n'
    del_doc_task_maps = f'Delete from public."DocumentTaskMap" where "DocumentDetailID" in {tuple(doc_ids)};\n'
    del_doc_ids = f'Delete from "DocumentDetail" where "DocumentDetailID" in {tuple(doc_ids)};\n'
    del_task_status = f'Delete from public."TaskStatus" where "TaskDetailID" in {tuple(task_detail_ids)};\n'
    del_queries = del_label_annot_maps + del_label_sublabel_maps + del_annot_details + del_sublabel_details \
                  + del_task_label_maps + del_label_ids + del_doc_task_maps + del_task_status + del_task_details +  del_doc_ids
    return del_queries

if __name__ == "__main__":
    with open("files_to_be_deleted.txt", 'r') as f:
        f_lines = f.readlines()
    file_names = [s.replace("\n", "") for s in f_lines]
    main_doc_ids = get_main_doc_ids(file_names)
    split_doc_ids = get_split_doc_ids(main_doc_ids)
    task_ids = get_task_detail_ids(main_doc_ids, split_doc_ids)
    label_ids = get_label_detail_ids(task_ids)
    sublabel_ids = get_sublabel_ids(label_ids)
    annotation_ids = get_annot_ids(label_ids)

    delete_queries = create_del_queries(annotation_ids, sublabel_ids,label_ids, task_ids, split_doc_ids + main_doc_ids)
    with open("delete_queries.sql", "w") as f:
        f.write(delete_queries)