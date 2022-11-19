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
    logger.info("REQUEST METHOD: ", request.method)
    logger.info("REQUEST HEADERS: ", request.headers)
    if 'Authorization' in request.headers:
        logger.warning("Authorized token found in request: ", request.headers['Authorization'])

    if request.method == "GET":
        logger.info("REQUEST PARAMS: ", request.args)
    elif request.method == "POST":
        logger.info("REQUEST PARAMS: ", request.data)
        logger.info("REQUESTED FILES: ", request.files)


@app.after_request
def after_request(response):

    header = response.headers
    header['Access-Control-Allow-Origin'] = os.getenv(
        'ALLOWED_ORIGIN_HOST_PROD')
    header['Access-Control-Allow-Headers'] = '*'
    header['Access-Control-Allow-Methods'] = '*'
    header['Access-Control-Allow-Credentials'] = "true"

    logger.info("RESPONSE STATUS: ", response.status)
    logger.info("RESPONSE HEADERS: ", response.headers)
    logger.info("RESPONSE BODY: ")
    logger.debug(response.data)
    return response
