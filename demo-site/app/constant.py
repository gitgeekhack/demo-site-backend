import os
from enum import Enum

USER_DATA_PATH = os.getenv("USER_DATA_PATH")


class BotoClient:
    AWS_DEFAULT_REGION = "us-east-1"
    read_timeout = 3600
    connect_timeout = 3600


class DrivingLicenseParser:
    WORLD_CITIES_LIST = './app/data/world_cities.csv'

    class Regex:
        NAME = r'([A-Z]{3,14}[\s]{0,1}([A-Z]{3,14})[\s]{0,1}([A-Z]{0,14}))(([\s]{0,1}[,]{0,1}[\s]{0,1}([A-Z]{0,4}))|)'
        DATE = r'([0-9]{1,2}[\/-][0-9]{1,2}[\/-][0-9]{2,4})'
        LICENSE_NUMBER = r'([0-9A-Z]{1})[\S]([0-9A-Z\-*]*[0-9A-Z\-*\s]*)'
        ADDRESS = r'([0-9]{1,5}\w+[\s]{0,1})([A-Z\s0-9\-,&#\n]*[0-9]{3})'
        CITY = r'([A-Za-z\s]+=?)'
        ZIPCODE = r'([0-9\-]{5,10})'
        STATE = r'[A-Za-z]{2}'
        STATE_WITH_SPACE = r'\s[A-Za-z]{2}\s'
        GENDER = r'^[MF]{1}'
        HEIGHT = r'''\d{1}'{0,1}-{0,1}\d{1,2}\"{0,1}'''
        WEIGHT = r'(?<=[WGTwgt]){0,3}(\d{2,4})(?<=[lbLB]){0,2}'
        HAIR_COLOR = r'(\w{3,4})'
        EYE_COLOR = r'(\w{3,4})'
        LICENSE_CLASS = r"(\s{1}\w{1,2}$)|((?<=CLASS)\w{1,2}$)|((?<=CLASSIFICATION)\w{1,2}$)"


class Gender(Enum):
    FEMALE = 'Female'
    MALE = 'Male'

    @classmethod
    def items(cls):
        return list(map(lambda c: c.value, cls))


class OCRConfig:
    class DrivingLicense:
        NAME = '-l eng --oem 1 --psm 4 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ ,\n" load_system_dawg=false load_freq_dawg=false'
        LICENSE_NO = '-l eng --oem 1 --psm 7 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789*- " load_system_dawg=false load_freq_dawg=false'
        ADDRESS = '-l eng --oem 1 --psm 4 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789# ,\n-" load_system_dawg=false load_freq_dawg=false'
        DATE = '-l eng --oem 1 --psm 3 -c tessedit_char_whitelist="0123456789/- " load_system_dawg=false load_freq_dawg=false'
        GENDER = '-l eng --oem 1 --psm 7 -c tessedit_char_whitelist="MF" load_system_dawg=false load_freq_dawg=false'
        HEIGHT = '''-l eng --oem 1 --psm 4 -c tessedit_char_whitelist="0123456789H'\\"" load_system_dawg=false load_freq_dawg=false '''
        WEIGHT = '''-l eng --oem 1 --psm 4 -c tessedit_char_whitelist="0123456789WGTLBlbwgt " load_system_dawg=false load_freq_dawg=false'''
        HAIR_COLOR = '-l eng --oem 1 --psm 4 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ " load_system_dawg=false load_freq_dawg=false'
        EYE_COLOR = '-l eng --oem 1 --psm 4 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ " load_system_dawg=false load_freq_dawg=false'
        LICENSE_CLASS = '-l eng --oem 1 --psm 4 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890   " load_system_dawg=false load_freq_dawg=false'

    class CertificateOfTitle:
        TITLE_NO = '-l five --oem 1 --psm 7 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789\n" load_system_dawg=false load_freq_dawg=false'
        VIN_FINE_TUNED = '-l five --oem 1 --psm 3 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" load_system_dawg=false load_freq_dawg=false'
        VIN_PRE_TRAINED = '-l eng --oem 1 --psm 3 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" load_system_dawg=false load_freq_dawg=false'
        YEAR_PSM6 = '-l five --oem 1 --psm 6 -c tessedit_char_whitelist="0123456789 \n" load_system_dawg=false load_freq_dawg=false'
        YEAR_PSM11 = '-l five --oem 1 --psm 11 -c tessedit_char_whitelist="0123456789 \n" load_system_dawg=false load_freq_dawg=false'
        MAKE = '-l five --oem 1 --psm 7 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" load_system_dawg=false load_freq_dawg=false'
        MODEL = '-l five --oem 1 --psm 7 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789/ \n" load_system_dawg=false load_freq_dawg=false'
        DATE_FINE_TUNED = '-l five --oem 1 --psm 6 -c tessedit_char_whitelist="0123456789/- " load_system_dawg=false load_freq_dawg=false'
        DATE_PRE_TRAINED = '-l eng --oem 1 --psm 6 -c tessedit_char_whitelist="0123456789/- " load_system_dawg=false load_freq_dawg=false'
        NAME = '-l eng --oem 1 --psm 4 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ ,\n" load_system_dawg=false load_freq_dawg=false'
        ADDRESS = '-l five --oem 1 --psm 4 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789# ,\n-" load_system_dawg=false load_freq_dawg=false'
        BODY_STYLE = '-l five --oem 1 --psm 11 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789\n " load_system_dawg=false load_freq_dawg=false'
        ODOMETER = '-l five --oem 1 --psm 11 -c tessedit_char_whitelist="EXMPTexmpt0123456789 ,\n" load_system_dawg=false load_freq_dawg=false'
        DOCUMENT_TYPE = '-l five --oem 1 --psm 3 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ\n" load_system_dawg=false load_freq_dawg=false'
        TITLE_TYPE = '-l five --oem 1 --psm 3 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ\n" load_system_dawg=false load_freq_dawg=false'
        REMARK = '-l five --oem 1 --psm 3 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ \n" load_system_dawg=false load_freq_dawg=false'


