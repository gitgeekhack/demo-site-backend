import difflib
import pickle
import re
from datetime import datetime

from fuzzywuzzy import fuzz

from app import logger
from app.constant import Gender, Parser, EyeHairColor

REGX = Parser.Regx
with open('./app/data/make.pkl', 'rb') as file:
    make = pickle.load(file)


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


@strip_text
def parse_name(text):
    text = text.replace("\nCEN", "")
    text = text.replace("FN ", "")
    text = text.replace(" FN ", "")
    text = text.replace("LN ", "")
    text = text.replace(" LN ", "")
    text = text.replace("\n", " ")
    texts = re.findall(REGX.NAME, text)
    final_text = []
    result = ''
    if texts:
        for text in texts:
            temp = ''
            for i in text:
                if i not in temp:
                    temp += i
            final_text.append(temp)

        result = max(final_text, key=len)
    return result


@strip_text
def parse_date(text):
    text = text.replace('- ', '-')
    text = text.replace(' -', '-')
    text = text.replace('/ ', '/')
    text = text.replace(' /', '/')
    text = text.replace(' ', '')
    date = re.search(REGX.DATE, text)
    if date:
        date = date.group(1)
        try:
            if '-' in date:
                date = datetime.strptime(date, '%m-%d-%Y')
            elif '/' in date:
                date = datetime.strptime(date, '%m/%d/%Y')

            if isinstance(date, datetime):
                date = date.strftime('%Y-%m-%d')
        except Exception:
            date = None
    return date


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


@strip_text
def parse_issue_date(text):
    text = text.replace('- ', '-')
    text = text.replace(' -', '-')
    text = text.replace('/ ', '/')
    text = text.replace(' /', '/')
    text = text.replace(' ', '')
    date = re.search(REGX.DATE, text)
    if date:
        date = date.group(1)
        date = try_parse_date(date)
        if isinstance(date, datetime):
            date = date.strftime('%Y-%m-%d')
    return date


@strip_text
def parse_license_number(text):
    text = text.split('LIC')[-1] if 'LIC' in text else text
    text = text.split('L ')[-1] if 'L ' in text else text
    text = text.split('LC ')[-1] if 'LC ' in text else text
    text_group = re.search(REGX.LICENSE_NUMBER, text)
    license_number = ''
    if text_group:
        license_number = text_group.group(0).replace(' ', '')

    return license_number


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
    text_group = re.findall(REGX.ADDRESS, text)
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
    address = {'street': None, 'city': None, 'state': None, 'zipcode': None}
    city_state_zip = address_split[-1]
    if address_split:
        address['street'] = address_split[0].strip()
    city_state_zip_group = re.search(REGX.CITY, city_state_zip.replace(address['street'], ''))
    if city_state_zip_group:
        city = city_state_zip_group.group(1)
        address['city'] = autocorrect_city(city, cities)
        city_state_zip = city_state_zip.replace(city, '')
        zipcode = re.search(REGX.ZIPCODE, city_state_zip.replace(address['city'], ''))
        if zipcode:
            address['zipcode'] = zipcode.group()
            city_state_zip = city_state_zip.replace(address['zipcode'], '').strip()
        state_group = re.search(REGX.STATE, city_state_zip)
        if state_group:
            address['state'] = state_group.group()
        else:
            state_group = re.search(REGX.STATE_WITH_SPACE, city)
            address['state'] = state_group.group().strip() if state_group else None
    return address


@strip_text
def parse_gender(text):
    text_group = re.search(REGX.GENDER, text)
    gender = {'M': Gender.MALE.value, 'F': Gender.FEMALE.value}
    if text_group:
        _gender = gender[text_group.group(0)]
        return _gender


@strip_text
def parse_height(text):
    SIMILAR_INCH_NUMBERS = {'8': '0'}
    text = text.split('H')[-1] if 'H' in text else text
    text_group = re.search(REGX.HEIGHT, text)
    if text_group:
        height = text_group.group(0)
        x = re.findall(r'\d', height)
        if len(x) == 3:
            if x[1] in SIMILAR_INCH_NUMBERS.keys():
                x[1] = SIMILAR_INCH_NUMBERS[x[1]]
            if int(x[1]) > 1:
                logger.info(f"""Incorrect format for height unit -> {x[0]}'{x[1]}{x[2]}\"""")
                return None
            height = f"""{x[0]}'{x[1]}{x[2]}\""""
        return height


@strip_text
def parse_weight(text):
    text_group = re.findall(REGX.WEIGHT, text)
    if text_group:
        weight = f'{text_group[-1]} lbs'
        return weight


@strip_text
def parse_hair_color(text):
    text_group = re.findall(REGX.HAIR_COLOR, text)
    if text_group:
        hair = text_group[-1]
        if hair != 'HAI' and hair in EyeHairColor.color:
            return EyeHairColor.color[hair[:3]]


