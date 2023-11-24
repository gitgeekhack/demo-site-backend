class ExceptionMessage:
    INVALID_FILE_EXCEPTION_MESSAGE = 'Inputted file is invalid'
    FAILED_TO_DOWNLOAD_FILE_FROM_URL_EXCEPTION_MESSAGE = 'Unable to download file from url'
    NO_IMAGE_FOUND_EXCEPTION_MESSAGE = "Unable to find image in PDF"


class APIEndPointURL:
    PDF_EXTRACT_FIRST_IMAGE_ENDPOINT_URL = "/api/v1/internal/pdf-extract-first-image"
    BARCODE_EXTRACT_API_ENDPOINT_URL= "/api/v1/integration/mahindra-logistics/detect-pod"

class APIErrorMessage:
    BAD_REQUEST_PARAMS_MISSING_MESSAGE="one or more parameter is missing"
    NO_IAMGE_IN_PDF_MESSAGE="Unable to find image in PDF"
    UNABLE_TO_DOWNLOAD_FILE_MESSAGE="Unable to get input file"
    INVALID_FILE_MESSAGE="Invalid input file"