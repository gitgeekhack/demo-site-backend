import re
from datetime import datetime

from app.constant import MultipleNames, Gender, Parser

REGX = Parser.Regx


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


def parse_multiple_names(text):
    multiple_names = text.split(MultipleNames.OR_KEY) if text and MultipleNames.OR_KEY in text else [text]
    return multiple_names


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


@strip_text
def parse_address(text):
    text = text.replace("\n", " ")
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

    return address


@strip_text
def parse_gender_dl(text):
    text_group = re.search(REGX.GENDER, text)
    gender = {'M': Gender.MALE.value, 'F': Gender.FEMALE.value}
    if text_group:
        _gender = gender[text_group.group(0)]
        return _gender


def parse_gender(text):
    text = text.strip().lower()
    gender = {'m': Gender.MALE.value, 'f': Gender.FEMALE.value}
    if text:
        _gender = gender[text[0]]
        return _gender
    return None


@strip_text
def parse_vin(text):
    text = text.replace('VEHICLEIDENTIFICATIONNUMBER', '')
    text = text.replace('VEHICLEIDENTIFICATION NUMBER', '')
    text = text.replace('IDENTIFICATIONNUM', '')
    text_group = re.search(REGX.VIN, text)
    if text_group:
        return text_group.group(0)


@strip_text
def parse_make(text):
    text = text.replace('MAKE', '')
    text = text.replace('\n', ' ')
    try:
        text = " ".join([x if len(x) == 4 else '' for x in text.split()]).split()[-1] if text else text
    except Exception as e:
        pass
    text_group = re.search(REGX.MAKE, text)
    if text_group:
        return text_group.group(0)


@strip_text
def parse_year(text):
    text_group = re.search(REGX.YEAR, text)
    if text_group:
        return int(text_group.group(0))


@strip_text
def parse_history(text):
    text_group = re.search(REGX.VEHICLE_HISTORY, text)
    if text_group:
        return text_group.group(0)


@strip_text
def parse_validity_date(text):
    dates = re.findall(REGX.REG_VALIDITY, text)
    if dates:
        to_date = dates[-1][0]
        try:
            to_date = datetime.strptime(to_date, '%m/%d/%Y')
        except Exception:
            to_date = None
        return to_date


@strip_text
def parse_registration_name(text):
    text = "".join(text.split('OWNER')[-1])
    text = text.replace('REGISTERED OWNER', '')
    text = text.split('\nOR ')
    text = [x + '\n' for x in text]
    texts = []
    for t in text:
        texts.append(re.findall(REGX.REG_NAME, t))
    names = []
    for text in texts:
        for text_group in text:
            if text_group:
                names.append(text_group[0])
    return names
