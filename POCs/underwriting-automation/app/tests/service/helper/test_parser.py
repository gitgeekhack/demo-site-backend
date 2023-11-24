from app.service.helper.parser import parse_date
from app.service.helper.serializer_helper import deserialize


def test_date1():
    x = parse_date('01-01-2020')
    assert x == '2020-01-01'


def test_date2():
    x = parse_date('01/01/2020')
    assert x == '2020-01-01'


def test_date3():
    x = parse_date('asdasd 01/01/2020')
    assert x == '2020-01-01'


def test_date4():
    x = parse_date('2020')
    assert not x
