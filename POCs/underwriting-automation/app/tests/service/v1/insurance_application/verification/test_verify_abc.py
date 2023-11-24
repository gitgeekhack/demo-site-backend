from app.service.api.v1.insurance_application.verifier_v1 import verify_abc

async def test_is_equal_valid_date():
    x = '1998-08-09'
    y = '1998-08-09'
    abc = verify_abc.VerifyABC(uuid='', data='')
    x = await abc.is_equal_date(x,y)
    assert x == True


async def test_is_equal_different_dates():
    x = '1998-08-09'
    y = '1998-09-09'
    abc = verify_abc.VerifyABC(uuid='', data='')
    x = await abc.is_equal_date(x, y)
    assert x == False

async def test_is_equal_int():
    x = 2020
    y = 2020
    abc = verify_abc.VerifyABC(uuid='', data='')
    x = await abc.is_equal(x, y)
    assert x == True

async def test_is_equal_int_invalid():
    x = 2020
    y = 2002
    abc = verify_abc.VerifyABC(uuid='', data='')
    x = await abc.is_equal(x, y)
    assert x == False

async def test_is_equal_names():
    x = 'Alfonso Soto'
    y = 'Soto Alfonso'
    abc = verify_abc.VerifyABC(uuid='', data='')
    x = await abc.is_equal(x, y)
    assert x == True

async def test_is_equal_names_invalid():
    x = 'Alfonso Soto'
    y = 'Soto Ricardo Alfonso'
    abc = verify_abc.VerifyABC(uuid='', data='')
    x = await abc.is_equal(x, y)
    assert x == False

async def test_is_equal_names_none_invalid():
    x = 'Alfonso Soto'
    y = None
    abc = verify_abc.VerifyABC(uuid='', data='')
    x = await abc.is_equal(x, y)
    assert not x

async def test_is_subset_invalid():
    x = 'Alfonso Soto'
    y = None
    abc = verify_abc.VerifyABC(uuid='', data='')
    x = await abc.is_equal(x, y)
    assert not x

async def test_is_subset_names_valid():
    x = 'Alfonso Soto'
    y = 'Soto Ricardo Alfonso'
    abc = verify_abc.VerifyABC(uuid='', data='')
    x = await abc.is_subset(x, y)
    assert x == True

async def test_is_subset_names_invalid():
    x = 'Ricardo Corona'
    y = 'Soto Ricardo Alfonso'
    abc = verify_abc.VerifyABC(uuid='', data='')
    x = await abc.is_subset(x, y)
    assert x == False