from enum import Enum


class Parser:
    class Regx:
        NAME = r'([A-Z]{3,14}[\s]{0,1}([A-Z]{3,14})[\s]{0,1}([A-Z]{0,14}))(([\s]{0,1}[,]{0,1}[\s]{0,1}([A-Z]{0,4}))|)'
        DATE = r'([0-9]{0,2}[\/-]([0-9]{0,2})[\/-][0-9]{0,4})'
        LICENSE_NUMBER = r'([0-9A-Z]{1})[\S]([0-9A-Z\-*]*[0-9A-Z\-*\s]*)'
        ADDRESS = r'([0-9]{2,5}\w+[\s]{0,1})([A-Z\s0-9\-,#]*[0-9]{3})'
        GENDER = r'^[MF]{1}'
        HEIGHT = r'''\d{1}'{0,1}-{0,1}\d{1,2}\"{0,1}'''
        WEIGHT = r'(?<=[WGTwgt]){0,3}(\d{2,4})(?<=[lbLB]){0,2}'
        HAIR_COLOR = r'(\w{3,4})'
        EYE_COLOR = r'(\w{3,4})'
        LICENSE_CLASS = r"(\s{1}\w{1,2}$)|((?<=CLASS)\w{1,2}$)|((?<=CLASSIFICATION)\w{1,2}$)"


class Gender(Enum):
    FEMALE = 'female'
    MALE = 'male'

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


class DrivingLicense:
    class ObjectDetection:
        DL_OBJECT_DETECTION_MODEL_PATH = './app/model/driving_license/DLObjectDetection.pt'
        YOLOV5 = 'ultralytics/yolov5:v6.0'
        MODEL_CONFIDENCE = 0.49
        OBJECT_LABELS = {0: 'license_number', 1: 'name', 2: 'address', 3: 'date', 4: 'gender', 5: 'height',
                         6: 'weight', 7: 'hair_color', 8: 'eye_color', 9: 'license_class'}

    class RegexCollection:
        DATE_REGEX = '(\d{2})[/.-](\d{2})[/.-](\d{4})$'


class AllowedFileType:
    IMAGE = ['jpg', 'png', 'jpeg']


class ExceptionMessage:
    INVALID_INSURANCE_COMPANY_NAME = 'Inputted application is of invalid insurance company'
    INVALID_FILE_EXCEPTION_MESSAGE = 'Inputted file is invalid'
    FAILED_TO_DOWNLOAD_FILE_FROM_URL_EXCEPTION_MESSAGE = 'Unable to download file from url'
    INVALID_PDF_STRUCTURE_TYPE = 'file has invalid pdf structure'
    UNABLE_TO_GET_ENVIRONMENT_VARIABLE = 'Unable to get environment variable'
    FILE_NOT_FOUND = 'file not found in temporary folder'
    MISSING_DOCUMENTS = 'one or more documents missing'
    UNABLE_TO_EXTRACT_NAME = 'Unable to extract name'
    UNABLE_TO_EXTRACT_EOD_SECTION = 'Unable to extract end of the document'
    UNABLE_TO_EXTRACT_DATE = 'Unable to Extract Date'
    UNABLE_TO_EXTRACT_DATAPOINT = 'Request ID: [{}] -> Unable to extract {}'


class EyeHairColor:
    color = {'SIL': 'Silver', 'AUB': 'Auburn', 'BAL': 'Bald', 'BGE': 'Beige', 'BLK': 'Black', 'BLD': 'Blonde',
             'BLN': 'Blonde', 'BLU': 'Blue', 'DBL': 'Blue, Dark', 'LBL': 'Blue, Light', 'BRO': 'Brown', 'BRN': 'Brown',
             'MAR': 'Maroon', 'COM': 'Stainless Steel', 'CPR': 'Copper', 'CRM': 'Ivory', 'GLD': 'Gold', 'GRY': 'Gray',
             'GRN': 'Green', 'DGR': 'Green, Dark', 'LGR': 'Green, Light', 'HAZ': 'Hazel', 'LAV': 'Lavender',
             'ONG': 'Orange', 'PNK': 'Pink', 'PLE': 'Purple', 'RED': 'Red', 'TAN': 'Tan', 'TRQ': 'Turquoise',
             'WHI': 'White','YEL': 'Yellow'}
