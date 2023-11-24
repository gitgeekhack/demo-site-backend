from aiohttp import web

from app import logger
from app.service.helper.authentication import BearerToken


def required_authentication(f):
    async def wrapper(*args, **kwargs):
        request = args[0].request
        headers = request.headers
        token = headers.get('Authorization', None)
        token = token.split()[1] if token else token
        if BearerToken().validate(token):
            return await f(*args, **kwargs)

        logger.warning(f'Authentication failed dumping request data url: {request.url} headers: {headers}')
        return web.json_response({"message": 'Unauthorized'}, status=401)

    return wrapper
