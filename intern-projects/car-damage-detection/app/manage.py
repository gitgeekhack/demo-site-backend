"""
This module contains the Flask application factory for the car damage detection application.

Functions:
    create_app(debug=False): Creates and configures a new Flask app.
"""
from flask import Flask
from app.constants import Path


def create_app(debug=False):
    app = Flask(__name__, template_folder=Path.TEMPLATE_FOLDER, static_folder=Path.STATIC_FOLDER)
    app.debug = debug
    return app

