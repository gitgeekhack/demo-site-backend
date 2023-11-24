import os

import aiohttp_jinja2

from app.manage import create_app
from aiohttp import web
import jinja2

app, logger = create_app()

from app.resource.pinger import Pinger
from app.resource.random_string import Generator, Index

app.router.add_view('/', Index)
app.router.add_view('/generator', Generator)

