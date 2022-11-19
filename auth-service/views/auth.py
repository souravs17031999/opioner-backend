from urllib import response
from flask import Flask, json, jsonify, request, Response, Blueprint, render_template
from werkzeug.datastructures import Headers

# from flaskext.mysql import MySQL
import jwt
import datetime
from functools import wraps
import os
import uuid
import bcrypt
import psycopg2
import redis
import secrets
import string
import requests
import json
import subprocess
from utils.log_util import get_logger

app = Flask(__name__)

# mysql = MySQL()
# app.config['MYSQL_DATABASE_USER'] = os.getenv('MYSQL_DATABASE_USER')
# app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('MYSQL_DATABASE_PASSWORD')
# app.config['MYSQL_DATABASE_DB'] = os.getenv('MYSQL_DATABASE_DB')
# app.config['MYSQL_DATABASE_HOST'] = os.getenv('MYSQL_DATABASE_HOST')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# mysql.init_app(app)

auth = Blueprint("auth", __name__)
logger = get_logger(__name__)

DATABASE_URL = f"postgres://{os.getenv('PGUSER')}:{os.getenv('PGPASSWORD')}@{os.getenv('PGHOST')}/{os.getenv('PGDATABASE')}"
if os.getenv("DATABASE_URL") != "":
    DATABASE_URL = os.getenv("DATABASE_URL")

logger.info("======= Connecting to Database...")
conn = psycopg2.connect(DATABASE_URL)
logger.info(conn)
REDIS_URL = f"redis://{os.getenv('REDIS_USERNAME')}:{os.getenv('REDIS_PASSWORD')}@{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}/{os.getenv('REDIS_DB')}"
if os.getenv("REDIS_URL") != "":
    REDIS_URL = os.getenv("REDIS_URL")

logger.info("======= Connecting to Redis.... %s", REDIS_URL)
redisServer = redis.Redis.from_url(REDIS_URL)

logger.info(redisServer)
NOTIFICATION_INTERNAL_API = os.getenv("NOTIFICATION_INTERNAL_URL")
REDIS_CACHE_TIMEOUT = 60
OTP_DIGITS = 6

