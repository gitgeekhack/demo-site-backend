from fitz.fitz import FileNotFoundError
from app.common.utils import is_image_file, is_pdf_file, get_pdf_page_count, is_allowed_file

pytest_plugins = ('pytest_asyncio',)


class TestUtils:
    def test_is_image_file_with_valid_file(self):
        file = "data/image/sample_image1.jpeg"
        assert is_image_file(file)

    def test_is_image_file_with_invalid_file(self):
        file = "data/pdf/Sample1.pdf"
        assert not is_image_file(file)

    def test_is_pdf_file_with_valid_file(self):
        file = "data/pdf/Sample1.pdf"
        assert is_pdf_file(file)

    def test_is_pdf_file_with_invalid_file(self):
        file = "data/image/sample_image1.jpeg"
        assert not is_pdf_file(file)

    def test_get_pdf_page_count_with_pdf_file(self):
        file_path = "data/pdf/Sample1.pdf"
        assert get_pdf_page_count(file_path) == 2

    def test_get_pdf_page_count_with_image_file(self):
        file_path = "data/image/sample_image1.jpeg"
        assert get_pdf_page_count(file_path) == 1

    def test_get_pdf_page_count_with_invalid_file_path(self):
        file_path = "./data/data_utils/sample.pdf"
        try:
            count = get_pdf_page_count(file_path)
        except FileNotFoundError:
            assert True

    def test_is_allowed_file_with_valid_name_and_extension(self):
        filename = "Sample1.jpg"
        allowed_extensions = ['jpg', 'jpeg', 'pdf']
        assert is_allowed_file(filename, allowed_extensions)

    def test_is_allowed_file_with_invalid_extension(self):
        filename = "Sample1.json"
        allowed_extensions = ['jpg', 'jpeg', 'pdf']
        assert not is_allowed_file(filename, allowed_extensions)

    def test_is_allowed_file_with_invalid_filename(self):
        filename = "Sample1jpg"
        allowed_extensions = ['jpg', 'jpeg', 'pdf']
        assert not is_allowed_file(filename, allowed_extensions)
