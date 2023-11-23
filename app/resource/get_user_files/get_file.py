import os
from aiohttp import web
from app.constant import USER_DATA_PATH


class GetResourceData(web.View):
    async def get(self):
        try:
            file_name = self.request.query['file_name']
            filepath = os.path.join(USER_DATA_PATH, file_name)
            with open(filepath, 'rb') as file:
                file_data = file.read()

                # Set response headers to specify the file name and content type
                content_type = 'application/octet-stream'

                # Set response headers to specify the file name and content type
                headers = {
                    'Content-Disposition': f'attachment; filename="{file_name}"',
                    'Content-Type': content_type,
                }

                # Return the file data as a response
                return web.Response(body=file_data, headers=headers)

        except FileNotFoundError:
            return web.Response(text='File not found', status=404)

        except Exception as e:
            return web.Response(text=f'Error: {str(e)}', status=500)