def encode_auth_token(user_id):
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=1800),
            'iat': datetime.datetime.utcnow(),
            'sub': {"user-id": user_id, "roles": ["admin"]}
        }
        return jwt.encode(
            payload,
            app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        return e


def decode_auth_token(auth_token):
    """
    Decodes the auth token
    :param auth_token:
    :return: integer|string
    """
    try:
        payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'

def get_password_hash(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    logger.debug("hashedpwd: %s", hashed)
    return hashed.decode()

@auth.route("/open-id/connect/token", methods=["POST"])
def return_open_id_jwt_token():

    post_request = request.get_json(force=True)
    response = {}

    if post_request["user-id"] is None:
        logger.info("[ERROR]: Unauthorized access detected for authorized Page for user !")
        response["status"] = "failure"
        response["message"] = "Unauthorized access detected for authorized Page for user"
        return jsonify(response), 401

    try:
        logger.info("************ JWT TOKEN GENERATION ********* ")
        userJwtToken = encode_auth_token(post_request["user-id"])
    except Exception as e:
        logger.info("Error in generating JWT token for userid: %s", post_request["user-id"])
        logger.info("[ERROR]: ", e)
        response["status"] = "failure"
        response["message"] = "Error in generating JWT token for user!"
        return jsonify(response), 500
    
    response = {
        "status": "success",
        "message": "user authorized token generation successfull !",
        "token": userJwtToken
    }
    return jsonify(response), 200


@auth.route("/v2/generate/otp", methods=["POST"])
def generate_otp_for_user():

    post_request = request.get_json(force=True)
    key_for_redis = post_request["email"] + post_request["secret_token"]
    N = OTP_DIGITS
    randomValOTP = "".join(
        secrets.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase)
        for i in range(N)
    )

    try:
        payload = json.dumps(
            {
                "otp": randomValOTP,
            }
        )
        redisServer.set(key_for_redis, payload, REDIS_CACHE_TIMEOUT)
        logger.info(
            "generating OTP for key: ",
            key_for_redis,
            ", for email: ",
            post_request["email"],
        )
        logger.info("payload: ", payload)
        response = {}
        emailData = {}
        emailData[
            "subject"
        ] = f"Hi {post_request['firstname'].title()}, Please enter OTP and start your journey at Opioner"
        emailData["user_email"] = post_request["email"]
        emailData["otp"] = [x for x in randomValOTP]
        apiData = {
            "email_data": emailData,
            "service": "auth-service",
            "template_name": "generate_otp.html",
        }
        headers = {"Content-Type": "application/json"}
        try:
            notifyResponse = requests.post(
                NOTIFICATION_INTERNAL_API + "/notification/send/email",
                data=json.dumps(apiData),
                headers=headers,
                timeout=10,
            )
            logger.info("[debug]: notification-service response: %s", notifyResponse)
            if notifyResponse.status_code != 200:
                logger.info("Error in sending notification email for OTP")

                response["status"] = "failure"
                response["message"] = "Error in sending notification email for OTP"
                return jsonify(response), 500

        except Exception as e:
            logger.info("Error in sending notification email for OTP: ", e)
            response["status"] = "failure"
            response["message"] = "Error in sending notification email for OTP"
            return jsonify(response), 500

    except Exception as e:
        logger.info("Error in generating OTP for user: ", e)
        response["status"] = "failure"
        response["message"] = "Error in generating OTP for user"
        return jsonify(response), 500

    response["status"] = "success"
    response["message"] = "OTP sent to user email successfully !"
    return jsonify(response), 200


def verify_otp_for_user(userData, otp):

    key_for_redis = userData["email"] + userData["secret_token"]
    payload = redisServer.get(key_for_redis)
    logger.info("Got payload: ", payload, " for key: ", key_for_redis)
    if payload is not None and json.loads(payload)["otp"] == otp:
        return True
    else:
        return False


@auth.route("/status/live", methods=["GET", "POST"])
def liveness_check_auth_service():
    return jsonify({
        "status" : "success", 
        "message": "This is auth-service liveness probe, service is up and running !"
        }), 200

@auth.route("/status/health", methods=["GET", "POST"])
def health_check_auth_service():

    POSTGRES_SUCCESS, APP_SUCCESS, REDIS_SUCCESS = True, True, True
    components_check = [
        {"postgresDB": POSTGRES_SUCCESS},
        {"application": APP_SUCCESS}, 
        {"redis": REDIS_SUCCESS}
    ]
    try:
        subprocess_output = subprocess.run(["pg_isready", "-h", f"{os.getenv('PGHOST')}"])
        if subprocess_output.returncode != 0:
            POSTGRES_SUCCESS = False
    except Exception as e:
        logger.info(e)
    
    try:
        if redisServer.ping() != True:
            REDIS_SUCCESS = False
    except Exception as e:
        logger.info(e)

    return jsonify({
        "status" : "success", 
        "component_status": components_check
        }), 200

@auth.route("/login/user", methods=["POST"])
def login_to_app():
    post_request = request.get_json(force=True)
    affected_count = 0
    # conn = mysql.connect()
    cursor = conn.cursor()
    query = "SELECT * from users u WHERE u.username=%s"
    try:
        cursor.execute(query, (post_request["username"],))
        affected_count = cursor.rowcount
        db_data = cursor.fetchone()
    except Exception as e:
        logger.info(e)
    finally:
        if affected_count == 0:
            cursor.close()

    logger.info("----------------------------------------------------")
    logger.info(cursor.query.decode())
    logger.info(f"{affected_count} rows affected")
    logger.info("DB DATA : ", db_data)
    logger.info("----------------------------------------------------")
    response = {}

    if db_data == None:
        response["status"] = "failure"
        response["message"] = "No data for user found !"
        return jsonify(response), 401

    else:
        loggedInUserId = db_data[0]
        logger.info("****** PASSWORD AUTHENTICATION STARTED *******")
        if bcrypt.checkpw(post_request["password"].encode(), db_data[2].encode()):
            # auth user request
            # token = jwt.encode({'user': post_request["username"], 'exp': datetime.datetime.utcnow(
            # ) + datetime.timedelta(minutes=5)}, app.config['SECRET_KEY'])
            HOST = request.headers.get("Host")
            USER_AGENT = request.headers.get("User-Agent")
            ORIGIN = request.headers.get("Origin")
            LAST_LOGGED_IN = datetime.datetime.now()
            logger.info("******** Updating user session ********")
            userSessionUpdatequery = "UPDATE login_sessions SET host=%s, user_agent=%s, origin=%s, last_logged_in=%s, active_sessions = active_sessions + 1 WHERE user_id=%s"
            try:
                cursor.execute(
                    userSessionUpdatequery,
                    (
                        HOST,
                        USER_AGENT,
                        ORIGIN,
                        LAST_LOGGED_IN,
                        loggedInUserId,
                    ),
                )
                conn.commit()
                affected_count = cursor.rowcount
                logger.info("----------------------------------------------------")
                logger.info(cursor.query.decode())
                logger.info(f"{affected_count} rows affected")
                db_sessions_data = cursor.fetchone()
                logger.info("DB DATA : ", db_sessions_data)
                logger.info("----------------------------------------------------")
            except Exception as e:
                logger.info(e)
            finally:
                cursor.close()

            logger.info("************ JWT TOKEN APPENDING ********* ")
            userJwtToken = encode_auth_token(loggedInUserId)
            user_data = {
                "user_id": db_data[0],
                "username": db_data[1],
                "firstname": db_data[4],
                "token": userJwtToken
            }
            response["user_data"] = user_data
            response["status"] = "success"
            response["message"] = "User logged in succesfully !"
            # response["token"] = token.decode()
            return jsonify(response), 200
        else:
            response["status"] = "failure"
            response["message"] = "No data for user found !"
            return jsonify(response), 401


def signup_to_app(post_request):
    # post_request = request.get_json(force=True)

    # conn = mysql.connect()
    cursor = conn.cursor()

    authSelectQuery = "SELECT * FROM users WHERE username = %s"
    affected_count = 0
    try:
        cursor.execute(authSelectQuery, (post_request["username"],))
        logger.info("----------------------------------------------------")
        affected_count = cursor.rowcount
        logger.info(cursor.query.decode())
        logger.info(f"{cursor.rowcount} rows affected")
    except Exception as e:
        logger.info("ERROR in fetching user data", e)
    finally:
        if affected_count != 0:
            cursor.close()

    if affected_count != 0:
        logger.info("FAILURE")
        logger.info("Chosen username already exists !")
        return False, "Chosen username already exists !"

    createdUserId = None
    hashed_password = get_password_hash(post_request["password"])
    insertQuery = "INSERT INTO users(username, password, firstname, lastname, email) VALUES(%s, %s, %s, %s, %s)"
    try:
        cursor.execute(
            insertQuery,
            (
                post_request["username"],
                hashed_password,
                post_request["firstname"],
                post_request["lastname"],
                post_request["email"],
            ),
        )
        conn.commit()
        affected_count = cursor.rowcount
        logger.info(cursor.query.decode())
        logger.info(f"{cursor.rowcount} rows affected")
    except Exception as e:
        logger.info("ERROR in inserting users: ", e)
        return False, "ERROR: ERROR in user creation"
    finally:
        selectQuery = "SELECT u.user_id FROM users u WHERE username = %s"
        cursor.execute(selectQuery, (post_request["username"],))
        logger.info(cursor.query.decode())
        logger.info(f"{cursor.rowcount} rows affected")
        db_data = cursor.fetchone()
        createdUserId = db_data[0]
        logger.info("DB DATA : ", db_data)

    logger.info("----------------------------------------------------")

    insertUserSessionsQuery = "INSERT INTO login_sessions(user_id, host, user_agent, origin, active_sessions, last_logged_in) VALUES(%s, %s, %s, %s, %s, %s)"
    HOST = request.headers.get("Host")
    USER_AGENT = request.headers.get("User-Agent")
    ORIGIN = request.headers.get("Origin")
    LAST_LOGGED_IN = datetime.datetime.now()

    try:
        cursor.execute(
            insertUserSessionsQuery,
            (
                createdUserId,
                HOST,
                USER_AGENT,
                ORIGIN,
                1,
                LAST_LOGGED_IN,
            ),
        )
        conn.commit()
        affected_count = cursor.rowcount
        logger.info("----------------------------------------------------")
        logger.info(cursor.query.decode())
        logger.info(f"{cursor.rowcount} rows affected")
        logger.info("----------------------------------------------------")
    except Exception as e:
        logger.error("ERROR in inserting user login sessions: %s", e)
        return False, "ERROR: ERROR in user creation"

    insertNotificationQuery = "INSERT INTO user_notifications(event_type, description, user_id) VALUES(%s, %s, %s)"

    try:
        cursor.execute(
            insertNotificationQuery,
            (
                "update_event",
                "Welcome to Opioner ! Share your first post now, it's just a click away",
                db_data[0],
            ),
        )
        conn.commit()
        affected_count = cursor.rowcount
        logger.info(cursor.query.decode())
        logger.info(f"{cursor.rowcount} rows affected")
    except Exception as e:
        logger.error("ERROR in inserting user notifications: ", e)
        return False, "ERROR: ERROR in user creation"
    finally:
        cursor.close()

    logger.info("----------------------------------------------------")
    user_data = {"user_id": createdUserId}
    if affected_count == 0:
        return False, user_data
    else:
        logger.info("************ JWT TOKEN APPENDING ********* ")
        userJwtToken = encode_auth_token(createdUserId)
        user_data["token"] = userJwtToken
        return True, user_data


@auth.route("/password/user", methods=["PUT"])
def update_password_user():
    post_request = request.get_json(force=True)

    # conn = mysql.connect()
    cursor = conn.cursor()
    select_query = "SELECT * FROM users WHERE username = %s"

    affected_count = 0
    try:
        cursor.execute(select_query, (post_request["username"],))
        affected_count = cursor.rowcount
        logger.info("----------------------------------------------------")
        logger.info(cursor.query.decode())
        logger.info(f"{affected_count} rows affected")
        db_data = cursor.fetchone()
        logger.info("DB DATA : %s", db_data)

    except Exception as e:
        logger.info(e)
    finally:
        if affected_count == 0:
            cursor.close()

    response = {}
    if affected_count == 0:
        response["status"] = "failure"
        response["message"] = "Unauthorized request, cannot update password for user !"
        return jsonify(response), 401

    user_data = {
        "email": post_request["email"],
        "secret_token": post_request["secret_token"],
    }

    if not verify_otp_for_user(user_data, post_request["otp"]):
        logger.info("[ERROR]: OTP verification failed for user: %s", post_request["email"])
        response["status"] = "failure"
        response["message"] = "OTP verification failed !"
        return jsonify(response), 403

    hashed_password = get_password_hash(post_request["password"])

    update_query = "UPDATE users SET password = %s WHERE username = %s"
    try:
        cursor.execute(
            update_query,
            (
                hashed_password,
                post_request["username"],
            ),
        )
        conn.commit()
        affected_count = cursor.rowcount
        logger.info(cursor.query.decode())
        logger.info(f"{affected_count} rows affected")
        db_data = cursor.fetchone()
        logger.info("DB DATA : %s", db_data)

    except Exception as e:
        logger.info(e)
    finally:
        cursor.close()

    logger.info("----------------------------------------------------")

    if affected_count == 0:
        response["status"] = "failure"
        response["message"] = "Error updating password for user !"
        return jsonify(response), 500
    else:
        response["status"] = "success"
        response["message"] = "Password updated for user successfully !"
        return jsonify(response), 200


@auth.route("/logout/user", methods=["POST"])
def logout_from_app():
    post_request = request.get_json(force=True)
    affected_count = 0
    # conn = mysql.connect()
    cursor = conn.cursor()
    username = post_request["username"]
    user_id = post_request["user_id"]
    query = "SELECT * from users u WHERE u.username=%s AND u.user_id=%s"
    try:
        cursor.execute(
            query,
            (
                username,
                user_id,
            ),
        )
        affected_count = cursor.rowcount
        db_data = cursor.fetchone()
    except Exception as e:
        logger.info(e)
    finally:
        if affected_count == 0:
            cursor.close()

    logger.info("----------------------------------------------------")
    logger.info(cursor.query.decode())
    logger.info(f"{affected_count} rows affected")
    logger.info("DB DATA : %s", db_data)
    logger.info("----------------------------------------------------")
    response = {}

    if db_data == None:
        response["status"] = "failure"
        response["message"] = "No data for user found !"
        return jsonify(response), 403

    else:
        loggedInUserId = db_data[0]
        HOST = request.headers.get("Host")
        USER_AGENT = request.headers.get("User-Agent")
        ORIGIN = request.headers.get("Origin")
        LAST_LOGGED_OUT = datetime.datetime.now()
        logger.info("******** Logging out user now ********")
        userSessionUpdatequery = "UPDATE login_sessions SET host=%s, user_agent=%s, origin=%s, last_logged_out=%s, active_sessions = active_sessions - 1 WHERE user_id=%s"
        try:
            cursor.execute(
                userSessionUpdatequery,
                (
                    HOST,
                    USER_AGENT,
                    ORIGIN,
                    LAST_LOGGED_OUT,
                    loggedInUserId,
                ),
            )
            conn.commit()
            affected_count = cursor.rowcount
            logger.info("----------------------------------------------------")
            logger.info(cursor.query.decode())
            logger.info(f"{affected_count} rows affected")
            logger.info("----------------------------------------------------")
        except Exception as e:
            logger.info(e)
        finally:
            cursor.close()

    if affected_count == 0:
        response["status"] = "failure"
        response["message"] = "User couldn't be logged out !"
        return jsonify(response), 500
    else:
        response["status"] = "success"
        response["message"] = "User logged out successfully !"
        return jsonify(response), 204


@auth.route("/generate/otp", methods=["POST"])
def generate_OTP_signup():

    post_request = request.get_json(force=True)

    cursor = conn.cursor()
    authSelectQuery = "SELECT * FROM users WHERE email = %s"
    affected_count = 0
    try:
        cursor.execute(authSelectQuery, (post_request["email"],))
        affected_count = cursor.rowcount
        logger.info("----------------------------------------------------")
        logger.info(cursor.query.decode())
        logger.info(f"{affected_count} rows affected")
    except Exception as e:
        logger.info(e)

    response = {}
    if affected_count != 0:
        response["status"] = "failure"
        response[
            "message"
        ] = "User already registered with this email ! Try logging in or click on forgot password."
        return jsonify(response), 403

    usernameSelectQuery = "SELECT * FROM users WHERE username = %s"
    try:
        cursor.execute(usernameSelectQuery, (post_request["username"],))
        affected_count = cursor.rowcount
        logger.info(cursor.query.decode())
        logger.info(f"{affected_count} rows affected")
    except Exception as e:
        logger.info(e)
    finally:
        cursor.close()

    logger.info("----------------------------------------------------")
    if affected_count != 0:
        response["status"] = "failure"
        response[
            "message"
        ] = "Chosen username already exists ! Try again with different username."
        return jsonify(response), 403

    

    key_for_redis = post_request["email"] + post_request["secret_token"]
    N = OTP_DIGITS
    randomValOTP = "".join(
        secrets.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase)
        for i in range(N)
    )

    errorFlagOTP = False
    errorFlagEmail = False
    try:
        payload = json.dumps(
            {
                "firstname": post_request["firstname"],
                "lastname": post_request["lastname"],
                "username": post_request["username"],
                "password": post_request["password"],
                "email": post_request["email"],
                "otp": randomValOTP,
            }
        )
        redisServer.set(key_for_redis, payload, REDIS_CACHE_TIMEOUT)
        logger.info(
            "generating OTP for key: %s",
            key_for_redis,
            ", for email: %s",
            post_request["email"],
        )
        logger.info("payload: %s", payload)
    except Exception as e:
        logger.error("Error: %s", e)
        errorFlagOTP = True

    emailData = {}
    emailData[
        "subject"
    ] = f"Hi {post_request['firstname'].title()}, Please enter OTP and start your journey at Opioner"
    emailData["user_email"] = post_request["email"]
    emailData["otp"] = [x for x in randomValOTP]
    apiData = {
        "email_data": emailData,
        "service": "auth-service",
        "template_name": "generate_otp.html",
    }
    headers = {"Content-Type": "application/json"}
    try:
        logger.info(
            "[debug] Requesting to Notification service API: %s",
            NOTIFICATION_INTERNAL_API + "/notification/send/email",
        )
        logger.info("[debug] request body: ", apiData)
        notifyResponse = requests.post(
            NOTIFICATION_INTERNAL_API + "/notification/send/email",
            data=json.dumps(apiData),
            headers=headers,
            timeout=10,
        )
        logger.info("[debug] notification-service status: %s", notifyResponse)
        logger.info("[debug] notification-service response: %s", notifyResponse.text)
        if notifyResponse.status_code != 200:
            errorFlagEmail = True
        logger.info("============================")

    except Exception as e:
        logger.info(e)
        errorFlagEmail = True

    if errorFlagEmail:
        response = {"status": "failure", "message": "OTP Notification email failed !"}
        return jsonify(response), 500
    elif errorFlagOTP:
        response = {"status": "failure", "message": "OTP generation failed !"}
        return jsonify(response), 500
    else:
        response = {
            "email": post_request["email"],
            "secret_token": post_request["secret_token"],
            "status": "success",
            "message": "OTP sent to user email !",
        }
        return jsonify(response), 200


