import pandas
from database.conn_mgr import get_db_connection, close_conn
import requests
import json
import uuid
import glob
import os
import csv
from base64 import b64encode
from database.conn_mgr import get_db_connection, close_conn
from tqdm import tqdm

def get_request_id(self, conn, case_id):
    cursor = conn.cursor()
    query = f'SELECT "RequestId" FROM public."Document" where "CaseId"=%s;'
    values = (case_id,)
    cursor.execute(query, values)
    request_id = cursor.fetchone()[0]
    return request_id
# reading the CSV file
csvFile = pandas.read_csv('/home/heli/Documents/git/accuracy-testing-automation/accuracy_testing_2023_07_18_11_52_37_am.csv')
conn = get_db_connection()
for x in csvFile['case_id']:
    print(x)

close_conn(conn)

# displaying the contents of the CSV file
print(csvFile)