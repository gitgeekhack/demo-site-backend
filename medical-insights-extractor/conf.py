from app import logger
import subprocess
from os import environ

# Run tests
logger.info("Running tests...")
test_result = subprocess.run(["pytest"], capture_output=True, text=True, cwd="/medical-insights/tests")
logger.info(test_result.stdout)

# Check test result
if test_result.returncode == 0:
    logger.info("Tests passed successfully. Proceeding to start the server...")
    # Start server
    """gunicorn WSGI server configuration."""
    bind = '0.0.0.0:' + environ.get('PORT', '8083')
    max_requests = 1000
    worker_class = 'aiohttp.worker.GunicornWebWorker'
    workers = 2
    timeout = 3600
    server_command = ["gunicorn", "-b", bind, "-w", str(workers), "-k", worker_class, "--max-requests",
                      str(max_requests), "--timeout", str(timeout), "app:app"]
    subprocess.run(server_command)

else:
    logger.error("Tests failed. Aborting server start.")
