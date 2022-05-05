import re
from datetime import datetime

from app import logger
from app.constant import Gender, Parser, EyeHairColor

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
