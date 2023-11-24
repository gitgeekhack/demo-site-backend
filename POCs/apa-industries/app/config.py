CONFIG = {
    "production": "app.config.ProductionConfig",
    "staging": "app.config.StagingConfig"
}


class BaseConfig(object):
    DATA_PATH = './data/data.csv'
    MODEL_PATH = './data/model/Bidirectional'


class ProductionConfig(BaseConfig):
    pass


class StagingConfig(BaseConfig):
    pass
