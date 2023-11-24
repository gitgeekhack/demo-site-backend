import json

import requests
from model_training_app.config import Config, Constant

response = requests.get(Config.URL, params={"key": Config.API_KEY})
data = response.json()
with open(Constant.DATA_FILE_PATH, 'w') as f:
    json.dump(data, f)
