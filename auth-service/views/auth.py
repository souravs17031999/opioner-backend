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

app = Flask(__name__)

# mysql = MySQL()
# app.config['MYSQL_DATABASE_USER'] = os.getenv('MYSQL_DATABASE_USER')
# app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('MYSQL_DATABASE_PASSWORD')
# app.config['MYSQL_DATABASE_DB'] = os.getenv('MYSQL_DATABASE_DB')
# app.config['MYSQL_DATABASE_HOST'] = os.getenv('MYSQL_DATABASE_HOST')
# app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


# mysql.init_app(app)

auth = Blueprint("auth", __name__)
DATABASE_URL = f"postgres://{os.getenv('PGUSER')}:{os.getenv('PGPASSWORD')}@{os.getenv('PGHOST')}/{os.getenv('PGDATABASE')}"
if os.getenv("DATABASE_URL") != "":
    DATABASE_URL = os.getenv("DATABASE_URL")

print("======= Connecting to Database...")
conn = psycopg2.connect(DATABASE_URL)
print(conn)
REDIS_URL = f"redis://{os.getenv('REDIS_USERNAME')}:{os.getenv('REDIS_PASSWORD')}@{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}/{os.getenv('REDIS_DB')}"
if os.getenv("REDIS_URL") != "":
    REDIS_URL = os.getenv("REDIS_URL")

print("======= Connecting to Redis....", REDIS_URL)
redisServer = redis.Redis.from_url(REDIS_URL)

print(redisServer)
NOTIFICATION_INTERNAL_API = os.getenv("NOTIFICATION_INTERNAL_URL")
REDIS_CACHE_TIMEOUT = 60
OTP_DIGITS = 6


