import difflib
import re
from datetime import datetime

import pandas as pd
from fuzzywuzzy import fuzz
from string import punctuation
from app.constant import DrivingLicenseParser, CertificateOfTitle

DL_REGEX = DrivingLicenseParser.Regex
COT_REGEX = CertificateOfTitle.Regex
SECTION = CertificateOfTitle.Sections


def strip_text(f):
    def wrapper(*args, **kwargs):
        args = tuple([arg.strip() if isinstance(arg, str) else arg for arg in args])
        result = f(*args, **kwargs)
        if isinstance(result, str):
            result = result.replace('\n', ' ').strip()
            return result if len(result) > 0 else None
        elif isinstance(result, list):
            result = [x.replace('\n', ' ').strip() if isinstance(x, str) else x for x in result]
        return result

    return wrapper


def try_parse_date(date):
    if '-' in date:
        for fmt in ('%m-%d-%Y', '%m-%d-%y'):
            try:
                return datetime.strptime(date, fmt)
            except ValueError:
                pass
    elif '/' in date:
        for fmt in ('%m/%d/%Y', '%m/%d/%y'):
            try:
                return datetime.strptime(date, fmt)
            except ValueError:
                pass
    return None


def longestRepeatedSubstring(str):
    n = len(str)
    LCSRe = [[0 for x in range(n + 1)]
             for y in range(n + 1)]
    res = ""
    res_length = 0

    suffix_index = 0
    for start_index in range(1, n + 1):
        for end_index in range(start_index + 1, n + 1):

            if (str[start_index - 1] == str[end_index - 1] and
                    LCSRe[start_index - 1][end_index - 1] < (end_index - start_index)):
                LCSRe[start_index][end_index] = LCSRe[start_index - 1][end_index - 1] + 1

                if LCSRe[start_index][end_index] > res_length:
                    res_length = LCSRe[start_index][end_index]
                    suffix_index = max(start_index, suffix_index)

            else:
                LCSRe[start_index][end_index] = 0

    if res_length > 0:
        for start_index in range(suffix_index - res_length + 1,
                       suffix_index + 1):
            res = res + str[start_index - 1]

    return res


@strip_text
def parse_issue_date(text):
    text = text.replace('- ', '-')
    text = text.replace(' -', '-')
    text = text.replace('/ ', '/')
    text = text.replace(' /', '/')
    text = text.replace(' ', '')
    date = re.search(DL_REGEX.DATE, text)
    if date:
        date = date.group(1)
        date = try_parse_date(date)
        if isinstance(date, datetime):
            date = date.strftime('%Y-%m-%d')
    return date


def autocorrect_city(city, cities=None):
    if cities and city:
        city = ''.join([s.capitalize() for s in city.split(' ')])
        ''' We Capitalise the first letter of the split text as it seems to work better with 
            difflib.get_close_matches library.

            EG: new york -> NewYork
        '''
        if len(city) > 0:
            similar_cities = difflib.get_close_matches(city, cities)
            city = similar_cities[0] if similar_cities else city
        return city


def parse_address(text, cities=None):
    text_group = re.findall(DL_REGEX.ADDRESS, text)
    address_texts = []
    address = ''
    if text_group:
        for group in text_group:
            temp = ''
            for i_text in group:
                if i_text not in temp:
                    temp += i_text
            address_texts.append(temp)

        address = max(address_texts, key=len).replace('  ', ' ')
        address = split_address(address=address, cities=cities)
    return address


@strip_text
def split_address(address, cities=None):
    address_split = address.split('\n')
    address = {'street': None, 'city': None, 'state': None, 'zip_code': None}
    city_state_zip = address_split[-1]
    if address_split:
        address['street'] = address_split[0].strip()
    city_state_zip_group = re.search(DL_REGEX.CITY, city_state_zip.replace(address['street'], ''))
    if city_state_zip_group:
        city = city_state_zip_group.group(1)
        address['city'] = autocorrect_city(city, cities)
        city_state_zip = city_state_zip.replace(city, '')
        zipcode = re.search(DL_REGEX.ZIPCODE, city_state_zip.replace(address['city'], ''))
        if zipcode:
            address['zip_code'] = zipcode.group()
            city_state_zip = city_state_zip.replace(address['zip_code'], '').strip()
        state_group = re.search(DL_REGEX.STATE, city_state_zip)
        if state_group:
            address['state'] = state_group.group()
        else:
            state_group = re.search(DL_REGEX.STATE_WITH_SPACE, city)
            address['state'] = state_group.group().strip() if state_group else None
    return address


@strip_text
def parse_title_number(text):
    text = text.upper()
    pos = text.find("TITLE")
    text = text.replace('TITLE NUMBER', '')
    text = text.replace('TITLE NO', '')
    text = text.replace('TITLENO', '')
    text = text.replace('TITLE', '')
    text = text.replace('NUMBER', '')
    text = text.replace('.','')
    text = text.replace('\n', ' ')
    for i_text in text.split(' '):
        if fuzz.ratio(i_text, "TITLE") > 50:
            text = text.replace(i_text, '')
        if fuzz.ratio(i_text, "NUMBER") > 50:
            text = text.replace(i_text, '')
        if i_text in punctuation:
            text = text.replace(i_text, '')
        if i_text.isalpha():
            text = text.replace(i_text, '')
    return text


