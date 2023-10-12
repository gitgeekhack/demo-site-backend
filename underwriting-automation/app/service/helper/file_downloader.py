import io
import traceback

import httpx

from app.business_rule_exception import FailedToDownloadFileFromURLException

from app import logger, app


async def get_file_stream(uuid, url):
    try:
        logger.info(f'Request ID: [{uuid}] Downloading: [{url}]')
        headers = {'Authorization': 'Bearer ' + app.config.API_KEY}
        params = {'uuid': uuid}
        async with httpx.AsyncClient(headers=headers, params=params) as client:
            response = await client.get(url, follow_redirects=True, timeout=5)
        logger.info(f'Request ID: [{uuid}] Response code: [{response.status_code}]')
        if response.status_code == 200:
            content = io.BytesIO(response.content)
            return content
        raise FailedToDownloadFileFromURLException(url)
    except Exception as e:

        logger.error(f'Request ID: [{uuid}] %s -> %s', e, traceback.format_exc())
        raise FailedToDownloadFileFromURLException(url)
