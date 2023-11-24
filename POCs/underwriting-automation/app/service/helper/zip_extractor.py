import zipfile
from app import app
import io


class ZipExtractor:

    def extract_zip_folder(self, file):
        folder_name = file.filename
        with zipfile.ZipFile(io.BytesIO(file.file.read()), "r") as zip_ref:
            file_list = zip_ref.namelist()
            path = app.config.TEMP_FOLDER_PATH + folder_name.split('.')[0]
            zip_ref.extractall(path)
        return file_list, path
