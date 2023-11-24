from flask import current_app
from flask_restful import reqparse, abort
from app.services.helper.authentication import BearerToken


def required_authentication(f):
    def wrapper(*args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('Authorization', location='headers')
        parameters = parser.parse_args()
        token = parameters['Authorization']
        token = token.split()[1] if token else token
        if BearerToken().validate(token):
            return f(*args, **kwargs)
        else:
            return abort(401, ErrorMessage="Unauthorized")

    return wrapper
