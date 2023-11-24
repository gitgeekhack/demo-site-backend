from app import app

from app.business_rule_exception import InvalidFileException
from app.services.helper.pdf_helper import PDFHelper
from PIL.PngImagePlugin import PngImageFile


class TestPDFHelper():

    def test_extract_first_image_successful(self):
        with app.app_context():
            PDF = PDFHelper()
            result = PDF.extract_first_image('app/tests/test_data/10389327_delivery_image_12723104.pdf')
            # result.show()
            # target_name = os.path.join('./', "extracted_img.png")
            # result.save(target_name)
            assert result
            assert PngImageFile == type(result)

    def test_extract_first_image_empty_pdf(self):
        with app.app_context():
            PDF = PDFHelper()
            result = PDF.extract_first_image('app/tests/test_data/blank.pdf')
            assert not result

    def test_extract_first_image_invalid_file(self):
        with app.app_context():
            PDF = PDFHelper()
            try:
                result = PDF.extract_first_image('app/tests/test_data/4902377_delivery_image_13432192.jpg')
                assert False

            except InvalidFileException as e:
                assert True

            except Exception as e:
                assert False
