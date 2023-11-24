import os

from app.business_rule_exception import UnableToGetEnvironmentVariableException

CONFIG = {
    "production": "app.config.ProductionConfig",
    "staging": "app.config.StagingConfig",
    "development": "app.config.DevelopmentConfig"
}


def get_environment_var(variable):
    value = os.getenv(variable, None)
    if not value:
        raise UnableToGetEnvironmentVariableException(variable)
    return value


class BaseConfig(object):
    APP_VERSION = '1.0.0'
    TESSERACT_PATH = get_environment_var('Tesseract_PATH')
    TEMP_FOLDER_PATH = './app/data/temp/'
    ABREVS_MAPPING_FILE_PATH = './app/data/make_abbreviation_mapping.csv'
    CHECK_BOX_TEMPLATE_PATH = './app/data/checkbox_template.png'


class ProductionConfig(BaseConfig):
    ENVIRONMENT = 'production'
    API_KEY = 'dPP194ijPCObGCoRtD15R866w1XA4rsY'
    DEBUG = False
    HOST = 'http://127.0.0.1/'


class StagingConfig(BaseConfig):
    ENVIRONMENT = 'staging'
    API_KEY = 'dPP194ijPCObGCoRtD15R866w1038HsP'
    DEBUG = False
    HOST = 'http://127.0.0.1/'
    TEMP_FOLDER_PATH = '/var/underwriting-automation/volume/'


class DevelopmentConfig(BaseConfig):
    ENVIRONMENT = 'development'
    API_KEY = 'hXCQjAvi5ScCZk3cjBEEak5lLc038Hkb'
    DEBUG = True
    HOST = 'http://127.0.0.1:8080/'
