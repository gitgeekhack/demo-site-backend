bind = '0.0.0.0:8082'
workers = 1
max_requests = 1000
worker_class = 'aiohttp.worker.GunicornWebWorker'
loglevel = 'info'
timeout = 300