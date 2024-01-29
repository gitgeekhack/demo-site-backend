"""gunicorn WSGI server configuration."""
from os import environ
bind = '0.0.0.0:' + environ.get('PORT', '8081')
max_requests = 1000
worker_class = 'aiohttp.worker.GunicornWebWorker'
workers = 1
timeout = 300
