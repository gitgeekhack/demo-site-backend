CVAT_PROTO = 'http'
CVAT_DOMAIN = ''
CVAT_USER = ''
CVAT_MAIL = ''
CVAT_PASS = ''
CVAT_IMPORT_FORMAT = 'CVAT 1.1'
CVAT_DATASET_FORMAT = 'CVAT for images 1.1'


class CvatUrls:
    CVAT_TASK_URL_API = '{}://{}/api/v1/tasks/{}'
    CVAT_PROJECT_URL = '{}://{}/api/v1/projects?page_size=50&without_tasks=true'
    CVAT_ANNOTATION_URL = '{}://{}/api/v1/tasks/{}/annotations'
    CVAT_TASK_URL = '{}://{}/tasks/{}'


class ExceptionMessage:
    UNABLE_TO_LOGIN_EXCEPTION_MESSAGE = 'Unable to login into CVAT'
    UNABLE_TO_GET_ENVIRONMENT_VARIABLE_EXCEPTION_MESSAGE = 'Unable to get environment variable'
    TASK_NOT_FOUND_EXCEPTION_MESSAGE = 'Task not found'
    INVALID_TOKEN_EXCEPTION_MESSAGE = 'Invalid token for login'
