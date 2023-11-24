from app.constant import ExceptionMessage

class InvalidFile(Exception):

    def __init__(self, file_url, message=ExceptionMessage.INVALID_FILE_EXCEPTION_MESSAGE):
        self.message = message
        self.file_url = file_url
        super().__init__(self.message)

    def __str__(self):
        return f'{self.file_url} -> {self.message}'


class MissingRequiredParameter(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'




class InvalidFileException(Exception):

    def __init__(self, message=ExceptionMessage.INVALID_FILE_EXCEPTION_MESSAGE):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'

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
