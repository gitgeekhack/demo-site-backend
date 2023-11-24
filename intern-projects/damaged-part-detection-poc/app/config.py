CONFIG = {
    "Production": "app.config.ProductionConfig",
    "Staging": "app.config.StagingConfig",
    "Development": "app.config.DevelopmentConfig"
}


class BaseConfig(object):
    APP_NAME = 'car-damage-detection-poc'
    APP_VERSION = '1.0'
    TEMPLATES_AUTO_RELOAD = True


class DevelopmentConfig(BaseConfig):
    ENVIRONMENT = 'Development'


class StagingConfig(BaseConfig):
    ENVIRONMENT = 'Staging'


class ProductionConfig(BaseConfig):
    ENVIRONMENT = 'Production'
