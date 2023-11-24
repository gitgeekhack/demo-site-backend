from aiohttp import web
from app.resources import WebhookHandler

async def handler(request):
    req = await request.json()
    res = await WebhookHandler.handle_webhook(req)
    return web.Response(text=res)
