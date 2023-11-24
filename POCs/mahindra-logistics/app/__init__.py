from flask_restful import Api
from app.manage import create_app
from app.resource.pinger import Pinger
from app.resource.barcode_extraction import BarCodeExtractionAPI
from app.resource.pdf_image_extraction import PDFExtractFirstImageAPI
from app.resource.download import download_app
from app.constants import APIEndPointURL
from tensorflow.python.keras.models import load_model

app = create_app()
app.register_blueprint(download_app)
api = Api(app, errors={'Exception': {'message': 'Internal Server Error'}})
api.add_resource(Pinger, "/ping")
api.add_resource(BarCodeExtractionAPI, APIEndPointURL.BARCODE_EXTRACT_API_ENDPOINT_URL)
api.add_resource(PDFExtractFirstImageAPI, APIEndPointURL.PDF_EXTRACT_FIRST_IMAGE_ENDPOINT_URL)
app.logger.info("Loading model in memory")
Model = load_model(app.config['MODEL_PATH'])
app.logger.info("Model loaded in memory")