@strip_text
def parse_vin(text):
    text = text.upper()
    text = text.replace('VEHICLEIDENTIFICATIONNUMBER', '')
    text = text.replace('VEHICLEIDENTIFICATION NUMBER', '')
    text = text.replace('IDENTIFICATION/HULL', '')
    text = text.replace('IDENTIFICATION', '')
    text = text.replace('VINNO', '')
    text = text.replace('VIN', '')
    text = text.replace('VEHICLE', '')
    text = text.replace('NUMBER', '')
    text = text.strip()
    for ch in punctuation:
        if ch in text:
            text = text.replace(ch, '')
    temp = longestRepeatedSubstring(text)
    if len(temp) >= 17:
        text = temp
    for i_text in text.split('\n'):
        if len(i_text) == 17:
            text = i_text
            break
        else:
            temp1 = i_text.replace(' ', '')
            if temp1.isalpha():
                text = text.replace(i_text, '')
            if temp1.isnumeric():
                text = text.replace(i_text, '')
    text = text.replace('\n', ' ')
    text = text.replace(' ', '')
    for i_text in text.split(' '):
        if len(i_text) == 17 and i_text.isalnum():
            return i_text


@strip_text
def parse_year(text):
    year = ''
    text = text.upper()
    text = text.replace('YEAR', '')
    text = text.replace('\n', ' ')
    for i_text in text.split(' '):
        if i_text.isalpha():
            text = text.replace(i_text, '')
        if len(i_text) > 4:
            text = text.replace(i_text, '')
        if i_text in punctuation:
            text = text.replace(i_text, '')
    if int(text) // 1000 > 2:
        year = text[::-1]
    year = text.strip()
    return year


@strip_text
def parse_make(text):
    make = pd.read_pickle(SECTION.MAKE_PICKLE_PATH)
    text = text.upper()
    text = text.replace('MAKEOFVEHICLE', '')
    text = text.replace('MAKEBODY', '')
    text = text.replace('MAKE', '')
    text = text.replace('VEHICLE', '')

    text = text.replace('\n', ' ')
    for i_text in text.split(' '):
        if fuzz.ratio(i_text, 'MAKE') > 49:
            text = text.replace(i_text, '')
    for i_text in text.split(' '):
        if len(i_text) < 3 and i_text not in ['MG', 'AC']:
            text = text.replace(i_text, '')
    text = text.strip()
    if text in list(make):
        return text
    text = text.split()
    expected_makes = []
    for i_text in text:
        res = [i_make for i_make in list(make) if fuzz.ratio(i_text, i_make) > 49]
        for i_make in res:
            if i_make.startswith(i_text[:3]):
                expected_makes.append([i_text, i_make])
    fuzz_score = {}
    for exp in expected_makes:
        for exp_make in exp[1:]:
            val = fuzz.ratio(exp[0], exp_make)
            fuzz_score[exp_make] = val
    try:
        max_val = max(list(fuzz_score.values()))
    except:
        return None
    result_make = list(fuzz_score.keys())[list(fuzz_score.values()).index(max_val)]
    return result_make


@strip_text
def parse_model(text):
    model = pd.read_pickle(SECTION.MODEL_PICKLE_PATH)
    text = text.upper()
    text = text.replace('DESCRIPTION', '')
    text = text.replace('NAME', '')
    text = text.replace('MODEL', '')
    text = text.replace('\n', ' ')
    text = text.strip()
    for i_text in text.split(' '):
        if fuzz.ratio(i_text, 'MODEL') > 59:
            text = text.replace(i_text, '')
    if text in list(model):
        return text
    text = text.split(' ')
    for i_text in text:
        if i_text in list(model):
            return i_text
    for i_text in text:
        if i_text[::-1] in model:
            return i_text[::-1]
    expected_models = []
    for i_text in text:
        res = [i_model for i_model in list(model) if fuzz.ratio(i_text, i_model) > 49]
        for i_make in res:
            if i_make.startswith(i_text[:3]):
                expected_models.append([i_text, i_make])
    fuzz_score = {}
    for exp in expected_models:
        for exp_make in exp[1:]:
            val = fuzz.ratio(exp[0], exp_make)
            fuzz_score[exp_make] = val
    try:
        max_val = max(list(fuzz_score.values()))
    except:
        return None
    result_model = list(fuzz_score.keys())[list(fuzz_score.values()).index(max_val)]
    return result_model