class DrivingLicense:
    class ObjectDetection:
        DL_OBJECT_DETECTION_MODEL_PATH = './app/model/driving_license/DLObjectDetection.pt'
        YOLOV5 = 'ultralytics/yolov5:v6.0'
        MODEL_CONFIDENCE = 0.49
        OBJECT_LABELS = {0: 'license_number', 1: 'name', 2: 'address', 3: 'date', 4: 'gender', 5: 'height', 6: 'weight',
                         7: 'hair_color', 8: 'eye_color', 9: 'license_class'}

    class ResponseKeys:
        NAME = 'name'
        EYE_COLOR = 'eye_color'
        GENDER = 'gender'
        HEIGHT = 'height'
        ADDRESS = 'address'
        WEIGHT = 'weight'
        LICENSE_NUMBER = 'license_number'
        LICENSE_CLASS = 'license_class'
        HAIR_COLOR = 'hair_color'
        DATE_OF_BIRTH = 'date_of_birth'
        ISSUE_DATE = 'issue_date'
        EXPIRY_DATE = 'expiry_date'
        KEYS = [NAME, EYE_COLOR, GENDER, HAIR_COLOR, HEIGHT, WEIGHT, LICENSE_CLASS, LICENSE_NUMBER, EXPIRY_DATE,
                DATE_OF_BIRTH, ISSUE_DATE]
        DATE_LABELS = [DATE_OF_BIRTH, ISSUE_DATE, EXPIRY_DATE]

    class Section:
        INPUT_PATH = 'driving_license/input_images'


class BarcodeDetection:
    class Section:
        INPUT_PATH = 'barcode_detection/input_images'


class AllowedFileType:
    IMAGE = ['jpg', 'png', 'jpeg']
    PDF = ['pdf']


class ExceptionMessage:
    INVALID_FILE_EXCEPTION_MESSAGE = 'Input file is invalid'
    FAILED_TO_DOWNLOAD_FILE_FROM_URL_EXCEPTION_MESSAGE = 'Unable to download file from url'
    NO_IMAGE_FOUND_EXCEPTION_MESSAGE = "Unable to find image in PDF"
    FILE_LIMIT_EXCEEDED_EXCEPTION_MESSAGE = "File limit exceeded, only upload file upto 25 MB"
    MAX_FILE_SIZE_EXCEEDED_ERROR = "File limit exceeded, only upload file upto 100 MB"
    FILE_PATH_NULL_EXCEPTION_MESSAGE = "File is not uploaded"
    INPUT_QUERY_NULL_EXCEPTION_MESSAGE = "Input query is empty or null"
    MULTIPLE_FILE_UPLOADED_EXCEPTION_MESSAGE = "Multiple files are uploaded, only upload single file"
    MISSING_REQUEST_BODY_EXCEPTION_MESSAGE = "Missing request body in the request"
    INVALID_REQUEST_BODY_EXCEPTION_MESSAGE = "Invalid request body received"
    FILE_UPLOAD_LIMIT_REACHED_EXCEPTION_MESSAGE = "Uploaded more than {x} files"
    TOTAL_PAGE_EXCEEDED_EXCEPTION_MESSAGE = "Combined document pages must not exceed {page_count_threshold}. Please upload fewer pages."
    FOLDER_PATH_NULL_EXCEPTION_MESSAGE = "Project not uploaded"


