from app.manage import create_app
from app.resources.route import handler
from aiohttp import web

app = create_app()

app.add_routes([web.post('/', handler)])