import os

environment = os.getenv('FLASK_CONFIGURATION', 'staging')

if environment.lower() == 'production':
    API_KEY = 'C8D6F8FB18C27'

else:
    API_KEY = 'D85718A11A3B6'
