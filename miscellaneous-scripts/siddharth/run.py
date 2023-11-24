import psycopg2
import pandas as pd
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

# Establish a connection to the PostgreSQL database
# conn = psycopg2.connect(
#     host="pareit-prod-ds-m5-xlarge-rds.c9jmnvdvstnz.us-east-1.rds.amazonaws.com",
#     database="PareITDS",
#     user="root",
#     password="3C7J2Dbper9OaAqC"
# )

types = [
    "Admission_Sheet",
    "Ambulance",
    "Anesthesia",
    "Chiro",
    "Dentistry",
    "Discharge_Summary",
    "DME",
    "Emergency",
    "Gastroenterology",
    "Gynecology",
    "Hosp Records",
    "Hospital Records",
    "Imaging Record",
    "IME",
    "Infectious_Disease",
    "Lab_Form",
    "MD Record",
    "Neuro/Psych Eval",
    "Neurological",
    "Oncology",
    "Operative Report",
    "Ophthalmology",
    "Orthopaedic",
    "Orthropaedic",
    "Pathology_Result",
    "Pediatrics",
    "Pharmacology",
    "Physical Therapy",
    "Psychiatry",
    "Psychological_Eval",
    "Referral/Request",
    "Summary",
    "Supplemental Doc"
]


def get_all_document():
    all_dfs = []
    c = 1
    for t in types:
        print(f"#{c} Listing Documents for: {t}")
        get_documents_by_cat = """
        Select DD."DocumentDetailID", DD."DocumentS3URL", LD."PageNumber" as "ParentStartPage" from public."DocumentDetail" DD
        inner join public."DocumentTaskMap" DTM on DTM."DocumentDetailID" = DD."DocumentDetailID"
        inner join public."TaskDetail" TD on DTM."TaskDetailID" = TD."TaskDetailID"
        inner join public."ProjectDetail" PD on TD."ProjectID" = PD."ProjectID"
        inner join public."TaskLabelMap" TLM on TLM."TaskDetailID" = TD."TaskDetailID"
        inner join public."LabelDetail" LD on LD."LabelDetailID" = TLM."LabelDetailID"
        inner join public."LabelSublabelMap" LSM on LSM."LabelDetailID" = LD."LabelDetailID"
        inner join public."SublabelDetail" SLD on LSM."SublabelDetailID" = SLD."SublabelDetailID"
        where SLD."Value" = '{record_type}'
        AND PD."ProjectID" = 28 limit {no_of_sample};"""
        df = pd.read_sql_query(get_documents_by_cat.format(record_type=t, no_of_sample=15), conn)
        df['Type'] = t
        all_dfs.append(df)
        c += 1
    # Print the DataFrame
    df = pd.concat(all_dfs)
    return df


def get_document_end_page(document_id, parent_start_no):
    # Create a cursor object to execute SQL queries
    print(f'Getting Page End for: {document_id} -> {parent_start_no}')
    get_document_total_pages = """
    Select "TotalPages" from public."DocumentDetail" 
    where "ParentDocumentID" = {document_id} and "ParentPageStartNumber"={parent_start_no}"""

    cursor = conn.cursor()
    cursor.execute(get_document_total_pages.format(document_id=document_id, parent_start_no=parent_start_no))
    rows = cursor.fetchone()
    cursor.close()
    if rows and len(rows) > 0:
        return parent_start_no + rows[0]
    else:
        return -1

#
# df = get_all_document()
# df.to_csv("more_samples_document.csv", index=False)
# df = pd.read_csv("more_samples_document.csv")
# df['ParentEndPage'] = df.apply(lambda x: get_document_end_page(x['DocumentDetailID'], x['ParentStartPage']), axis=1)
# df['FilePath'] = df['DocumentS3URL'].apply(lambda x: x.replace('https://pareit-dev-datalabeling-anno.s3.us-east-2.amazonaws.com/', ''))
# df['FilePath'] = df['FilePath'].apply(lambda x: x.replace('https://pareit-dev-datalabeling-anno-hash.s3.us-east-2.amazonaws.com/', ''))
# df['FilePath'] = df['FilePath'].apply(lambda x: x.replace('https://pareit-dev-datalabeling-anno-hash.s3.us-east-2.amazonaws.com/', ''))
# df['FilePath'] = df['FilePath'].apply(lambda x: x.replace('+', ' '))
# df['FilePath'] = "./more_samlpes/"+ df['FilePath']
# df.to_csv("more_samples.csv", index=False)
df = pd.read_csv("more_samples.csv")

print()


def generate_download_files(items):
    with open('more_samples_all_files.txt', 'w') as f:
        for item in items:
            item = item.replace('https://pareit-dev-datalabeling-anno.s3.us-east-2.amazonaws.com/', '')
            item = item.replace('https://pareit-dev-datalabeling-anno-hash.s3.us-east-2.amazonaws.com/', '')
            f.write(item + "\n")


print("generating download file")
generate_download_files(df["DocumentS3URL"].tolist())
print("download file generated")

# conn.close()
