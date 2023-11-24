"""
This module contains routes for the car damage detection application.

Attributes:
    blueprint (flask.Blueprint): A Blueprint object for grouping related routes.
"""
import flask
from flask import Blueprint, render_template
from app.services import car_damage_detection as application

blueprint = Blueprint('detection_route', __name__, url_prefix='/')


@blueprint.route('/')
def home():
    return render_template('index.html')


@blueprint.route('/predict', methods=['POST'])
def prediction():
    return application.predict(flask.request)