def get_password_hash(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    print("hashedpwd:", hashed)
    return hashed.decode()


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
        print(
            "generating OTP for key: ",
            key_for_redis,
            ", for email: ",
            post_request["email"],
        )
        print("payload: ", payload)
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
            print("[debug]: notification-service response: ", notifyResponse)
            if notifyResponse.status_code != 200:
                print("Error in sending notification email for OTP")

                response["status"] = "failure"
                response["message"] = "Error in sending notification email for OTP"
                return jsonify(response), 500

        except Exception as e:
            print("Error in sending notification email for OTP: ", e)
            response["status"] = "failure"
            response["message"] = "Error in sending notification email for OTP"
            return jsonify(response), 500

    except Exception as e:
        print("Error in generating OTP for user: ", e)
        response["status"] = "failure"
        response["message"] = "Error in generating OTP for user"
        return jsonify(response), 500

    response["status"] = "success"
    response["message"] = "OTP sent to user email successfully !"
    return jsonify(response), 200


def verify_otp_for_user(userData, otp):

    key_for_redis = userData["email"] + userData["secret_token"]
    payload = redisServer.get(key_for_redis)
    print("Got payload: ", payload, " for key: ", key_for_redis)
    if payload is not None and json.loads(payload)["otp"] == otp:
        return True
    else:
        return False


@auth.route("/test", methods=["GET", "POST"])
def test_auth_service():
    return "<h1> This is auth service testing, service is up and running !</h1>"


@auth.route("/login-user", methods=["POST"])
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
        print(e)
    finally:
        if affected_count == 0:
            cursor.close()

    print("----------------------------------------------------")
    print(cursor.query.decode())
    print(f"{affected_count} rows affected")
    print("DB DATA : ", db_data)
    print("----------------------------------------------------")
    response = {}

    if db_data == None:
        response["status"] = "failure"
        response["message"] = "No data for user found !"
        return jsonify(response), 401

    else:
        loggedInUserId = db_data[0]
        print("****** PASSWORD AUTHENTICATION STARTED *******")
        if bcrypt.checkpw(post_request["password"].encode(), db_data[2].encode()):
            # auth user request
            # token = jwt.encode({'user': post_request["username"], 'exp': datetime.datetime.utcnow(
            # ) + datetime.timedelta(minutes=5)}, app.config['SECRET_KEY'])
            HOST = request.headers.get("Host")
            USER_AGENT = request.headers.get("User-Agent")
            ORIGIN = request.headers.get("Origin")
            LAST_LOGGED_IN = datetime.datetime.now()
            print("******** Updating user session ********")
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
                print("----------------------------------------------------")
                print(cursor.query.decode())
                print(f"{affected_count} rows affected")
                db_sessions_data = cursor.fetchone()
                print("DB DATA : ", db_sessions_data)
                print("----------------------------------------------------")
            except Exception as e:
                print(e)
            finally:
                cursor.close()

            user_data = {
                "user_id": db_data[0],
                "username": db_data[1],
                "firstname": db_data[4],
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
        print("----------------------------------------------------")
        affected_count = cursor.rowcount
        print(cursor.query.decode())
        print(f"{cursor.rowcount} rows affected")
    except Exception as e:
        print("ERROR in fetching user data", e)
    finally:
        if affected_count != 0:
            cursor.close()

    if affected_count != 0:
        print("FAILURE")
        print("Chosen username already exists !")
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
        print(cursor.query.decode())
        print(f"{cursor.rowcount} rows affected")
    except Exception as e:
        print("ERROR in inserting users: ", e)
        return False, "ERROR: ERROR in user creation"
    finally:
        selectQuery = "SELECT u.user_id FROM users u WHERE username = %s"
        cursor.execute(selectQuery, (post_request["username"],))
        print(cursor.query.decode())
        print(f"{cursor.rowcount} rows affected")
        db_data = cursor.fetchone()
        createdUserId = db_data[0]
        print("DB DATA : ", db_data)

    print("----------------------------------------------------")

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
        print("----------------------------------------------------")
        print(cursor.query.decode())
        print(f"{cursor.rowcount} rows affected")
        print("----------------------------------------------------")
    except Exception as e:
        print("ERROR in inserting user login sessions: ", e)
        return False, "ERROR: ERROR in user creation"

    insertNotificationQuery = "INSERT INTO user_notifications(event_type, description, user_id) VALUES(%s, %s, %s)"

    try:
        cursor.execute(
            insertNotificationQuery,
            (
                "update_event",
                "Welcome to taskly ! Create your first task now, it’s just a click away",
                db_data[0],
            ),
        )
        conn.commit()
        affected_count = cursor.rowcount
        print(cursor.query.decode())
        print(f"{cursor.rowcount} rows affected")
    except Exception as e:
        print("ERROR in inserting user notifications: ", e)
        return False, "ERROR: ERROR in user creation"
    finally:
        cursor.close()

    print("----------------------------------------------------")
    user_data = {"user_id": createdUserId}
    if affected_count == 0:
        return False, user_data
    else:
        return True, user_data


@auth.route("/update-password-user", methods=["POST"])
def update_password_user():
    post_request = request.get_json(force=True)

    # conn = mysql.connect()
    cursor = conn.cursor()
    select_query = "SELECT * FROM users WHERE username = %s"

    affected_count = 0
    try:
        cursor.execute(select_query, (post_request["username"],))
        affected_count = cursor.rowcount
        print("----------------------------------------------------")
        print(cursor.query.decode())
        print(f"{affected_count} rows affected")
        db_data = cursor.fetchone()
        print("DB DATA : ", db_data)

    except Exception as e:
        print(e)
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
        print("[ERROR]: OTP verification failed for user: ", post_request["email"])
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
        print(cursor.query.decode())
        print(f"{affected_count} rows affected")
        db_data = cursor.fetchone()
        print("DB DATA : ", db_data)

    except Exception as e:
        print(e)
    finally:
        cursor.close()

    print("----------------------------------------------------")

    if affected_count == 0:
        response["status"] = "failure"
        response["message"] = "Error updating password for user !"
        return jsonify(response), 500
    else:
        response["status"] = "success"
        response["message"] = "Password updated for user successfully !"
        return jsonify(response), 200


@auth.route("/logout-user", methods=["POST"])
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
        print(e)
    finally:
        if affected_count == 0:
            cursor.close()

    print("----------------------------------------------------")
    print(cursor.query.decode())
    print(f"{affected_count} rows affected")
    print("DB DATA : ", db_data)
    print("----------------------------------------------------")
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
        print("******** Logging out user now ********")
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
            print("----------------------------------------------------")
            print(cursor.query.decode())
            print(f"{affected_count} rows affected")
            print("----------------------------------------------------")
        except Exception as e:
            print(e)
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
        print("----------------------------------------------------")
        print(cursor.query.decode())
        print(f"{affected_count} rows affected")
    except Exception as e:
        print(e)

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
        print(cursor.query.decode())
        print(f"{affected_count} rows affected")
    except Exception as e:
        print(e)

    print("----------------------------------------------------")
    if affected_count != 0:
        response["status"] = "failure"
        response[
            "message"
        ] = "Chosen username already exists ! Try again with different username."
        return jsonify(response), 403

    cursor.close()

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
        print(
            "generating OTP for key: ",
            key_for_redis,
            ", for email: ",
            post_request["email"],
        )
        print("payload: ", payload)
    except Exception as e:
        print("Error: ", e)
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
        print(
            "[debug] Requesting to Notification service API: ",
            NOTIFICATION_INTERNAL_API + "/notification/send/email",
        )
        print("[debug] request body: ", apiData)
        notifyResponse = requests.post(
            NOTIFICATION_INTERNAL_API + "/notification/send/email",
            data=json.dumps(apiData),
            headers=headers,
            timeout=10,
        )
        print("[debug] notification-service status: ", notifyResponse)
        print("[debug] notification-service response: ", notifyResponse.text)
        if notifyResponse.status_code != 200:
            errorFlagEmail = True
        print("============================")

    except Exception as e:
        print(e)
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
        print("Got payload: ", user_signup_payload, " for key: ", key_for_redis)
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
        print("ERROR: ", e)
        response["status"] = "failure"
        response["verified_status"] = False
        response["message"] = "OTP verification failed !"

    if response["status"] == "success":
        return jsonify(response), 200
    else:
        return jsonify(response), 500


def login_to_app_via_google(post_request, user_data):

    cursor = conn.cursor()
    HOST = request.headers.get("Host")
    USER_AGENT = request.headers.get("User-Agent")
    ORIGIN = request.headers.get("Origin")
    LAST_LOGGED_IN = datetime.datetime.now()
    loggedInUserId = user_data[0]
    print("******** Updating user session ********")
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
        print("----------------------------------------------------")
        print(cursor.query.decode())
        print(f"{affected_count} rows affected")
        print("----------------------------------------------------")
    except Exception as e:
        print("Error logging in user via Google signin: ", e)
        return False, "Error logging in user via Google signin"
    finally:
        cursor.close()

    user_data = {
        "user_id": user_data[0],
        "username": user_data[1],
        "firstname": user_data[4],
    }

    return True, user_data


def signup_to_app_via_google(post_request):

    cursor = conn.cursor()

    createdUserId = None
    insertQuery = "INSERT INTO users(username, firstname, email, google_profile_url, is_google_verified, google_token_id) VALUES(%s, %s, %s, %s, %s, %s)"
    try:
        cursor.execute(
            insertQuery,
            (
                post_request["username"],
                post_request["firstname"],
                post_request["email"],
                post_request["google_profile_url"],
                1,
                post_request["google_token_id"],
            ),
        )
        conn.commit()
        affected_count = cursor.rowcount
        print(cursor.query.decode())
        print(f"{cursor.rowcount} rows affected")
    except Exception as e:
        print("ERROR in inserting users: ", e)
        return False, "ERROR: ERROR in user creation"
    finally:
        selectQuery = "SELECT u.user_id FROM users u WHERE username = %s"
        cursor.execute(selectQuery, (post_request["username"],))
        print(cursor.query.decode())
        print(f"{cursor.rowcount} rows affected")
        db_data = cursor.fetchone()
        createdUserId = db_data[0]
        print("DB DATA : ", db_data)

    print("----------------------------------------------------")

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
        print("----------------------------------------------------")
        print(cursor.query.decode())
        print(f"{cursor.rowcount} rows affected")
        print("----------------------------------------------------")
    except Exception as e:
        print("ERROR in inserting user login sessions: ", e)
        return False, "ERROR: ERROR in user creation"

    insertNotificationQuery = "INSERT INTO user_notifications(event_type, description, user_id) VALUES(%s, %s, %s)"

    try:
        cursor.execute(
            insertNotificationQuery,
            (
                "update_event",
                "Welcome to taskly ! Create your first task now, it’s just a click away",
                db_data[0],
            ),
        )
        conn.commit()
        affected_count = cursor.rowcount
        print(cursor.query.decode())
        print(f"{cursor.rowcount} rows affected")
    except Exception as e:
        print("ERROR in inserting user notifications: ", e)
        return False, "ERROR: ERROR in user creation"
    finally:
        cursor.close()

    print("----------------------------------------------------")
    user_data = {"user_id": createdUserId}
    if affected_count == 0:
        return False, user_data
    else:
        return True, user_data


@auth.route("/verify/google/sign", methods=["POST"])
def verify_google_sign_up():

    post_request = request.get_json(force=True)
    response = {}

    cursor = conn.cursor()

    authSelectQuery = "SELECT * FROM users WHERE email = %s"
    affected_count = 0
    user_data = None
    try:
        cursor.execute(authSelectQuery, (post_request["email"],))
        print("----------------------------------------------------")
        affected_count = cursor.rowcount
        user_data = cursor.fetchone()
        print(cursor.query.decode())
        print(f"{cursor.rowcount} rows affected")
    except Exception as e:
        print("ERROR in fetching user data", e)
        response["status"] = "failure"
        response["verified_status"] = False
        response[
            "message"
        ] = "ERROR in fetching user data while verifying/signing up google user"
        return jsonify(response), 500
    finally:
        cursor.close()

    post_request = {
        "username": post_request["email"],
        "firstname": post_request["firstname"],
        "email": post_request["email"],
        "google_profile_url": post_request["google_profile_url"],
        "google_token_id": post_request["google_token_id"],
    }

    userResponse = None
    action = None
    if affected_count == 1:
        print("[debug]: User already found, logging in user ....")
        userResponse = login_to_app_via_google(post_request, user_data)
        action = "LOGIN"
    elif affected_count == 0:
        print("[debug]: User not found, signing up the user ....")
        userResponse = signup_to_app_via_google(post_request)
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
        return jsonify(response), 500
