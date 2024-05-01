import os


class ExceptionMessage:
    INVALID_FILE_EXCEPTION_MESSAGE = 'Input file is invalid'
    FILE_LIMIT_EXCEEDED_EXCEPTION_MESSAGE = "File limit exceeded, only upload file upto 25 MB"
    FILE_PATH_NULL_EXCEPTION_MESSAGE = "File is not uploaded"
    MULTIPLE_FILE_UPLOADED_EXCEPTION_MESSAGE = "Multiple files are uploaded, only upload single file"
    MISSING_REQUEST_BODY_EXCEPTION_MESSAGE = "Missing request body in the request"
    SHORT_AUDIO_LENGTH_EXCEPTION_MESSAGE = 'Audio duration below the designated threshold. The minimum required duration is 2 seconds.'


headers = {
    'Access-Control-Allow-Origin': "*",
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS, PUT, DELETE',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
}


class S3:
    AWS_KEY_PATH = "user-data"
    LOCAL_PATH = "static"
    BUCKET_NAME = 'answering-machine-detection-ds'
    ENCRYPTION_KEY = eval(os.getenv("S3_ENCRYPTION_KEY"))
    PREFIX = "s3://answering-machine-detection-ds/"
