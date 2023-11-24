"""
This module contains constants used in the car damage detection application.

Attributes:
    MODEL_PATH (str): The file path to the car damage detection model.
    UPLOAD_PATH (str): The file path to the directory where uploaded images are stored.
    PREDICT_PATH (str): The file path to the directory where predicted images are saved.
    TEMPLATE_FOLDER (str): The file path to the directory containing HTML templates.
    STATIC_FOLDER (str): The file path to the directory containing static files like CSS.
"""


class Path:
    MODEL_PATH = "app/model/car_damage_detection.pt/"
    UPLOAD_PATH = "app/static/uploads/"
    PREDICT_PATH = "app/static/predict/"
    TEMPLATE_FOLDER = "../app/templates"
    STATIC_FOLDER = "../app/static"

