import os
from .conn_mgr import get_db_connection, close_conn
from AnnotationMigration.helper import read_properties_file

parent_dir = os.path.dirname(os.path.abspath(__file__))
sqlconfig = read_properties_file(os.path.join(parent_dir, "sql.properties"))
