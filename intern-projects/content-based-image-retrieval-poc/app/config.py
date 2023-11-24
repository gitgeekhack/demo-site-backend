CONFIG = {
    "Production": "app.config.ProductionConfig",
    "Staging": "app.config.StagingConfig",
    "Development": "app.config.DevelopmentConfig",
}


class BaseConfig(object):
    APP_NAME = 'Content-Based-Image-Retrieval'
    APP_VERSION = '1.0'


class DevelopmentConfig(BaseConfig):
    ENVIRONMENT = 'Development'
    HOST = "https://localhost:9200"
    USERNAME = "elastic"
    PASSWORD = "chjpVZ=wb13+pV8vWS=q"


class StagingConfig(BaseConfig):
    ENVIRONMENT = 'Staging'
    HOST = "set remote address here"
    USERNAME = "username"
    PASSWORD = "password"


class ProductionConfig(BaseConfig):
    ENVIRONMENT = 'Production'
    HOST = "set remote address here"
    USERNAME = "username"
    PASSWORD = "password"
