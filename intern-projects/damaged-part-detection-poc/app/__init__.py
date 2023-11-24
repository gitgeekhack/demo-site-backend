from app.resource.model_detect import damage_detect_app

from app.manage import create_app

app, logger = create_app()
app.register_blueprint(damage_detect_app)