class APIEndPointURL:
    PDF_EXTRACT_FIRST_IMAGE_ENDPOINT_URL = "/api/v1/internal/pdf-extract-first-image"
    BARCODE_EXTRACT_API_ENDPOINT_URL = "/api/v1/integration/mahindra-logistics/detect-pod"


class APIErrorMessage:
    BAD_REQUEST_PARAMS_MISSING_MESSAGE = "one or more parameter is missing"
    NO_IMAGE_IN_PDF_MESSAGE = "Unable to find image in PDF"
    UNABLE_TO_DOWNLOAD_FILE_MESSAGE = "Unable to get input file"
    INVALID_FILE_MESSAGE = "Invalid input file"


class EyeHairColor:
    color = {'SIL': 'Silver', 'AUB': 'Auburn', 'BAL': 'Bald', 'BGE': 'Beige', 'BLK': 'Black', 'BLD': 'Blonde',
             'BLN': 'Blonde', 'BLU': 'Blue', 'DBL': 'Blue, Dark', 'LBL': 'Blue, Light', 'BRO': 'Brown', 'BRN': 'Brown',
             'MAR': 'Maroon', 'COM': 'Stainless Steel', 'CPR': 'Copper', 'CRM': 'Ivory', 'GLD': 'Gold', 'GRY': 'Gray',
             'GRN': 'Green', 'DGR': 'Green, Dark', 'LGR': 'Green, Light', 'HAZ': 'Hazel', 'LAV': 'Lavender',
             'ONG': 'Orange', 'PNK': 'Pink', 'PLE': 'Purple', 'RED': 'Red', 'TAN': 'Tan', 'TRQ': 'Turquoise',
             'WHI': 'White', 'YEL': 'Yellow'}


class CertificateOfTitle:
    VAL_SCORE = 0.6

    class ObjectDetection:
        COT_OBJECT_DETECTION_MODEL_PATH = './app/model/certificate_of_title/cot-20220427-1426.pt'
        YOLOV5 = 'ultralytics/yolov5:v6.0'
        MODEL_CONFIDENCE = 0.4
        OBJECT_LABELS = {0: 'title_no', 1: 'vin', 2: 'year', 3: 'make', 4: 'model', 5: 'body_style',
                         6: 'odometer_reading', 7: 'issue_date', 8: 'owners', 9: 'owner_address', 10: 'lienholder_name',
                         11: 'lienholder_address', 12: 'lien_date', 13: 'document_type', 14: 'title_type', 15: 'remark'}

    class ResponseKeys:
        TITLE_NO = 'title_no'
        VIN = 'vin'
        YEAR = 'year'
        MAKE = 'make'
        MODEL = 'model'
        BODY_STYLE = 'body_style'
        ODOMETER_READING = 'odometer_reading'
        ISSUE_DATE = 'issue_date'
        OWNER_NAME = 'owners'
        OWNER_ADDRESS = 'owner_address'
        LIENHOLDER_NAME = 'lienholder_name'
        LIENHOLDER_ADDRESS = 'lienholder_address'
        LIEN_DATE = 'lien_date'
        DOCUMENT_TYPE = 'document_type'
        TITLE_TYPE = 'title_type'
        REMARK = 'remark'
        KEYS = [TITLE_NO, VIN, YEAR, MAKE, MODEL, BODY_STYLE, ODOMETER_READING, ISSUE_DATE, OWNER_ADDRESS,
                OWNER_ADDRESS, LIENHOLDER_NAME, LIENHOLDER_ADDRESS, LIEN_DATE, DOCUMENT_TYPE, TITLE_TYPE]

    class Sections:
        TITLE_TYPE = ['SALVAGE', 'CLEAR', 'REBUILT', 'RECONSTRUCTED', 'ASSEMBLED', 'FLOOD DAMAGE', 'SALVAGE-FIRE',
                      'NON-REPAIRABLE', 'JUNK', 'NORMAL', 'STANDARD', 'VEHICLE']
        DOCUMENT_TYPE = ['ORIGINAL', 'DUPLICATE', 'TRANSFER CERTIFIED COPY', 'NEW', 'REPLACEMENT']
        INPUT_PATH = 'certificate_of_title/input_images'
        MULTIPLE_LABELS_OBJECT = ['title_type', 'owner_address', 'document_type']
        MAKE_PICKLE_PATH = './app/data/make.pkl'
        VIN_PICKLE_PATH = './app/data/VehicleWithVIN.pkl'
        BODY_STYLE_PICKLE_PATH = './app/data/body_style.pkl'
        MODEL_PICKLE_PATH = './app/data/model.pkl'

    class Regex:
        YEAR = r'(19[8-9][0-9]|20[0-9]{2})|\b([12][0-9])\b'
        OWNER_NAME = r'([A-Z,]{3,14}\s*[A-Z,]{1,14}\s?[A-Z\s]*)'
        LIEN_NAME = r'([A-Z,]{3,14}\s+[A-Z,]{1,14}\s?[A-Z\s]*)'
        ODOMETER_READING = r'([\d,]{5,})|(EXEMPT)'
        DOCUMENT_TYPE = r'ORIGINAL|DUPLICATE|TRANSFER CERTIFIED COPY|NEW|REPLACEMENT'
        TITLE_TYPE = r'SALVAGE|CLEAR|REBUILT|RECONSTRUCTED|ASSEMBLED|FLOOD DAMAGE|SALVAGE-FIRE|NON-REPAIRABLE|JUNK|NORMAL|STANDARD|VEHICLE'
        REMARKS = r'SALVAGE|CLEAR|REBUILT|RECONSTRUCTED|ASSEMBLED|FLOOD DAMAGE|SALVAGE-FIRE|NON-REPAIRABLE|JUNK|NORMAL|STANDARD|VEHICLE|ORIGINAL|DUPLICATE|TRANSFER CERTIFIED COPY|NEW|REPLACEMENT'


