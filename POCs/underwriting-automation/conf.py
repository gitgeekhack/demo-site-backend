"""gunicorn WSGI server configuration."""
from os import environ

# CMD gunicorn app:app -b 0.0.0.0:80 -w 1 --worker-class aiohttp.worker.GunicornWebWorker --log-file /var/underwriting-automation/volume/api.log --capture-output

bind = '0.0.0.0:' + environ.get('PORT', '8000')
max_requests = 1000
worker_class = 'aiohttp.worker.GunicornWebWorker'
# preload_app = True
workers = 1
# capture_output = True

