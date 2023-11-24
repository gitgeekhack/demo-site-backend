"""
This code creates a Flask application instance and registers the blueprint object for the detection route resource.

Variables:
- web_app: Flask application instance with the `debug` flag set to `True` and the detection route blueprint registered.
"""

from app.manage import create_app
from app.resource.detection_route import blueprint

web_app = create_app(debug=True)
web_app.register_blueprint(blueprint)
