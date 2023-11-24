import json
import os

from flask import Blueprint

parent_dir = os.path.dirname(os.path.abspath(__file__))
common_app = Blueprint('common', __name__)


@common_app.route('/ping', methods=['GET', 'POST'])
def ping():
    return json.dumps({"Data": None, "ErrorCode": None, "Success": True}), 200
