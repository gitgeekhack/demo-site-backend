
import os

from flask import Blueprint
from flask import send_file

parent_dir = os.path.dirname(os.path.abspath(__file__))
download_app = Blueprint('common', __name__)

@download_app.route("/download/<file>")
def download(file):
    file_path = os.path.join('temp_data/', file)
    file_to_return = send_file(file_path, as_attachment=True, mimetype='application/octet-stream')
    return file_to_return
