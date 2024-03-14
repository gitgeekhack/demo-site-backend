"""
The Authentication helper signifies helper class which provides necessary supporting methods used in API authentication
"""

from app.config import API_KEY

class BearerToken:
    """Contains validate method which verifies the API Key"""
    @staticmethod
    def validate(token):
        return token and token == API_KEY