@auth.route("/verify/otp", methods=["POST"])
def verify_OTP_signup():

    post_request = request.get_json(force=True)
    userOTP = post_request["otp"]
    key_for_redis = post_request["email"] + post_request["secret_token"]

    response = {}
    try:
        user_signup_payload = redisServer.get(key_for_redis)
        logger.info("Got payload: %s", user_signup_payload, " for key: ", key_for_redis)
        if (
            user_signup_payload is not None
            and json.loads(user_signup_payload)["otp"] == userOTP
        ):
            decoded_payload = json.loads(user_signup_payload)
            post_request = {
                "username": decoded_payload["username"],
                "password": decoded_payload["password"],
                "firstname": decoded_payload["firstname"],
                "lastname": decoded_payload["lastname"],
                "email": decoded_payload["email"],
            }
            userSignedUpProcess = signup_to_app(post_request)
            if userSignedUpProcess[0]:
                response["status"] = "success"
                response["verified_status"] = True
                response["user_data"] = userSignedUpProcess[1]
                response["message"] = "User signed up successfully !"
            else:
                response["status"] = "failure"
                response["verified_status"] = True
                response["message"] = userSignedUpProcess[1]

        else:
            response["status"] = "failure"
            response["verified_status"] = False
            response["message"] = "OTP verification failed !"

    except Exception as e:
        logger.error("ERROR: %s", e)
        response["status"] = "failure"
        response["verified_status"] = False
        response["message"] = "OTP verification failed !"

    if response["status"] == "success":
        return jsonify(response), 200
    else:
        return jsonify(response), 500


