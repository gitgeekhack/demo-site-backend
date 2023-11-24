import os
import traceback
from PIL import Image
from flask import Flask, render_template, request, url_for, redirect, Blueprint
from werkzeug.utils import secure_filename
from app.services.model_detect import DamageDetect
from app.common.utils import make_dir
from app.constant import Path
from app.constant import Extension

damage_detect_app = Blueprint('damage_detect', __name__, static_folder="static")

app = Flask(__name__)


def allowed_file(filename):
    filename = filename.lower()
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in Extension.ALLOWED_EXTENSIONS


@damage_detect_app.route('/')
def index():
    return render_template('index.html')


@damage_detect_app.route('/damage-detection/')
def damage_detection():
    damage_detect = DamageDetect()
    try:
        file_error = request.args.get("file_error")
        if file_error:
            return render_template('damage-detection.html',
                                   file_error=True)
        images = request.args.get("image")
        if images:
            results = damage_detect.detect(images)
            response = render_template('damage-detection.html', results=results)
            return response
        else:
            return render_template('damage-detection.html')
    except Exception as e:
        print('%s -> %s', e, traceback.format_exc())
        response = render_template('damage-detection.html',
                                   error=True)
        return response


@damage_detect_app.route('/upload', methods=['POST'])
def upload_img():
    files = request.files.getlist("file")
    filenames = []
    make_dir(Path.STATIC_PATH + Path.UPLOADED_PATH)
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = Path.STATIC_PATH + Path.UPLOADED_PATH
            file_path = os.path.join(path, filename)
            file.save(file_path)
            image = Image.open(file_path)
            if Extension.PNG in filename.lower():
                image = image.convert("RGB")
                filename = filename.split(".")[0] + Extension.JPG
                file_path = os.path.join(Path.UPLOADED_PATH, filename)
            basewidth = 640
            if image.size[0] > basewidth:
                wpercent = (basewidth / float(image.size[0]))
                hsize = int((float(image.size[1]) * float(wpercent)))
                image = image.resize((basewidth, hsize), Image.ANTIALIAS)
            image.save(file_path)
            image.close()
            filenames.append(filename)
        else:
            return redirect(url_for('index', file_error=True))
    return redirect(url_for('damage_detect.damage_detection', image=','.join(filenames)))

