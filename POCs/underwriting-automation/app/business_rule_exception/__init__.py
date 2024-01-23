from app.constant import ExceptionMessage


class InvalidFileException(Exception):

    def __init__(self, file_url, message=ExceptionMessage.INVALID_FILE_EXCEPTION_MESSAGE):
        self.message = message
        self.file_url = file_url
        super().__init__(self.message)

    def __str__(self):
        return f'{self.file_url} -> {self.message}'


class InvalidInsuranceCompanyException(Exception):

    def __init__(self, company_name, message=ExceptionMessage.INVALID_INSURANCE_COMPANY_NAME):
        self.message = message
        self.company_name = company_name
        super().__init__(self.message)

    def __str__(self):
        return f'{self.company_name} -> {self.message}'


class FailedToDownloadFileFromURLException(Exception):

    def __init__(self, file_url, message=ExceptionMessage.FAILED_TO_DOWNLOAD_FILE_FROM_URL_EXCEPTION_MESSAGE):
        self.message = message
        self.file_url = file_url
        super().__init__(self.message)

    def __str__(self):
        return f'{self.file_url} -> {self.message}'


class InvalidPDFStructureTypeException(Exception):

    def __init__(self, file_url, message=ExceptionMessage.INVALID_PDF_STRUCTURE_TYPE):
        self.message = message
        self.file_url = file_url
        super().__init__(self.message)

    def __str__(self):
        return f'{self.file_url} -> {self.message}'


class UnableToGetEnvironmentVariableException(Exception):
    def __init__(self, variable, message=ExceptionMessage.UNABLE_TO_GET_ENVIRONMENT_VARIABLE):
        self.message = message
        self.variable = variable
        super().__init__(self.message)

    def __str__(self):
        return f'{self.variable} -> {self.message}'


class MissingRequiredDocumentException(Exception):
    def __init__(self, variable, message=ExceptionMessage.MISSING_DOCUMENTS):
        self.message = message
        self.variable = variable
        super().__init__(self.message)

    def __str__(self):
        return f'{self.variable} -> {self.message}'


class MissingRequiredParameterException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'


class FileSizeLimitExceed(Exception):
    def __init__(self, variable, message=ExceptionMessage.SIZE_LIMIT_EXCEEDED):
        self.message = message
        self.variable = variable
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'


class MultipleFileUploaded(Exception):

    def __init__(self, message=ExceptionMessage.MULTIPLE_FILE_UPLOADED_EXCEPTION_MESSAGE):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'