@strip_text
def parse_eye_color(text):
    text_group = re.findall(REGX.EYE_COLOR, text)
    if text_group:
        eye = text_group[-1]
        excluded_text = ['EYE', 'EYES']
        if eye not in excluded_text and eye in EyeHairColor.color:
            return EyeHairColor.color[eye[:3]]


@strip_text
def parse_license_class(text):
    text_group = re.search(REGX.LICENSE_CLASS, text)
    if text_group:
        return text_group.group(0)


@strip_text
def parse_title_number(text):
    text = text.upper()
    text = text.replace('TITLE NUMBER', '')
    text = text.replace('TITLE NO', '')
    text = text.replace('TITLENO', '')
    text = text.replace('TITLE', '')
    text = text.replace('NUMBER', '')
    text = text.replace('\n', ' ')
    for i_text in text.split(' '):
        if len(i_text) > 4 and i_text.isalnum() and not i_text.isalpha():
            return i_text


@strip_text
def parse_vin(text):
    text = text.upper()
    text = text.replace('VEHICLEIDENTIFICATIONNUMBER', '')
    text = text.replace('VEHICLEIDENTIFICATION NUMBER', '')
    text = text.replace('IDENTIFICATION', '')
    text = text.replace('VINNO', '')
    text = text.replace('VIN', '')
    text = text.replace('VEHICLE', '')
    text = text.replace('NUMBER', '')
    text = text.replace('\n', ' ')
    for i_text in text.split(' '):
        if len(i_text) == 17 and i_text.isalnum() and not i_text.isalpha():
            return i_text


@strip_text
def parse_year(text):
    year = ''
    text = text.upper()
    text = text.replace('YEAR', '')
    text = text.replace('\n', ' ')
    text_group = re.search(r'(19[8-9][0-9]|20[0-9]{2})|\b([12][0-9])\b', text)
    if text_group:
        year = int(text_group.group(0))
    return year


@strip_text
def parse_make(text):
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
    prev_score = 0
    temp = None
    for i_make in make:
        score = fuzz.token_sort_ratio(text, i_make)
        if score > prev_score:
            temp, prev_score = i_make, score
    return temp


@strip_text
def parse_model(text):
    text = text.upper()
    text = text.replace('DESCRIPTION', '')
    text = text.replace('NAME', '')
    text = text.replace('MODEL', '')
    text = text.replace('\n', ' ')
    for i_text in text.split(' '):
        if fuzz.ratio(i_text, 'MODEL') > 59:
            text = text.replace(i_text, '')
    return text


@strip_text
def parse_body_style(text):
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
    return text


@strip_text
def parse_owner_name(text):
    names = []
    text = text.upper()
    text = text.replace('NAMES AND ADDRESS OF REGISTERED OWNERS', '')
    text = text.replace('NAME AND ADDRESS OF VEHICLE OWNER', '')
    text = text.replace('OWNERS NAME AND ADDRESS', '')
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
        name_group = re.findall(r'([A-Z,]{3,14}\s*[A-Z,]{1,14}\s?[A-Z\s]*)', i_text)
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
        name = re.search(r'([A-Z,]{3,14}\s+[A-Z,]{1,14}\s?[A-Z\s]*)', i_text)
        if name:
            return name.group(0)
    return name


@strip_text
def parse_lien_address(text, cities=None):
    texts = text.split('PO BOX') if 'PO BOX' in text else text
    text = ' '.join(texts).replace('\n', ' ')
    text = re.sub(r' (?= )', '', text)
    text_group = re.findall(REGX.ADDRESS, text)
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
    text_group = re.search(r'([\d,]{5,})|(EXEMPT)', text)
    if text_group:
        odometer = text_group.group(0)
        odometer = odometer.replace(',', '')
    return odometer


@strip_text
def parse_doc_type(text):
    result = []
    text = text.replace('\n', ' ')
    text_group = re.findall(r'ORIGINAL|DUPLICATE|TRANSFER CERTIFIED COPY|NEW|REPLACEMENT', text)
    if text_group:
        result = list(set(text_group))
    return result


@strip_text
def parse_title_type(text):
    result = []
    text = text.replace('\n', ' ')
    text_group = re.findall(
        r'SALVAGE|CLEAR|REBUILT|RECONSTRUCTED|ASSEMBLED|FLOOD DAMAGE|SALVAGE-FIRE|NON-REPAIRABLE|JUNK|NORMAL|STANDARD|VEHICLE',
        text)
    if text_group:
        result = list(set(text_group))
    return result


@strip_text
def parse_remarks(text):
    result = []
    text = text.replace('\n', ' ')
    text_group = re.findall(
        r'SALVAGE|CLEAR|REBUILT|RECONSTRUCTED|ASSEMBLED|FLOOD DAMAGE|SALVAGE-FIRE|NON-REPAIRABLE|JUNK|NORMAL|STANDARD|VEHICLE|ORIGINAL|DUPLICATE|TRANSFER CERTIFIED COPY|NEW|REPLACEMENT',
        text)
    if text_group:
        result = list(set(text_group))
    return result
