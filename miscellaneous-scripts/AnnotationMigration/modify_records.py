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


def get_doc_details():
    main_masks = []
    dup_ids = []
    main_doc_names = []
    query = 'SELECT "DocumentDetailID", substring("DocumentMaskedName" from 11 for 32)||\'.pdf\' as main_mask, "DocumentName" FROM public."DocumentDetail"  where "DocumentMaskedName" like \'Duplicate%\' AND "ParentDocumentID" IS NULL and "DocumentDetailID" not in (Select "DocumentDetailID" from public."DocumentTaskMap");'
    cursor = conn.cursor()
    cursor.execute(query)
    records = cursor.fetchall()
    for r in records:
        dup_ids.append(r[0])
        main_masks.append(r[1])
        main_doc_names.append(r[2])
    return dup_ids, main_masks, main_doc_names


def get_main_doc_ids(masked_names):
    query = 'SELECT "DocumentDetailID" from public."DocumentDetail" WHERE "DocumentMaskedName" = %s'
    cursor = conn.cursor()
    main_doc_ids = []
    for masked_name in masked_names:
        cursor.execute(query, [masked_name])
        main_doc_id = cursor.fetchone()[0]
        main_doc_ids.append(main_doc_id)
    return main_doc_ids


def get_created_date(masked_names):
    query = 'SELECT "CreatedDatetime" from public."DocumentDetail" where "DocumentMaskedName" = %s'
    cursor = conn.cursor()
    parent_created_dates = []
    for masked_name in masked_names:
        cursor.execute(query, [masked_name])
        main_created_date = cursor.fetchone()[0]
        parent_created_dates.append(main_created_date)
    return parent_created_dates


def update_dup_to_main_queries(real_doc_ids, parent_created_dates, dup_ids):
    sql = '-- Update SQL statements\n'
    for i in range(len(dup_ids)):
        query = f'UPDATE public."DocumentDetail" SET "ParentDocumentID" = {real_doc_ids[i]}, "CreatedDatetime" = \'{parent_created_dates[i]}\' WHERE "ParentDocumentID" = {dup_ids[i]};\n'
        sql += query
    return sql


def delete_dup_queries(dup_ids, doc_names):
    sql = '-- Delete SQL statements\n'
    cursor = conn.cursor()
    for dup_id in dup_ids:
        get_doc_name = f'Select "DocumentName" from public."DocumentDetail" WHERE  "DocumentDetailID" = {dup_id};\n'
        cursor.execute(get_doc_name, [dup_id])
        doc_name = cursor.fetchone()[0]
        if doc_name in doc_names:
            query = f'DELETE FROM public."DocumentDetail" WHERE "DocumentDetailID" = {dup_id} AND "DocumentName" = \'{doc_name}\';\n'
            sql += query
            doc_names.remove(doc_name)
    return sql


if __name__ == "__main__":
    duplicate_ids, main_doc_masks, main_doc_names = get_doc_details()
    main_doc_ids = get_main_doc_ids(main_doc_masks)
    created_dates = get_created_date(main_doc_masks)
    update_queries = update_dup_to_main_queries(main_doc_ids, created_dates, duplicate_ids)
    delete_queries = delete_dup_queries(duplicate_ids, main_doc_names)
    with open("update_queries.sql", "w") as f:
        data = update_queries + delete_queries
        f.write(data)
