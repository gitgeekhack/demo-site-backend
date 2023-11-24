CONFIG = {
    "production": "app.config.ProductionConfig",
    "staging": "app.config.StagingConfig",
    "development": "app.config.DevelopmentConfig"
}


class BaseConfig(object):
    APP_VERSION = '1.0.0'


class ProductionConfig(BaseConfig):
    ENVIRONMENT = 'production'
    API_KEY = 'dPP194ijPCObGCoRtD15R866w1XA4rsY'


class StagingConfig(BaseConfig):
    ENVIRONMENT = 'staging'
    API_KEY = 'dPP194ijPCObGCoRtD15R866w1038HsP'


class DevelopmentConfig(BaseConfig):
    ENVIRONMENT = 'development'
    API_KEY = 'hXCQjAvi5ScCZk3cjBEEak5lLc038Hkb'
