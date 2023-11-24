CONFIG = {
    "Development": "app.config.DevelopmentConfig"
}


class BaseConfig(object):
    APP_NAME = 'customer-satisfaction'
    APP_VERSION = '1.0'


class DevelopmentConfig(BaseConfig):
    ENVIRONMENT = 'Development'
