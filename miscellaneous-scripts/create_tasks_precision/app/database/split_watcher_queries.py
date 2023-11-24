import os
from app.database.conn_mgr import get_db_connection, close_conn
from app.database.read_sql_properties import sqlconfig
from app.database.common_queries import get_document_id
import psycopg2
import uuid


def insert_document_details(doc_details):
    """
    The method inserts details of document into DocumentDetail table.

    :param doc_details: dict containing various information related to document
    :return: boolean is document inserted or not
    """
    parent_doc_id = get_document_id(doc_details['document'])
    if parent_doc_id:
        total_pages = doc_details['end'] - doc_details['start'] + 1
        doc_name = doc_details['formatted_doc_name']
        doc_hash = os.path.basename(doc_details['file'])
        s3_url = None
        parent_page_start = doc_details['start']

        conn = get_db_connection()
        cursor = conn.cursor()
        query = sqlconfig['insert_document_detail']
        values = (total_pages, doc_name, doc_hash, parent_doc_id, s3_url, parent_page_start)
        try:
            cursor.execute(query, values)
        except psycopg2.errors.UniqueViolation as e:
            print("Duplicate document found in database, generating new hash...")
            conn.rollback()
            new_doc_hash = f'Duplicate_{doc_hash.replace(".pdf", "")}_{str(uuid.uuid4())[:8]}.pdf'
            values = (total_pages, doc_name, new_doc_hash, parent_doc_id, s3_url, parent_page_start)
            cursor.execute(query, values)
            print(f"New hash generated for Document: {doc_name}, Generated hash: {new_doc_hash}")

        conn.commit()
        close_conn(conn)
        return True
    return False