def login_to_app_via_social(post_request, user_data):

    cursor = conn.cursor()
    HOST = request.headers.get("Host")
    USER_AGENT = request.headers.get("User-Agent")
    ORIGIN = request.headers.get("Origin")
    LAST_LOGGED_IN = datetime.datetime.now()
    loggedInUserId = user_data[0]
    logger.info("******** Updating user session ********")
    userSessionUpdatequery = "UPDATE login_sessions SET host=%s, user_agent=%s, origin=%s, last_logged_in=%s, active_sessions = active_sessions + 1 WHERE user_id=%s"
    try:
        cursor.execute(
            userSessionUpdatequery,
            (
                HOST,
                USER_AGENT,
                ORIGIN,
                LAST_LOGGED_IN,
                loggedInUserId,
            ),
        )
        conn.commit()
        affected_count = cursor.rowcount
        logger.info("----------------------------------------------------")
        logger.info(cursor.query.decode())
        logger.info(f"{affected_count} rows affected")
        logger.info("----------------------------------------------------")
    except Exception as e:
        logger.info(
            f"Error logging in user via {post_request['action_event_source']} signin: ",
            e,
        )
        return (
            False,
            f"Error logging in user via {post_request['action_event_source']} signin:",
        )
    finally:
        cursor.close()
    
    logger.info("************ JWT TOKEN APPENDING ********* ")
    userJwtToken = encode_auth_token(loggedInUserId)
    user_data = {
        "user_id": user_data[0],
        "username": user_data[1],
        "firstname": user_data[4],
        "token": userJwtToken
    }

    return True, user_data


