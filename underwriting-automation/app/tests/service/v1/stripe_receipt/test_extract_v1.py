import fitz
import io
from app.service.api.v1.stripe_receipt import extract_v1
from app.service.helper.pdf_helper import PDFHelper

file_name = 'app/data/temp/test_data/294.90.pdf'
document_url = 'http://127.0.0.1:8080/download/example/stripe/294.90.pdf'
invalid_doc = fitz.open('app/data/temp/test_data/BROKER_PKG_Alfonso Soto.pdf', filetype="pdf")
invalid_document_url = 'http://127.0.0.1:8080/download/example/broker_package/BROKER_PKG_Alfonso Soto.pdf'


async def test_get_receipt_number_valid():
    f = open(file_name, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.STRPDataPointExtractorV1(uuid='89c5de1c-4d25-11ec-8623-d1e221452fcd',
                                              file=file)
    response = '1768-7259'
    x = await obj._STRPDataPointExtractorV1__get_receipt_number()
    assert x == response


async def test_get_amount_paid_valid():
    f = open(file_name, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.STRPDataPointExtractorV1(uuid='89c5de1c-4d25-11ec-8623-d1e221452fcd',
                                              file=file)
    response = 294.9
    x = await obj._STRPDataPointExtractorV1__get_amount_paid()
    assert x == response


async def test_get_payment_date_valid():
    f = open(file_name, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.STRPDataPointExtractorV1(uuid='89c5de1c-4d25-11ec-8623-d1e221452fcd',
                                              file=file)
    response = '2021-10-14'
    x = await obj._STRPDataPointExtractorV1__get_payment_date()
    assert x == response


async def test_get_payment_notes_valid():
    f = open(file_name, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.STRPDataPointExtractorV1(uuid='89c5de1c-4d25-11ec-8623-d1e221452fcd',
                                              file=file)
    response = {'card_last_4_digit': 2606}
    x = await obj._STRPDataPointExtractorV1__get_payment_notes()
    assert x == response


async def test_get_payment_notes_check_regex_valid():
    f = open(file_name, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.STRPDataPointExtractorV1(uuid='89c5de1c-4d25-11ec-8623-d1e221452fcd',
                                              file=file)
    obj.pdf_helper.metadata = (
        ('AMOUNT PAID', (176.81680297851562, 313.1219177246094, 223.6737823486328, 321.8925476074219), 0),
        ('DATE PAID', (250.45046997070312, 313.1219177246094, 283.82952880859375, 321.8925476074219), 0),
        ('PAYMENT METHOD', (344.4158020019531, 313.1219177246094, 405.5856018066406, 321.8925476074219), 0),
        ('$294.90', (176.81680297851562, 322.88262939453125, 205.262451171875, 333.84588623046875), 0),
        ('October 14, 2021', (250.45046997070312, 322.88262939453125, 313.0862731933594, 333.84588623046875), 0),
        (' -adfsf - 2606', (364.1979675292969, 322.88262939453125, 389.7745056152344, 333.84588623046875), 0))
    response = {'card_last_4_digit': 2606}
    x = await obj._STRPDataPointExtractorV1__get_payment_notes()
    assert x == response


async def test_get_amount_paid_check_regex_valid():
    f = open(file_name, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.STRPDataPointExtractorV1(uuid='89c5de1c-4d25-11ec-8623-d1e221452fcd',
                                              file=file)
    obj.pdf_helper.metadata = (
        ('AMOUNT PAID', (176.81680297851562, 313.1219177246094, 223.6737823486328, 321.8925476074219), 0),
        ('DATE PAID', (250.45046997070312, 313.1219177246094, 283.82952880859375, 321.8925476074219), 0),
        ('PAYMENT METHOD', (344.4158020019531, 313.1219177246094, 405.5856018066406, 321.8925476074219), 0),
        ('$294,929.90', (176.81680297851562, 322.88262939453125, 205.262451171875, 333.84588623046875), 0),
        ('October 14, 2021', (250.45046997070312, 322.88262939453125, 313.0862731933594, 333.84588623046875), 0),
        (' -adfsf - 2606', (364.1979675292969, 322.88262939453125, 389.7745056152344, 333.84588623046875), 0))
    response = 294929.9
    x = await obj._STRPDataPointExtractorV1__get_amount_paid()
    assert x == response


async def test_get_payment_date_valid_comma():
    f = open(file_name, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.STRPDataPointExtractorV1(uuid='89c5de1c-4d25-11ec-8623-d1e221452fcd',
                                              file=file)
    obj.pdf_helper.metadata = (
        ('AMOUNT PAID', (176.81680297851562, 313.1219177246094, 223.6737823486328, 321.8925476074219), 0),
        ('DATE PAID', (250.45046997070312, 313.1219177246094, 283.82952880859375, 321.8925476074219), 0),
        ('PAYMENT METHOD', (344.4158020019531, 313.1219177246094, 405.5856018066406, 321.8925476074219), 0),
        ('$294,929.90', (176.81680297851562, 322.88262939453125, 205.262451171875, 333.84588623046875), 0),
        ('Julio 14, 2021', (250.45046997070312, 322.88262939453125, 313.0862731933594, 333.84588623046875), 0),
        (' -2606', (364.1979675292969, 322.88262939453125, 389.7745056152344, 333.84588623046875), 0))
    response = '2021-10-14'
    x = await obj._STRPDataPointExtractorV1__get_payment_date()
    assert not x


async def test_get_amount_paid_invalid():
    f = open(file_name, "rb")
    file = io.BytesIO(f.read())
    obj = extract_v1.STRPDataPointExtractorV1(uuid='89c5de1c-4d25-11ec-8623-d1e221452fcd',
                                              file=file)
    obj.pdf_helper.metadata = (
        ('AMOUNT PAID', (176.81680297851562, 313.1219177246094, 223.6737823486328, 321.8925476074219), 0),
        ('DATE PAID', (250.45046997070312, 313.1219177246094, 283.82952880859375, 321.8925476074219), 0),
        ('PAYMENT METHOD', (344.4158020019531, 313.1219177246094, 405.5856018066406, 321.8925476074219), 0),
        ('Rs294.90', (176.81680297851562, 322.88262939453125, 205.262451171875, 333.84588623046875), 0),
        ('Julio 14, 2021', (250.45046997070312, 322.88262939453125, 313.0862731933594, 333.84588623046875), 0),
        (' -2606', (364.1979675292969, 322.88262939453125, 389.7745056152344, 333.84588623046875), 0))
    response = 294.9
    x = await obj._STRPDataPointExtractorV1__get_amount_paid()
    assert not x
