import os

import aiohttp_jinja2

from app.manage import create_app
from aiohttp import web
import jinja2

app, logger = create_app()

from app.resource.pinger import Pinger
from app.resource.driving_license.extract import Index, DLExtract

app.router.add_view('/', Index)
app.router.add_view('/dlocr', DLExtract)
