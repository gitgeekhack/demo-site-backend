import traceback

from flask import jsonify, make_response, request, current_app
from flask_restful import Resource

from app.business_rule_exception import FailedToDownloadFileFromURLException, InvalidFileException
from app.constants import APIErrorMessage
from app.database import result_tracker
from app.resource.authentication import required_authentication
from app.services.barcode_extraction import BarcodeExtraction


class BarCodeExtractionAPI(Resource):

    @required_authentication
    def post(self):
        body = request.json
        success = False
        error = None
        data = None
        if body and 'document_url' in body.keys():
            document_url = body['document_url']
        else:
            return make_response(jsonify(message=APIErrorMessage.BAD_REQUEST_PARAMS_MISSING_MESSAGE), 400)
        try:
            obj = BarcodeExtraction()
            success, data = obj.extract_by_url(document_url)
            response = make_response(jsonify(success=success, data=data), 200)

        except InvalidFileException as e:
            current_app.logger.error('%s -> %s', e, traceback.format_exc())
            error = e
            response = make_response(jsonify(success=False, message=APIErrorMessage.INVALID_FILE_MESSAGE),
                                     200)
        except FailedToDownloadFileFromURLException as e:
            current_app.logger.error('%s -> %s', e, traceback.format_exc())
            error = e
            response = make_response(jsonify(success=False, message=APIErrorMessage.UNABLE_TO_DOWNLOAD_FILE_MESSAGE),
                                     200)
        except Exception as e:
            current_app.logger.error('%s -> %s', e, traceback.format_exc())
            error = e
            response = make_response(jsonify(success=False), 200)

        finally:
            if success:
                result_tracker(success, url=document_url, data=data)
            else:
                result_tracker(success, url=document_url, data=data, error=error)
        return response
