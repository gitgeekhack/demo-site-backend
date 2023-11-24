from app.constants import *


class InvalidFileException(Exception):

    def __init__(self, file_path, message=ExceptionMessage.INVALID_FILE_EXCEPTION_MESSAGE):
        self.message = message
        self.file_path = file_path
        super().__init__(self.message)

    def __str__(self):
        return f'{self.file_path} -> {self.message}'

class FailedToDownloadFileFromURLException(Exception):

    def __init__(self, file_url, message=ExceptionMessage.FAILED_TO_DOWNLOAD_FILE_FROM_URL_EXCEPTION_MESSAGE):
        self.message = message
        self.file_url = file_url
        super().__init__(self.message)

    def __str__(self):
        return f'{self.file_url} -> {self.message}'

class NoImageFoundException(Exception):

    def __init__(self, file_url, message=ExceptionMessage.NO_IMAGE_FOUND_EXCEPTION_MESSAGE):
        self.message = message
        self.file_url = file_url
        super().__init__(self.message)

    def __str__(self):
        return f'{self.file_url} -> {self.message}'
