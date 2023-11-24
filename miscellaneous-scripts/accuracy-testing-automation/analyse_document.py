import requests
import json
import uuid
import glob
import os
import csv
from base64 import b64encode
from database.conn_mgr import get_db_connection, close_conn
import concurrent.futures
from tqdm import tqdm

PDF_FOLDER_PATH = os.getenv('PDF_FOLDER_PATH')
USERNAME = os.getenv('USER_NAME')
PASSWORD = os.getenv('PASS_WORD')


class PareitAPI:
    def __init__(self):
        self.base_url = "https://api.beta.sandbox.pareit.com/v1"
        self.state_token = None
        self.access_token = None

    def login(self):
        url = f"{self.base_url}/auth/login"
        payload = {}

        headers = {
            'dapr-app-id': 'pareit-auth-service',
            'Authorization': "Basic {}".format(b64encode(bytes(f"{USERNAME}:{PASSWORD}", "utf-8")).decode("ascii")),
            'Cookie': 'X-CSRF-TOKEN=CfDJ8N41YuMmNFdEpU0nmJ3h11mcclJYS3mVjzFYYUOsewFOv-4aZKZa1gztgY0KlZLYPlLENKvUHjQzQMHN6NkDK3BXxNIAWUJlUf9XmOorEcRaV7lVCfwDrHpkJJCStv7YdJgnT76Wb9Vebeasgzez8nc; .AspNetCore.Antiforgery.uEpP0wzm0B4=CfDJ8N41YuMmNFdEpU0nmJ3h11lBmEac0llo_bM9DPJuQnEwp9Xzeqx61XjspHfqgqfXjfz7YDE5McJkYwocd44HqSnDu24hbqVgoGqooN2MRM0MVnShaf_Ec26i_Q9_zTNeWhi1KoKITuf4rDoAixyR8OQ'
        }
        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            if response.status_code in (requests.codes.ok, requests.codes.created, requests.codes.no_content):
                response_data = response.json()
                self.state_token = response_data.get('state_token')
            else:
                print(f"Unexpected status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred:{e}")

    def otp_verification(self, verification_code):
        url = f"{self.base_url}/auth/verify-otp"
        payload = json.dumps({
            "state_token": self.state_token,
            "communication_channel": [
                "sms"
            ],
            "sms_verification_code": verification_code
        })
        headers = {
            'dapr-app-id': 'pareit-auth-service',
            'Content-Type': 'application/json',
            'Cookie': 'X-CSRF-TOKEN=CfDJ8N41YuMmNFdEpU0nmJ3h11m7xtNvmHy0oRgRrPCTS9yJLqSBRB27nWFZsi4rXQueqKCIWAwG_8kKHqjTWvA40W2D9vYcXQ-EwKIg2oD2NzzLWPW-dPs9sThS1YeYZ0fqbCi0yhwamZrrECug3zsZcA4'
        }
        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            if response.status_code in (requests.codes.ok, requests.codes.created, requests.codes.no_content):
                self.access_token = response.json()['token_info']['access_token']
            else:
                print(f"Unexpected status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred:{e}")

    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        else:
            return json.JSONEncoder().default(obj)

    def main(self, document_files):
        conn = get_db_connection()

        def process_document(document_files):
            for document_file in tqdm(document_files):
                document_name = os.path.basename(document_file)
                doc = document_name.replace('.pdf', '')
                case_id = self.create_case()
                user_package_id = self.create_user_package(case_id, package_id, additional_pages)
                self.purchase_case_payment(user_package_id, sandbox_payment_method_id)
                doc_id = self.upload_document(case_id, document_file)
                req_id = self.get_request_id(conn, case_id)
                self.write_to_csv(case_id, doc_id, document_name, file_name, req_id)

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            executor.map(process_document, document_files)
        close_conn(conn)

    def create_case(self):
        url = f"{self.base_url}/cases"
        payload = json.dumps({
            "name": f'{str(uuid.uuid1())} 27documents',
        }, default=self.default)
        headers = {
            'dapr-app-id': 'pareit-case-service',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}',
            'Cookie': 'X-CSRF-TOKEN=CfDJ8N41YuMmNFdEpU0nmJ3h11kH1WOpNWU1pLad0Sa37dbMkiaeDrAk3OGuM-Mj9bBrA4u-Y1mRy-a7YYhMeWqxlUBOwooiP-vDx7xg5unu4E62kaIiBysfqOnHUQCpgvddgSs8hBq8-rdEbal_YBDdhTqaUxsxSE-0Gcc_FW3C9idwBuDM2Zci_VizNcpEVmnOQw; .AspNetCore.Antiforgery.uEpP0wzm0B4=CfDJ8N41YuMmNFdEpU0nmJ3h11leBYKpUuaSnTq6K3uJt3M9rigq0v9H0dnsKPh30wz6YCWwS4NzjxcjnMvrGAmPBJvjcuedm6Y_oa2rx2za1ABZl9vpUNe7f0KxEkqhsCRo31eKOwnNl_-SjZujmM06J9g'
        }
        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            if response.status_code in (requests.codes.ok, requests.codes.created, requests.codes.no_content):
                case_id = response.json()['id']
                return case_id

        except requests.exceptions.RequestException as e:
            print(f"An error occurred:{e}")

    def get_request_id(self, conn, case_id):
        cursor = conn.cursor()
        query = f'SELECT "RequestId" FROM public."Document" where "CaseId"=%s;'
        values = (case_id,)
        cursor.execute(query, values)
        request_id = cursor.fetchone()[0]
        return request_id

    def create_user_package(self, case_id, package_id, additional_pages):
        url = f"{self.base_url}/user-packages"
        payload = json.dumps({
            "case_id": case_id,
            "package_id": package_id,
            "additional_pages": additional_pages
        })
        headers = {
            'dapr-app-id': 'pareit-payment-service',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}',
            'Cookie': 'X-CSRF-TOKEN=CfDJ8N41YuMmNFdEpU0nmJ3h11mpLy5wnOE8J3ChOibgecQmL_ZeWCHXWFy9moyGIusiuKvQLE7C6BJbiL2HWz8_GtPIj06cP7Cmg211uzQ8XW1eDCCKX8bpyPzlltf0CJ3PXlJI-r4w32ixG5NAIV0g0q8; .AspNetCore.Antiforgery.uEpP0wzm0B4=CfDJ8N41YuMmNFdEpU0nmJ3h11leBYKpUuaSnTq6K3uJt3M9rigq0v9H0dnsKPh30wz6YCWwS4NzjxcjnMvrGAmPBJvjcuedm6Y_oa2rx2za1ABZl9vpUNe7f0KxEkqhsCRo31eKOwnNl_-SjZujmM06J9g'
        }
        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            if response.status_code in (requests.codes.ok, requests.codes.created, requests.codes.no_content):
                user_package_id = response.json()['id']
                return user_package_id
            else:
                print(f"Unexpected status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred:{e}")

    def purchase_case_payment(self, user_package_id, payment_method_id):
        url = f"{self.base_url}/user-packages/{user_package_id}/purchase"

        payload = json.dumps({
            "payment_method_id": payment_method_id
        })

        headers = {
            'dapr-app-id': 'pareit-payment-service',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}',
            'Cookie': 'X-CSRF-TOKEN=CfDJ8N41YuMmNFdEpU0nmJ3h11nf4XAgZvS7trdJV6ZmAI3Gf6JMl0RNcdxMePm7N9-6P3cdgtLAlrnjePnUwKBEaPQG6Ls1Hcc6BBaL1LhSW66vIEA93fMGsB7r0nPwizY-4ypOSFaFeH6y6MJZR3HJUFs; .AspNetCore.Antiforgery.uEpP0wzm0B4=CfDJ8N41YuMmNFdEpU0nmJ3h11leBYKpUuaSnTq6K3uJt3M9rigq0v9H0dnsKPh30wz6YCWwS4NzjxcjnMvrGAmPBJvjcuedm6Y_oa2rx2za1ABZl9vpUNe7f0KxEkqhsCRo31eKOwnNl_-SjZujmM06J9g'
        }
        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            if response.status_code in (requests.codes.ok, requests.codes.created, requests.codes.no_content):
                print("Purchase case created!!")
            else:
                print(f"Unexpected status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred:{e}")

    def upload_document(self, case_id, document_files):
        url = f"{self.base_url}/cases/{case_id}/documents"
        payload = {}

        file_name = os.path.basename(document_files)
        file_path = os.path.join(os.path.dirname(document_files), file_name)
        file_info = [('document', (file_name, open(file_path, 'rb'), 'application/pdf'))]
        headers = {
            'dapr-app-id': 'pareit-case-service',
            'Authorization': f'Bearer {self.access_token}',
            'Cookie': '.AspNetCore.Antiforgery.uEpP0wzm0B4=CfDJ8N41YuMmNFdEpU0nmJ3h11lVxF1U86Ahpcvz2dSxi_B9r6uEcTIThl4gqxfONf2XmEiuZBioCEvzfoAj7ZX99awqZtjrpkAj8-lu9T7DfO4A7dGRQvL2roEP1DNLpo2O7ZbQQdo5eWEPV97JwGFfWjM'
        }
        try:
            response = requests.post(url, headers=headers, data=payload, files=file_info)
            response.raise_for_status()
            if response.status_code in (requests.codes.ok, requests.codes.created, requests.codes.no_content):
                doc_id = response.json().get('id')
                return doc_id
            else:
                print(f"Unexpected status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred:{e}")

    def write_to_csv(self, case_id, doc_id, doc_name, file_name, req_id):
        with open(file_name, 'a', newline='') as csvfile:
            file_empty = csvfile.tell() == 0
            writer = csv.writer(csvfile, delimiter=',')
            if file_empty:
                writer.writerow(['case_id', 'doc_id', 'doc_name', 'request_ids'])
            row = (case_id, doc_id, doc_name, req_id)
            writer.writerow(row)


pareit_api = PareitAPI()
verification_code = "110671"
document_files = glob.glob(PDF_FOLDER_PATH)
package_id = "95e60d34-74bc-451c-aa7f-6a663081a765"
additional_pages = 20
payment_method_id = "4e87821c-6d22-4148-97da-3164347ef01a"
sandbox_payment_method_id = "d6b9c6e4-764e-4151-b83a-a544bac82ef5"
file_name = "27_document_accuracy_testing_07-08-2023-sandbox.csv"
pareit_api.login()
print("Login completed!!")
pareit_api.otp_verification(verification_code)
print("OTP Varified!!")
pareit_api.main(document_files)
