import sys
sys.path.append("../../libs")

from app.constant import ExceptionMessage


class UnableToLoginException(Exception):

    def __init__(self, message=ExceptionMessage.UNABLE_TO_LOGIN_EXCEPTION_MESSAGE):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class UnableToGetEnvironmentVariableException(Exception):

    def __init__(self, message=ExceptionMessage.UNABLE_TO_GET_ENVIRONMENT_VARIABLE_EXCEPTION_MESSAGE):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class TaskNotFoundException(Exception):

    def __init__(self, message=ExceptionMessage.TASK_NOT_FOUND_EXCEPTION_MESSAGE):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class InvalidTokenException(Exception):

    def __init__(self, message=ExceptionMessage.INVALID_TOKEN_EXCEPTION_MESSAGE):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message

