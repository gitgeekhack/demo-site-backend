import traceback

from aiohttp import web

from app import logger
from app.constant import ErrorMessage
from app.resource.authentication import required_authentication
from app.service.api.v1 import RandomStringGeneratorV1
from datetime import datetime


class RandomStringGenerateV1(web.View):

    @required_authentication
    async def get(self):
        try:
            generator = RandomStringGeneratorV1()
            random_string = await generator.generate()
            response = {
                'data': {
                    'string': random_string,
                    'length': len(random_string)
                },
                'timestamp': datetime.utcnow().timestamp(),
                'at': datetime.utcnow().isoformat()
            }
            logger.info(response)
            return web.json_response(response)
        except Exception as e:
            logger.error('%s -> %s', e, traceback.format_exc())
            response = {"message": ErrorMessage.INTERNAL_SERVER_ERROR}
            return web.json_response(response, status=500)
