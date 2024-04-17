from aiohttp import web


class Pinger(web.View):

    async def get(self):
        print('Pinged')
        return web.json_response({"message": 'ok'})
