import traceback

from flask import jsonify, make_response, request, current_app
from flask_restful import Resource

from app.business_rule_exception import FailedToDownloadFileFromURLException, InvalidFileException
from app.constants import APIErrorMessage
from app.services.pdf_image_extraction import PDFExtractor
from app.resource.authentication import required_authentication


class PDFExtractFirstImageAPI(Resource):

    @required_authentication
    def post(self):
        try:
            body = request.json
            if not body and 'document_url' not in body.keys():
                return make_response(jsonify(message=APIErrorMessage.BAD_REQUEST_PARAMS_MISSING_MESSAGE), 400)

            document_url = body['document_url']
            obj = PDFExtractor()
            success, image = obj.extract_first_image_from_url(document_url)
            if success:
                download_url = current_app.config['HOST_URL'] + "/download/" + image
                return make_response(jsonify(success=True, image_url=download_url), 200)
            else:
                return make_response(jsonify(success=False, message=APIErrorMessage.NO_IAMGE_IN_PDF_MESSAGE), 200)
        except FailedToDownloadFileFromURLException as e:
            current_app.logger.error('%s -> %s', e, traceback.format_exc())
            return make_response(jsonify(success=False, message=APIErrorMessage.UNABLE_TO_DOWNLOAD_FILE_MESSAGE), 400)
        except InvalidFileException as e:
            current_app.logger.error('%s -> %s', e, traceback.format_exc())
            return make_response(jsonify(success=False, message=APIErrorMessage.INVALID_FILE_MESSAGE), 400)
