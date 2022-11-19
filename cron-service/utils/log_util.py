import logging
import uuid
from flask import has_request_context, g
import sys
import os 

class RequestFilter(logging.Filter):
    """
    This will add the g.request_id to the logger
    """
    def filter(self, record):
        if has_request_context():
            if getattr(g, 'request_id', None):
                record.request_id = g.request_id
            else:
                new_id = uuid.uuid4()
                record.request_id = new_id
                g.request_id = new_id
        else:
            record.request_id = '-'
        return record


def get_log_handler():
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(os.getenv("LOG_LEVEL"))
    handler.setFormatter(logging.Formatter("{\"request-id\": \"%(request_id)s\", \"@timestamp\": \"%(asctime)s\", \"module\": \"[%(name)s]\", \"function\": \"%(funcName)s: %(lineno)s\", \"levelname\": \"%(levelname)s\", \"message\": \"%(message)s\", \"levelname\": \"%(levelname)s\"}"))
    handler.addFilter(RequestFilter())
    return handler

def get_logger(logger_name):

    logger = logging.getLogger(logger_name)
    logger.setLevel(os.getenv("LOG_LEVEL"))
    logger.addHandler(get_log_handler())
    logger.propagate = False
    return logger