class CarDamageDetection:
    class ColorLabels:
        CAR_DAMAGE = {"headlights": (95, 202, 255), "hood": (159, 247, 17), "front_bumper": (0, 234, 254),
                      "rear_bumper": (99, 247, 220), "front_windshield": (228, 161, 0),
                      "rear_windshield": (60, 128, 240),
                      "flat_tyre": (245, 252, 3), "missing_mirror": (196, 221, 88), "missing_wheel": (158, 210, 250),
                      "taillights": (110, 92, 242), "trunk": (0, 183, 245), "window": (216, 102, 255),
                      "door": (41, 255, 94),
                      "fender": (245, 122, 206), "interior_damage": (133, 37, 247)}

    class Path:
        STATIC_PATH = "app/static/"
        UPLOADED_PATH = "damage_detection/Uploaded/"
        DETECTED_PATH = "damage_detection/Detected/"
        INSTANCE_LOG_FOLDER_PATH = os.path.abspath(os.path.join(__file__, '..', '..', '..', 'logs'))
        YOLOV5 = 'ultralytics/yolov5:v6.0'
        MODEL_PATH = "./app/model/car_damage_detection/DamagePartDetection_04-03-2024.pt"
        FONT_PATH = "./app/static/damage_detection/font_file/arial.ttf"


