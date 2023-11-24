from app.database.conn_mgr import get_db_connection, close_conn
from app.database.read_sql_properties import sqlconfig


def add_doc_s3_url(doc_name, url):
    """
    The method adds S3 url of given document in DocumentDetail table.

    :param doc_name: Document name
    :param url: S3 url of given document
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = sqlconfig['update_document_s3_url']
    values = (url, doc_name)
    cursor.execute(query, values)
    conn.commit()
    close_conn(conn)

