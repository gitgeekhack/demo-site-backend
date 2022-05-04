import traceback

import aiohttp_jinja2
import jinja2
from aiohttp import web

from app import logger, app
from app.resource.authentication import required_authentication
from app.service.random_string.generate_v1 import RandomStringGeneratorV1


class Index(web.View):
    @aiohttp_jinja2.template('index.html')
    async def get(self):
        return {}


class Generator(web.View):
    @aiohttp_jinja2.template('generator.html')
    async def get(self):
        try:
            generator = RandomStringGeneratorV1()
            random_string = await generator.generate()
        except Exception as e:
            logger.error('%s -> %s', e, traceback.format_exc())
            response = {"message": 'internal server error'}
            return web.json_response(response, status=500)
        return {'response': random_string}