class MedicalInsights:
    TOTAL_PAGES_THRESHOLD = 1000
    REQUEST_FOLDER_NAME = "request"
    RESPONSE_FOLDER_NAME = "response"

    class Prompts:
        PROMPT_TEMPLATE = """
        Human: Use the following pieces of context to provide a concise answer to the question at the end. If you don't know the answer, don't try to make up an answer.
        <context>
        {context}
        </context>

        Question: {question}

        Assistant:
        """

        PHI_PROMPT = """
        Your role is to extract important dates from a medical document, specifically focusing on the injury dates, admission dates, and discharge dates. This information is vital for medical records management and analysis. Your sole purpose is to provide the output in JSON format, without any additional text output.Don't refine anything, give an original answer.
        Provide the information in JSON format as follows: {"Injury Date": ["dd/mm/yyyy", ...], "Admission Date": ["dd/mm/yyyy", ...], "Discharge Date": ["dd/mm/yyyy", ...]}. Strictly maintain the consistency in this format.
        Note: Don't include visit dates, encounter dates, date of birth, MRI scan dates, X-ray dates, checkup dates, admin date/time, follow-up dates and 'filed at' date. Avoid including times in the output.

        Here is the definition of valid Injury Date, Admission Date and Discharge Date:
        Injury Date: In the medical field context, the injury date refers to the specific date on which a patient sustained an injury or trauma. Accident date of patient is also considered as injury date. It is the date when the event leading to the patient's medical condition or injury occurred.
        Admission Date: The admission date, in the medical field context, refers to the date on which a patient is formally admitted to a healthcare facility, such as a hospital. It marks the beginning of the patient's stay for medical evaluation, treatment, or surgery.
        Discharge Date: The discharge date, in the medical field context, refers to the date when a patient is released or discharged from a healthcare facility after receiving medical care or treatment. It marks the end of the patient's stay in the facility.

        Instructions:
        1. 'Injury Date': Extract the date of the patient's injury from the given medical text. There can be multiple injury dates present in the text. If the injury date is not mentioned in the document, fill the field with "None." Provide the extracted date in JSON format with "injury date" as the key.
        2. 'Admission Date': Extract the date of the patient's admission from the given medical text. There can be multiple admission dates present in the text. Consider the date of the initial examination, initial visit, or the first time the patient was seen in as the admission date. The date with labels such as "Admit date" or "Admission date" should be considered as the admission date. If the admission date is not mentioned in the document, fill the field with "None." Provide the extracted date in JSON format with "admission date" as the key.
        3. 'Discharge Date': Extract the date of the patient's discharge from the given medical text. There can be multiple discharge dates present in the text. Consider the date of the last visit or the last time the patient was seen as the discharge date. The date with labels such as "Discharge date" or "Date of Discharge" should be considered as the discharge date. If the discharge date is not mentioned in the document, fill the field with "None." Provide the extracted date in JSON format with "discharge date" as the key.

        Note: Convert the final output to dd/mm/yyyy format
        """

        DOC_TYPE_PROMPT = """
        You are provided with a text excerpt from a medical report. Your task is to determine the type of document based on its content and context. Utilize the following definitions as guidelines for classification:

        Ambulance: A medical report generated by emergency medical services (EMS) following an ambulance call. It includes patient identification, medical details, clinical observations, incident information, transport details, insurance and billing information, narrative notes, and crew information, serving as a comprehensive account for legal, billing, and medical record purposes.
        Emergency: An Emergency Department Report is a detailed and structured medical document that chronicles the events and clinical management of a patient's acute visit to the emergency department.

        Carefully analyze the medical text excerpt and determine the most appropriate document type based on its characteristics. Don't include your analysis in the response. If the document type matches one of the categories given, strictly respond in the following format:
        {"document_type": "Identified_Document_Type"}.

        If the report is not from any above categories, give the response in following format:
        {"document_type": "Other"}
        """

        MEDICAL_CHRONOLOGY_PROMPT = """
        Above text is obtained from medical records. Based on the information provided, you are tasked with extracting the 'Encounter Date' and corresponding 'Event' along with 'Doctor' from medical records.

        'Encounter Date' : In medical record, it is defined as the specific date when a patient had an interaction with a healthcare provider. This could be a visit to a clinic, a hospital admission, a telemedicine consultation, or any other form of medical service.
        Notes to keep in mind while extracting 'Encounter Date' :
        - Ensure 'Encounter Date' should also include other types of Protected Health Information dates which are listed below :
          1. 'Injury date' : In medical record, it is defined as the specific date when a patient sustained any type of injury.
          2. 'Admission date' : In medical record, it is defined as the specific date when a patient is officially admitted to a healthcare facility, such as a hospital or clinic, for inpatient care.
          3. 'Discharge date' : In medical record, it is defined as the specific date when a patient is discharged or released from a healthcare facility after receiving treatment or completing a course of care.
        - Extract only actual 'Encounter Date' and avoid giving any other types of dates which are listed below :
          1. 'Birth date' : In medical record, it is defined as the specific date when a patient is born. It is typically recorded and used for identification, legal, and administrative purposes. It is also used to calculate a person's age.
          2. 'Received date' : In medical record, it is defined as the specific date when a lab, hospital, or clinic received the test result.
          3. 'Printed date' : In medical record, it is defined as the specific date when the document was created, updated, or reviewed.
          4. 'Resulted date' : In medical record, it is defined as the specific date when the results of certain tests, procedures or treatments are made available or reported.
        - Ensure all the actual 'Encounter Date' are strictly converted to the same format of 'MM/DD/YYYY'.
        - Ensure none of the actual 'Encounter Date' is left behind. Ensure dates from Past Medical History / Past Surgical History are also included.

        'Event' : It is associated with the corresponding 'Encounter Date'. It is described as the summary of all activities that occurred on that particular 'Encounter Date'.
        Notes to keep in mind while extracting 'Event' :
        - Ensure all 'Event' descriptions should include the key points, context, and any relevant supporting details.
        - Also ensure all 'Event' descriptions are more detailed, thorough and comprehensive yet a concise summary in medium-sized paragraph.

        'Doctor' : In medical record, a 'Doctor' is typically defined as the name of a licensed medical professional. A 'Doctor' is responsible for attending, diagnosing, and treating illnesses, injuries, and other health conditions. A 'Doctor' often provides preventive care and health education to patients during the encounter.
        Notes to keep in mind while extracting 'Doctor' :
        - Ensure that the 'Doctor' pertains to the relevant 'Encounter Date' and 'Event'.
        - In case, if 'Doctor' is found then provide the name of 'Doctor' in the json format as below :
          {
            'Doctor' : "Doctor",
            'Role' : "None",
            'Institution' : "None"
          }
        - In case, if 'Doctor' is unknown then follow steps listed as below to find the 'Doctor' :
          Step-1 : Find the 'Institution' or 'Role' relevant to the 'Encounter Date' and 'Event'.
                   'Institution' and 'Role' are defined as below :
                   1. 'Institution' : In medical record, it is defined as the specific workplace of 'Doctor'.
                       If 'Institution' is found then go to Step-2.
                   2. 'Role' : In medical record, it is defined as the specific work role of 'Doctor'.
                       If 'Role' is found then go to Step-2.
          Step-2 : Find the name of 'Doctor' working at or related to that specific found 'Institution' or bearing that specific or similar found 'Role'.
          Step-3 : If the 'Doctor' is still not found then provide the name of 'Doctor' in one of the most suitable format out of four formats described below :
                   1. If 'Role' and 'Institution' are both found then provide the name of 'Doctor' in the json format as below :
                      {
                        'Doctor' : "None",
                        'Role' : "Role",
                        'Institution' : "Institution"
                      }
                   2. If 'Institution' is not found but 'Role' is found then provide the name of 'Doctor' in the json format as below :
                      {
                        'Doctor' : "None",
                        'Role' : "Role",
                        'Institution' : "None"
                      }
                   3. If 'Role' is not found but 'Institution' is found then provide the name of 'Doctor' in the json format as below :
                      {
                        'Doctor' : "None",
                        'Role' : "None",
                        'Institution' : "Institution"
                      }
                   4. If 'Role' and 'Institution' are both not found then find the 'Doctor' who is most relevant to the context of encounter.
                      If 'Doctor' is still not found then provide the name of 'Doctor' in the json format as below :
                      {
                        'Doctor' : "None",
                        'Role' : "None",
                        'Institution' : "None"
                      }
          Step-4 : If the 'Doctor' is found then provide the name of 'Doctor' in the json format as below :
                    {
                      'Doctor' : "Doctor",
                      'Role' : "None",
                      'Institution' : "None"
                    }

        You are required to present this output in a specific format using 'Tuple' and 'List'.
        Strictly adhere to the format explained as below and strictly avoid giving output in any other format.
        'Tuple' : It is used to store multiple items - in this case, the 'Encounter Date', 'Event' and 'Doctor'. It is created using parentheses and should be formatted as ("Encounter Date", "Event", "Doctor").
        'List' : It is used to store multiple items - in this case, the 'Tuple'. It is created using square brackets and should be formatted as [ ("Encounter Date", "Event", "Doctor") ].
        Additionally, arrange all tuples in the list in ascending or chronological order based on the 'Encounter Date'.
        Note: This extraction process is crucial for various aspects of healthcare, including patient care tracking, scheduling follow-up appointments, billing, and medical research. Your attention to detail and accuracy in this task is greatly appreciated.
        """

        PATIENT_INFO_PROMPT = """
        Your task is to identify the valid name and the date of birth of the patient from the user-provided text without including additional information, notes, and context. 

        Please follow the below guidelines:
        1) Consider Date of Birth, Birth Date, and DOB as date_of_birth.
        2) Do not consider age as value in date_of_birth.
        3) Consider Patient Name, only Patient, only Name and RE as patient_name.

        Please strictly only provide a JSON result containing the keys 'patient_name' and 'date_of_birth' containing a string as a value.
        """

        DIAGNOSIS_TREATMENT_ENTITY_PROMPT = """
            Task: Identify diagnoses and treatments from provided text without extra information.
            
            The definition of a valid diagnosis, valid treatment and valid medications is given below:
            Diagnosis: It is a process of identifying a patient's medical condition based on the evaluation of symptoms, history, and clinical evidence.
            Treatment: It is a proven, safe, and effective therapeutic intervention aligned with medical standards, to manage or cure a diagnosed health condition.
            PMH (Past Medical History): It is a record of a patient's health information regarding previous illnesses, surgeries, injuries, treatments, and other relevant medical events in life.
                    
            Guidelines for Extraction:
            1. Exclude negated diagnosis and treatment information.
            2. Categorize diagnoses as allergy, PMH, or current condition.
            3. Include signs, injuries, chronic pain, and medical conditions as diagnoses.
            4. Avoid repetition of PMH, allergies, and clear diagnoses.
            5. Extract only therapeutic procedures, surgeries, or interventions as treatments. Include past medical procedures under treatments.
            6. Exclude specific medication names and dosages from treatments.
            7. Avoid misinterpreting symptoms as diagnoses or treatments.
            8. Include system organs and direction of organs with medical entities.
            9. Exclude hypothetical and conditional statements.
            10. Categorize entities under appropriate PMH based on identification, ensuring treatments are not included in diagnosis and vice versa.
            
            Output Response Format:
            1. Clear distinction between diagnosis and treatment entities.
            2. Exclude tests from diagnoses.
            3. Exclude medication from treatments.
            4. Exclude clinical findings, physical exam findings, and observations.
            5. Exclude doctor and patient names.
            6. Avoid repeating diagnoses and treatments if referring to the same condition or treatment.
            
            Please provide a JSON response strictly using the format below. Use this response as an example, but do not include the entity if it is not present, and include empty string values for missing keys:
            {
              "diagnosis":{
                "allergies":["Peanuts"],
                "pmh":["Type 2 Diabetes"],
                "others":["Hypertension"]
              },
              "treatments":{
                "pmh":["NORCO"],
                "others":["REST"]
              }
            } 
        """

        PROCEDURE_MEDICATION_ENTITY_PROMPT = """
        Your task is to identify valid procedures and valid medications from the user-provided text without including additional information, notes, and context.
        
        The definition of the medical terms are given below:
        PMH (Past Medical History): It is a record of a patient's health information regarding previous illnesses, surgeries, injuries, treatments, and other relevant events in life.
        Procedures: It refers to a method used to conduct tests and analyze laboratory data for health assessment.
        Medication: It refers to drugs or substances used to treat, prevent, or diagnose diseases, relieve symptoms, or improve health.
        Treatment: It is a proven, safe, and effective therapeutic intervention aligned with medical standards, to manage or cure a diagnosed health condition.
        Tests: It is a medical procedure to determine the presence or extent of a health condition.
        Laboratory Tests: It is a specific analysis performed on clinical samples to diagnose or monitor diseases.
        Dosage: It refers to the specific amount of a drug to be taken at one time or within a certain period, as prescribed by a healthcare professional.
        
        Please follow the below guidelines:
        1. Identify and categorize medications as past medical history (PMH) or current medications, including dosage.
        2. Exclude 'Medication' entity from the medication category.
        3. Extract all the procedures from the document and categorize them as tests or laboratory tests.
        4. Only include diagnostic imaging, blood tests, or other standard medical tests in the test category.
        5. Ensure that every procedure is linked with the relevant date.
        6. Ensure treatments are not mistaken as medications.
        7. Avoid repeating entities across all categories and sub-categories. For instance, if an entity is listed under procedures, do not include it in medications.
        
        Please provide a JSON response strictly using the format below. Use this response as an example, but do not include the entity if it is not present, and include empty string values for missing keys:
        {
          "procedures":{
            "test":[
              {
                "date":"2023-03-25",
                "name":"Electrocardiogram (ECG)"
              }
            ],
            "lab_test":[
              {
                "date":"2023-03-30",
                "name":"Hemoglobin A1c"
              }
            ],
            "reports":[
              {
                "date":"2023-03-31",
                "name":"MRI scan report of the brain"
              }
            ]
          },
          "medications":{
            "pmh":[
              {
                "name":"Metformin",
                "dosage":"500 mg twice daily"
              }
            ],
            "others":[
              {
                "name":"Lisinopril",
                "dosage":"10 mg once daily"
              }
            ]
          }
        } 
        """

        SUMMARY_PROMPT = """Generate a detailed and accurate summary based on the user's input, concentrating specifically on identifying key medical diagnoses, outlining treatment plans, and highlighting pertinent aspects of the patient's medical history. Ensure precision and conciseness to deliver a focused and insightful summary, including the patient's name, age, and hospital name if provided. Avoid any suggestions or misconceptions not presented in the document."""

        CONCATENATE_SUMMARY = "Concatenate the summaries and remove the duplicate information from the summaries and make one summary without losing any information."

        HISTORY_PROMPT = """
        Model Instructions:
        Social History:
        Smoking: Check if there is any history of smoking (current or past). If there is, respond with "Yes" for both "Smoking" and "Tobacco". If there is no smoking history, proceed to evaluate tobacco use.
        Alcohol: Determine if the patient has ever consumed alcohol. If the patient currently consumes alcohol or has in the past, respond with "Yes". If not, respond with "No".
        Tobacco: If there is no history of smoking, assess the use of smokeless tobacco products such as chewing tobacco or snuff. Respond with "Yes" for "Tobacco" only if such non-smoking tobacco use is present. If there is no use of any tobacco products, respond with "No" for both "Smoking" and "Tobacco".

        Family History:
        Additional Information: Do not generate information beyond what is provided.
        Medical vs. Family History: Do not confuse the patient's medical history with their family history.
        Condition Details: List only the names of medical conditions, omitting details like onset, age, or timing.
        Key-Value Pairs: Use key-value pairs to represent significant medical histories of family members. The key is the family member's relation to the patient, and the value is a concise description of their significant medical history.
        Unspecified Relations: If a relation is not specified, use "NotMentioned" as the key. Do not include the "NotMentioned" key if there is no significant history.
        Exclusions: Leave out family members without a significant medical history, non-medical information, and personal identifiers. Focus solely on health conditions relevant to the patient's medical or genetic predisposition. Also exclude outputs such as {'NotMentioned': 'None'} because it is irrelevant for usecase. 

        JSON Template:
        Fill in the JSON template with the appropriate responses based on the medical text provided. Ensure that only family members with significant medical histories are included in the "Family_History" section.
        {
          "Social_History": {
            "Smoking": "Yes or No",
            "Alcohol": "Yes or No",
            "Tobacco": "Yes or No"
          },
          "Family_History": {
            // Insert key-value pairs for family members with significant medical history
            // Omit entries for family members without significant history
          }
        }
        """

        PSYCHIATRIC_INJURY_PROMPT = """
        Instructions for the model:
        Psychiatric Injury:       
        Compile a list of the names of psychiatric injuries or disorders the patient may have. This should encompass any diagnosed mental illnesses, traumatic brain injuries, psychological traumas, or other psychiatric conditions.
        Provide only the names of the psychiatric injuries or disorders without any additional details such as onset, treatment, or management strategies.

        Extract the relevant information from the provided medical text regarding the patient's psychiatric injuries or disorders and record your findings in the JSON template provided below:
        {
          "Psychiatric_Injury": ["name of injury or disorder", "another injury or disorder", ...]
        }
        """

        PATIENT_DEMOGRAPHICS_PROMPT = """
        Your task is to identify the name, date of birth, age, gender, height and weight from the user-provided text without including additional information, notes, and context.

        Please follow the below guidelines:
        1) Consider Date of Birth, Birth Date, and DOB as date_of_birth.
        2) Use Age or years old to identify the patient's age. Do not derive age from the date_of_birth. If multiple age values are mentioned, choose the highest value.
        3) Consider Patient Name, only Patient, only Name, and RE as patient_name.
        4) Use Gender, Sex, Male, Female, M, F, Mr. , Mrs. to identify the patient's gender. Do not assume or derive gender from the patient_name.
        5) Use Height, Ht to identify the patient's height. Strictly provide the height in inches only. If the height value of patient is present multiple time, ensure to return the current height of the patient.
            - Also provide the recent date on which the measurements of height were taken.
        6) Use Weight, Wt to identify the patient's weight. Strictly provide the weight in pounds only. If the weight value of patient is present multiple time, ensure to return the current weight of the patient.
            - Also provide the recent date on which the measurements of height were taken.
        7) The `date` for both `height` and `weight` should be the most recent date on which these measurements were taken.
        8) Don't provide your analysis in the final response.
        9) If the weight is present in kilograms(kgs), convert it into pounds(lbs).
        10) If the height is present in centimeters(cm), convert it into inches(in).

        Please strictly only provide a JSON result as given below:
        {
          "patient_name": "",
          "date_of_birth": "",
          "age": "",
          "gender": "",
          "height": {
            "value": "",
            "date": ""
          },
          "weight": {
            "value": "",
            "date": ""
          }
        }

        Ensure that height and weight are accurately reflected according to the specified units of measurement.
        Note: If any of the value is not found, fill the value with an empty string.
        """

    class LineRemove:
        SUMMARY_FIRST_LAST_LINE_REMOVE = [
            'Based on the provided',
            'Here is a detailed',
            'Here is a consolidated',
            'Based on the',
            'Based on the detailed',
            'Based on the provided',
            'Based on the information provided',
            'Here is the',
            'In summary,']