@strip_text
def parse_body_style(text):
    body_style = pd.read_pickle(SECTION.BODY_STYLE_PICKLE_PATH)
    text = text.upper()
    text = text.replace('BODY', '')
    text = text.replace('TYPE', '')
    text = text.replace('STYLE', '')
    text = text.replace('MODEL', '')
    text = text.replace('MAKES', '')
    text = text.replace('/', '')
    text = text.replace('\n', ' ')
    for i_text in text.split(' '):
        if fuzz.ratio(i_text, 'BODY') > 49:
            text = text.replace(i_text, '')
        if fuzz.ratio(i_text, 'STYLE') > 49:
            text = text.replace(i_text, '')
        if fuzz.ratio(i_text, 'MAKE') > 49:
            text = text.replace(i_text, '')
        if i_text in punctuation:
            text = text.replace(i_text, '')
        if i_text in body_style:
            text = i_text
    return text


@strip_text
def parse_owner_name(text):
    names = []
    text = text.upper()
    text = text.replace('NAMES AND ADDRESS OF REGISTERED OWNERS', '')
    text = text.replace('NAME AND ADDRESS OF VEHICLE OWNER', '')
    text = text.replace('OWNERS NAME AND ADDRESS', '')
    text = text.replace('OWNER\'S NAME AND ADDRESS', '')
    text = text.replace('REGISTERED OWNERS', '')
    text = text.replace('VEHICLE OWNER', '')
    text = text.replace('OWNER/LESSEE', '')
    text = text.replace('LESSEE', '')
    text = text.replace('OWNERS', '')
    text = text.replace('OWNER', '')
    text = text.replace('NAME', '')
    text = text.replace('ADDRESS', '')
    text = text.replace('REGISTERED', '')
    text = text.replace('*', '')
    if '\nOR' in text:
        text = text.split('\nOR')
    elif 'OR\n' in text:
        text = text.split('OR\n')
    else:
        text = text.split('\n')
    for i_text in text:
        name_group = re.findall(COT_REGEX.OWNER_NAME, i_text)
        for i_name_group in name_group:
            names.append(i_name_group)
    return names


@strip_text
def parse_lien_name(text):
    name = None
    text = text.upper()
    text = text.split('LIENHOLDER')[-1] if 'LIENHOLDER' in text else text
    text = text.split('SECURITY')[-1] if 'SECURITY' in text else text
    text = text.replace('INTEREST HOLDER/LESSOR', '')
    text = text.replace('OWNER', '')
    text = text.replace('NAME AND ADDRESS', '')
    text = text.replace('FIRST LIEN FAVOR OF', '')
    text = text.replace('FIRST LIEN', '')
    text = text.replace('LIEN HOLDER(S)', '')
    text = text.replace('SECURITY', '')
    text = text.replace('INTEREST', '')
    text = text.replace('FIRST', '')
    text = text.replace('LIEN', '')
    text = re.sub(r'\n(?=\n)', '', text)
    for i_text in text.split('\n'):
        name = re.search(COT_REGEX.LIEN_NAME, i_text)
        if name:
            return name.group(0)
    return name


@strip_text
def parse_lien_address(text, cities=None):
    texts = text.split('PO BOX') if 'PO BOX' in text else text
    text = ' '.join(texts).replace('\n', ' ')
    text = re.sub(r' (?= )', '', text)
    text_group = re.findall(DL_REGEX.ADDRESS, text)
    address_texts = []
    address = ''
    if text_group:
        for group in text_group:
            temp = ''
            for i_text in group:
                if i_text not in temp:
                    temp += i_text
            address_texts.append(temp)

        address = max(address_texts, key=len).replace('  ', ' ')
        address = split_address(address=address, cities=cities)
    return address


@strip_text
def parse_odometer_reading(text):
    odometer = ''
    text = text.upper()
    text = text.replace('MILEAGE AT TIME OF TRANSFER', '')
    text = text.replace('ODOMETER READING', '')
    text = text.replace('ODOMETER', '')
    text = text.replace('READING', '')
    text = text.replace('MILEAGE', '')
    text = text.replace('&', '')
    text = text.replace('CODE', '')
    text = text.replace('ODOM', '')
    text = text.replace('MILES', '')
    text = text.replace('\n', ' ')
    text_group = re.search(COT_REGEX.ODOMETER_READING, text)
    if text_group:
        odometer = text_group.group(0)
        odometer = odometer.replace(',', '')
    return odometer


@strip_text
def parse_doc_type(text):
    result = []
    text = text.replace('\n', ' ')
    text_group = re.findall(COT_REGEX.DOCUMENT_TYPE, text)
    if text_group:
        result = list(set(text_group))
    return result


@strip_text
def parse_title_type(text):
    result = []
    text = text.replace('\n', ' ')
    text_group = re.findall(COT_REGEX.TITLE_TYPE, text)
    if text_group:
        result = list(set(text_group))
    return result


@strip_text
def parse_remarks(text):
    result = []
    text = text.replace('\n', ' ')
    text_group = re.findall(COT_REGEX.REMARKS, text)
    if text_group:
        result = list(set(text_group))
    return result
