from flask import current_app


class BearerToken:

    def validate(self, token):
        return token and token == current_app.config['API_KEY']
