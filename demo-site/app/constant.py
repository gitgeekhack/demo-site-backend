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
    PROJECT_NAME = "driving-license"

    class S3:
        AWS_KEY_PATH = "user-data"
        LOCAL_PATH = "static"
        BUCKET_NAME = 'ds-driver-license-ocr'
        ENCRYPTION_KEY = eval(os.getenv("S3_ENCRYPTION_KEY"))
        PREFIX = "s3://ds-driver-license-ocr/"

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
    PROJECT_NAME = "certificate_of_title"
    VAL_SCORE = 0.6

    class S3:
        AWS_KEY_PATH = "user-data"
        LOCAL_PATH = "static"
        BUCKET_NAME = 'ds-certificate-of-title-ocr'
        ENCRYPTION_KEY = eval(os.getenv("S3_ENCRYPTION_KEY"))
        PREFIX = "s3://ds-certificate-of-title-ocr/"

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
    PROJECT_NAME = "car_damage_detection"

    class S3:
        AWS_KEY_PATH = "user-data"
        LOCAL_PATH = "static"
        BUCKET_NAME = 'ds-car-damage-identification'
        ENCRYPTION_KEY = eval(os.getenv("S3_ENCRYPTION_KEY"))
        PREFIX = "s3://ds-car-damage-identification/"
        REQUEST_FOLDER_NAME = "request"
        RESPONSE_FOLDER_NAME = "response"

    class ColorLabels:
        CAR_DAMAGE = {"headlights": (95, 202, 255), "hood": (159, 247, 17), "front_bumper": (0, 234, 254),
                      "rear_bumper": (99, 247, 220), "front_windshield": (228, 161, 0),
                      "rear_windshield": (60, 128, 240),
                      "flat_tyre": (245, 252, 3), "damaged_mirror": (196, 221, 88), "missing_wheel": (158, 210, 250),
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
