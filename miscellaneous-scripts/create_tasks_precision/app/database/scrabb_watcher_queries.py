from app.database.conn_mgr import get_db_connection, close_conn
from app.database.read_sql_properties import sqlconfig
import psycopg2
import uuid


def insert_document_details(doc_details):
    """
    The methods inserts document details into DocumentDetail table.

    :param doc_details: dict containing information related to document
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = sqlconfig['insert_document_detail']
    values = (doc_details['total_pages'], doc_details['filename'], doc_details['hash'], None, None, None)
    try:
        cursor.execute(query, values)
    except psycopg2.errors.UniqueViolation as e:
        print("Duplicate document found in database, generating new hash...")
        conn.rollback()
        doc_hash = doc_details['hash']
        new_doc_hash = f'Duplicate_{doc_hash.replace(".pdf", "")}_{str(uuid.uuid4())[:8]}.pdf'
        values = (doc_details['total_pages'], doc_details['filename'], new_doc_hash, None, None, None)
        cursor.execute(query, values)
        print(f"New hash generated for Document: {doc_details['filename']}, Generated hash: {new_doc_hash}")


    conn.commit()
    close_conn(conn)
