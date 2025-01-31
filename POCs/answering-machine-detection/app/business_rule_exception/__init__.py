from app.constant import ExceptionMessage


class InvalidFile(Exception):

    def __init__(self, file_url, message=ExceptionMessage.INVALID_FILE_EXCEPTION_MESSAGE):
        self.message = message
        self.file_url = file_url
        super().__init__(self.message)

    def __str__(self):
        return f'{self.file_url} -> {self.message}'


class FileLimitExceeded(Exception):

    def __init__(self, file_url, message=ExceptionMessage.FILE_LIMIT_EXCEEDED_EXCEPTION_MESSAGE):
        self.message = message
        self.file_url = file_url
        super().__init__(self.message)

    def __str__(self):
        return f'{self.file_url} -> {self.message}'


class FilePathNull(Exception):

    def __init__(self, message=ExceptionMessage.FILE_PATH_NULL_EXCEPTION_MESSAGE):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'


class MultipleFileUploaded(Exception):

    def __init__(self, message=ExceptionMessage.MULTIPLE_FILE_UPLOADED_EXCEPTION_MESSAGE):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'


class MissingRequestBody(Exception):

    def __init__(self, message=ExceptionMessage.MISSING_REQUEST_BODY_EXCEPTION_MESSAGE):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'


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


class ShortAudioLengthException(Exception):
    def __init__(self, message=ExceptionMessage.SHORT_AUDIO_LENGTH_EXCEPTION_MESSAGE):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'
