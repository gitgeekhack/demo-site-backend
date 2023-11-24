import os

DIMENSION = 1792
NO_OF_NEIGHBORS = 5
DISTANCE_THRESHOLD = 0.85
MAXIMUM_UPLOAD = 100


SECRET_KEY = 'asdklxjcnasdfsdfsjdkf'  # secret key for flask app

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}  # file extensions supported for our app

APP_ROOT = os.path.dirname(os.path.abspath(__file__))  # root folder of application

UPLOAD_FOLDER = APP_ROOT + '/static/Uploaded_images'  # upload folder for images

SAVED_INDEX_FOLDER = APP_ROOT + '/data/SavedIndex'  # folder path for saving faiss index

MOBILENET_V2_URL = 'https://tfhub.dev/google/imagenet/mobilenet_v2_140_224/feature_vector/4'
