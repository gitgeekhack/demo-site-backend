from flask import jsonify, make_response
from flask_restful import Resource


class Pinger(Resource):

    def get(self):
        return make_response(jsonify(message="success"), 200)
