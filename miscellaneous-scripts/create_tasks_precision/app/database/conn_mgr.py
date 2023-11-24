import psycopg2
import os


DB_NAME = os.getenv('DB_NAME', 'AnnotationTracking2')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', 'postgres')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', 5432)


def get_db_connection():
    """get connection of annotation tracking database"""

    conn = psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASS,
                            host=DB_HOST, port=DB_PORT)
    return conn


def close_conn(conn):
    """close connection of database"""
    conn.close()
