from elasticsearch import Elasticsearch
import os
from app.common.utils import read_properties_file, MonoState, load_config
from app.constant import APP_ROOT
from app.config import CONFIG


# class for database connection activities
class DatabaseConnection:
    def __init__(self):
        self.config = read_properties_file(os.path.join(APP_ROOT, "environment.properties"))
        self.config_name = os.getenv('APPLICATION_ENVIRONMENT', self.config['environment'])
        self.config_environment = load_config(CONFIG[self.config_name])

    def connect(self):
        es = Elasticsearch(self.config_environment.HOST,
                           basic_auth=(self.config_environment.USERNAME, self.config_environment.PASSWORD),
                           verify_certs=False)
        return es

    def close(self, es):
        es.close()