def signup_to_app_via_social(post_request):

    cursor = conn.cursor()

    createdUserId = None
    affected_count = 0

    if post_request["action_event_source"] == "google":

        insertQuery = "INSERT INTO users(username, firstname, lastname, email, google_profile_url, is_google_verified, google_token_id) VALUES(%s, %s, %s, %s, %s, %s)"
        try:
            cursor.execute(
                insertQuery,
                (
                    post_request["username"],
                    post_request["firstname"],
                    post_request["lastname"],
                    post_request["email"],
                    post_request["google_profile_url"],
                    1,
                    post_request["google_token_id"],
                ),
            )
            conn.commit()
            affected_count = cursor.rowcount
            logger.info(cursor.query.decode())
            logger.info(f"{cursor.rowcount} rows affected")
        except Exception as e:
            logger.error("ERROR in inserting users for google signin: %s", e)
            return False, "ERROR: ERROR in user creation for google signin user"

    elif post_request["action_event_source"] == "facebook":

        insertQuery = "INSERT INTO users(username, firstname, lastname, email, facebook_profile_url, is_facebook_verified, facebook_token_id, facebook_user_id, gender) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
        try:
            cursor.execute(
                insertQuery,
                (
                    post_request["username"],
                    post_request["firstname"],
                    post_request["lastname"],
                    post_request["email"],
                    post_request["facebook_profile_url"],
                    1,
                    post_request["facebook_token_id"],
                    post_request["facebook_user_id"],
                    post_request["gender"],
                ),
            )
            conn.commit()
            affected_count = cursor.rowcount
            logger.info(cursor.query.decode())
            logger.info(f"{cursor.rowcount} rows affected")
        except Exception as e:
            logger.error("ERROR in inserting users for facebook signin: %s", e)
            return False, "ERROR: ERROR in user creation for facebook signin user"

    selectQuery = "SELECT u.user_id FROM users u WHERE email = %s"
    cursor.execute(selectQuery, (post_request["email"],))
    logger.info(cursor.query.decode())
    logger.info(f"{cursor.rowcount} rows affected")
    db_data = cursor.fetchone()
    createdUserId = db_data[0]
    logger.info("DB DATA : %s", db_data)

    logger.info("----------------------------------------------------")

    insertUserSessionsQuery = "INSERT INTO login_sessions(user_id, host, user_agent, origin, active_sessions, last_logged_in) VALUES(%s, %s, %s, %s, %s, %s)"
    HOST = request.headers.get("Host")
    USER_AGENT = request.headers.get("User-Agent")
    ORIGIN = request.headers.get("Origin")
    LAST_LOGGED_IN = datetime.datetime.now()

    try:
        cursor.execute(
            insertUserSessionsQuery,
            (
                createdUserId,
                HOST,
                USER_AGENT,
                ORIGIN,
                1,
                LAST_LOGGED_IN,
            ),
        )
        conn.commit()
        affected_count = cursor.rowcount
        logger.info("----------------------------------------------------")
        logger.info(cursor.query.decode())
        logger.info(f"{cursor.rowcount} rows affected")
        logger.info("----------------------------------------------------")
    except Exception as e:
        logger.error("ERROR in inserting user login sessions: %s", e)
        return False, "ERROR: ERROR in user creation"

    insertNotificationQuery = "INSERT INTO user_notifications(event_type, description, user_id) VALUES(%s, %s, %s)"

    try:
        cursor.execute(
            insertNotificationQuery,
            (
                "update_event",
                "Welcome to Opioner ! Share your first post now, it's just a click away",
                db_data[0],
            ),
        )
        conn.commit()
        affected_count = cursor.rowcount
        logger.info(cursor.query.decode())
        logger.info(f"{cursor.rowcount} rows affected")
    except Exception as e:
        logger.error("ERROR in inserting user notifications: %s", e)
        return False, "ERROR: ERROR in user creation"
    finally:
        cursor.close()

    logger.info("----------------------------------------------------")
    logger.info("************ JWT TOKEN APPENDING ********* ")
    userJwtToken = encode_auth_token(createdUserId)
    user_data = {"user_id": createdUserId, "token": userJwtToken}
    if affected_count == 0:
        return False, user_data
    else:
        return True, user_data


