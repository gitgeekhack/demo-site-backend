from app.constants import APIEndPointURL

CONFIG = {
    "production": "app.config.ProductionConfig",
    "staging": "app.config.StagingConfig"
}


class BaseConfig(object):
    TMP_STORAGE_PATH = 'app/temp_data'
    ALLOWED_EXT = ['jpg', 'jpeg', 'pdf', 'png']
    MODEL_PATH = "app/model"


class ProductionConfig(BaseConfig):
    API_KEY = 'C8D6F8FB18C27'
    HOST_URL = 'http://demo.marutitech.com:7878'
    PDF_TO_IMAGE_API_URL = HOST_URL + APIEndPointURL.PDF_EXTRACT_FIRST_IMAGE_ENDPOINT_URL


class StagingConfig(BaseConfig):
    API_KEY = 'D85718A11A3B6'
    HOST_URL = 'http://127.0.0.1:8000'
    PDF_TO_IMAGE_API_URL = HOST_URL + APIEndPointURL.PDF_EXTRACT_FIRST_IMAGE_ENDPOINT_URL
