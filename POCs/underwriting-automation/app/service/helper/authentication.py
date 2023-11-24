"""
The Authentication helper signifies helper class which provides necessary supporting methods used in API authentication
"""

from app import app


class BearerToken:
    """Contains validate method which verifies the API Key"""

    def validate(self, token):
        return token and token == app.config.API_KEY