@auth.route("/verify/social/sign", methods=["POST"])
def verify_social_sign_up():

    post_request = request.get_json(force=True)
    response = {}

    cursor = conn.cursor()

    authSelectQuery = "SELECT * FROM users WHERE email = %s"
    affected_count = 0
    user_data = None

    if post_request.get("email") is None:
        logger.info("[Warning]: Email not found in request API")
        response["status"] = "failure"
        response["verified_status"] = False
        response["message"] = "Email not found in request API"
        return jsonify(response), 403

    try:
        cursor.execute(authSelectQuery, (post_request["email"],))
        logger.info("----------------------------------------------------")
        affected_count = cursor.rowcount
        user_data = cursor.fetchone()
        logger.info(cursor.query.decode())
        logger.info(f"{cursor.rowcount} rows affected")
    except Exception as e:
        logger.error("ERROR in fetching user data: %s", e)
        response["status"] = "failure"
        response["verified_status"] = False
        response[
            "message"
        ] = "ERROR in fetching user data while verifying/signing up social media user"
        return jsonify(response), 500
    finally:
        cursor.close()

    post_request_for_social = None

    if post_request.get("action_event_source") == "google":

        post_request_for_social = {
            "action_event_source": "google",
            "username": post_request["email"],
            "firstname": post_request["firstname"],
            "lastname": post_request["lastname"],
            "email": post_request["email"],
            "google_profile_url": post_request["google_profile_url"],
            "google_token_id": post_request["google_token_id"],
        }
    elif post_request.get("action_event_source") == "facebook":
        post_request_for_social = {
            "action_event_source": "facebook",
            "name": post_request["name"],
            "username": post_request["email"],
            "firstname": post_request["firstname"],
            "lastname": post_request["lastname"],
            "email": post_request["email"],
            "facebook_profile_url": post_request["facebook_profile_url"],
            "facebook_token_id": post_request["facebook_token_id"],
            "facebook_user_id": post_request["facebook_user_id"],
            "gender": post_request["gender"],
        }

    userResponse = None
    action = None

    if affected_count == 1:
        is_google_verified = True if user_data[11] else False
        is_facebook_verified = True if user_data[14] else False
        if (is_google_verified and post_request["action_event_source"] == "google") or (
            is_facebook_verified and post_request["action_event_source"] == "facebook"
        ):
            logger.info("[debug]: User already found, logging in user ....")
            userResponse = login_to_app_via_social(post_request_for_social, user_data)
            action = "LOGIN"
    elif affected_count == 0:
        logger.info("[debug]: User not found, signing up the user ....")
        userResponse = signup_to_app_via_social(post_request_for_social)
        action = "SIGNUP"

    if userResponse is not None and userResponse[0]:
        response["status"] = "success"
        response["verified_status"] = True
        response["user_data"] = userResponse[1]
        response["message"] = "User loggedin/signed up successfully !"
        if action == "LOGIN":
            response["is_new_user"] = False
        elif action == "SIGNUP":
            response["is_new_user"] = True

        return jsonify(response), 200
    else:
        response["status"] = "failure"
        response["verified_status"] = False
        response["message"] = userResponse[1]
        if action == "LOGIN":
            response["is_new_user"] = False
        elif action == "SIGNUP":
            response["is_new_user"] = True
        return jsonify(response), 500
