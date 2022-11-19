from flask import Flask, json, jsonify, request, Response, Blueprint
from views.auth import auth
from werkzeug.datastructures import Headers
import jwt
from functools import wraps
import os
from utils.log_util import get_logger

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

app.register_blueprint(auth, url_prefix='/auth')
logger = get_logger(__name__)

@app.before_request
def before_request_func():
    logger.info("\n***********************************************")
    logger.info("REQUEST METHOD: %s", request.method)
    logger.info("REQUEST HEADERS: %s", request.headers)
    if 'Authorization' not in request.headers:
        logger.warning("Authorized token not found in request: %s", request.headers['Authorization'])

    if request.method == "GET":
        logger.info("REQUEST PARAMS: %s", request.args)
    elif request.method == "POST":
        logger.info("REQUEST PARAMS: %s", request.data)
        logger.info("REQUESTED FILES: %s", request.files)


@app.after_request
def after_request(response):

    header = response.headers
    header['Access-Control-Allow-Origin'] = os.getenv(
        'ALLOWED_ORIGIN_HOST_PROD')
    header['Access-Control-Allow-Headers'] = '*'
    header['Access-Control-Allow-Methods'] = '*'
    header['Access-Control-Allow-Credentials'] = "true"

    logger.info("RESPONSE STATUS: %s", response.status)
    logger.info("RESPONSE HEADERS: %s", response.headers)
    logger.info("RESPONSE BODY: ")
    logger.debug("RESPONSE CONTENT: %s", response.data)
    return response
