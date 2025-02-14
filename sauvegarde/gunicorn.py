"""gunicorn WSGI server configuration."""
from multiprocessing import cpu_count
from os import environ


def max_workers():
    return cpu_count() * 2 + 1

max_requests = 1000
worker_class = 'gevent'
workers = max_workers()


accesslog = "/var/log/gunicorndjango/gunicorn.access.log"
errorlog = "/var/log/gunicorndjango/gunicorn.error.log"
capture_output = True
lolevel = "info"
