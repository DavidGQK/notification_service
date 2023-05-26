import logging

import logstash
from flask import Flask, Response, request

from core.config import settings


class RequestIdFilter(logging.Filter):
    def __init__(self, name: str | None = None, response: Response | None = None) -> None:
        self.name = name
        self.response: Response = response
    
    def filter(self, record):
        record.request_id = request.headers.get('X-Request-Id')
        record.tags = ['auth_api']
        record.status = self.response.status_code
        record.request = request
        return True


def init_logs(app: Flask):
    logstash_handler = logstash.LogstashHandler(settings.logstash_host, settings.logstash_port, version=1)
    logger = logging.getLogger(app.name)
    app.logger = logger
    app.logger.addHandler(logstash_handler)
    app.logger.setLevel(settings.log_level)
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.setLevel(settings.log_level)
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(module)s - %(funcName)s - line:%(lineno)d - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    uvicorn_access_logger.addHandler(ch)
    app.logger.addHandler(ch)
