class Endpoints:
    PINGER = '/ping'

    class API:
        class V1:
            class RandomString:
                GENERATE = '/api/v1/random-string/generate'


class ErrorMessage:
    INTERNAL_SERVER_ERROR = 'Internal Server Error'
