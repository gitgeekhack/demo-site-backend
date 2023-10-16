import traceback
import uuid

from aiohttp import web
from app import app
from app import logger
from app.constant import ErrorCode, ErrorMessage
from app.resource.authentication import required_authentication


class Downloader(web.View):

    @required_authentication
    async def get(self):
        x_uuid = uuid.uuid1()
        file_name = self.request.match_info.get('file_name', None)
        x_uuid = self.request.rel_url.query.get('uuid', str(x_uuid))
        logger.info(f'Request ID: [{x_uuid}] File:{file_name}')

        if file_name:
            try:
                f = open(app.config.TEMP_FOLDER_PATH + file_name, "rb")
                content = f.read()
                return web.Response(body=content)
            except FileNotFoundError as e:
                logger.warning(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
                response = {"code": ErrorCode.FILE_NOT_FOUND,
                            "message": ErrorMessage.FILE_NOT_FOUND}
                logger.info(f'Request ID: [{x_uuid}]')
                return web.json_response(response, status=404)
            except Exception as e:
                logger.error(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
                response = {"message": ErrorMessage.SERVER_ERROR}
                logger.info(f'Request ID: [{x_uuid}]')
                return web.json_response(response, status=500)

        return web.json_response({"code": ErrorCode.MISSING_DOCUMENT, "message": ErrorMessage.MISSING_DOCUMENT},
                                 status=400)
