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
