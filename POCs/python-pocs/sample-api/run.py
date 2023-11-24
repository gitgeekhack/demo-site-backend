from aiohttp import web

from app import app

if __name__ == "__main__":
    if app.config.ENVIRONMENT == 'development':
        web.run_app(app, port=8080)
    else:
        web.run_app(app, port=80, access_log=None)
