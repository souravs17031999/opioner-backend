from flask import Flask, json, jsonify, request, Response, Blueprint
from views.product import product
from werkzeug.datastructures import Headers
import jwt
from functools import wraps
import os
import requests

app = Flask(__name__)

app.register_blueprint(product, url_prefix='/product')

oidc_config = json.loads(os.getenv("OIDC_CONFIG"))
app.config['SERVER_URL'] = oidc_config["server_url"]
app.config['TOKEN_ISSUER'] = oidc_config["issuer"]
app.config['AUDIENCE_CLAIM'] = oidc_config["audience"]

SIGNATURE_EXPIRED = "SIGNATURE_EXPIRED"
INVALID_ISSUER = "INVALID_ISSUER"
INVALID_TOKEN = "INVALID_TOKEN"
INVALID_AUDIENCE = "INVALID_AUDIENCE"
PUBLIC_KEY_SERVER_ERROR = "PUBLIC_KEY_SERVER_ERROR"
SIGNATURE_VERIFICATION_FAILED = "SIGNATURE_VERIFICATION_FAILED"

@app.before_request
def before_request_func():
    print("\n***********************************************")
    print("REQUEST METHOD: ", request.method)
    print("REQUEST HEADERS: ", request.headers)
        
    if request.method == "GET":
        print("REQUEST PARAMS: ", request.args)
    elif request.method == "POST":
        print("REQUEST PARAMS: ", request.data)
        print("REQUESTED FILES: ", request.files)

    return authorize_request(request.headers)


@app.after_request
def after_request(response):

    header = response.headers
    header['Access-Control-Allow-Origin'] = os.getenv(
        'ALLOWED_ORIGIN_HOST_PROD')
    header['Access-Control-Allow-Headers'] = '*'
    header['Access-Control-Allow-Methods'] = '*'
    header['Access-Control-Allow-Credentials'] = "true"

    print("RESPONSE STATUS: ", response.status)
    print("RESPONSE HEADERS: ", response.headers)
    print("RESPONSE BODY: ")
    print(response.data, "\n")
    return response


def authorize_request(headers):

    if 'Authorization' not in headers:
        print("Authorized token not found in request")
        return jsonify({"error": "Bearer token not found in Authorization Header"}), 401
    
    split_token = headers['Authorization'].split(" ")
    payload = None
    if split_token[0] == "Bearer":
        payload = decode_auth_token(split_token[1])
    else:
        print("[Error]: Token not in valid format")
        return jsonify({"error": "Invalid token format"}), 401
    
    if payload == SIGNATURE_EXPIRED or payload == INVALID_ISSUER or payload == INVALID_AUDIENCE or payload == INVALID_TOKEN or payload == PUBLIC_KEY_SERVER_ERROR or payload == SIGNATURE_VERIFICATION_FAILED:
        return jsonify({
            "error": payload
            }), 401
    
    print("Request is Authorized")

def decode_auth_token(auth_token):
    """
    Decodes the auth token
    :param auth_token:
    :return: string
    """
    try:
        public_key = get_public_key_server()
        if public_key is None:
            return PUBLIC_KEY_SERVER_ERROR

        secret_key = '-----BEGIN PUBLIC KEY-----\n' + public_key + '\n-----END PUBLIC KEY-----'
        payload = jwt.decode(auth_token, secret_key, audience=app.config.get('AUDIENCE_CLAIM'), issuer=app.config.get('TOKEN_ISSUER'), algorithms='RS256')
        return payload
    except jwt.ExpiredSignatureError:
        print('Signature expired. Please log in again.')
        return SIGNATURE_EXPIRED
    except jwt.InvalidIssuerError:
        print('Invalid Issuer found. Please log in again.')
        return INVALID_ISSUER
    except jwt.InvalidAudienceError:
        print('Invalid Audience found. Please log in again.')
        return INVALID_AUDIENCE
    except jwt.InvalidSignatureError:
        print('Signature verification failed. Please log in again.')
        return SIGNATURE_VERIFICATION_FAILED
    except jwt.InvalidTokenError:
        print('Invalid token. Please log in again.')
        return INVALID_TOKEN

def get_public_key_server():
    try:
        authorization_server_response = requests.get(
                app.config.get("SERVER_URL"),
                timeout=60,
            )
        if authorization_server_response.status_code != 200:
            print("Error in fetching public key from server")
            return None

        return authorization_server_response.json()["public_key"]
    except Exception as e:
        print(e) 
        return None