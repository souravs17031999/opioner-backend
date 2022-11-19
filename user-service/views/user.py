from flask import Flask, json, jsonify, request, Response, Blueprint, g
from werkzeug.datastructures import Headers

# from flaskext.mysql import MySQL
import jwt
import datetime
from functools import wraps
import os
import uuid
import pyrebase
import psycopg2
import subprocess
import json
from utils.log_util import get_logger

app = Flask(__name__)

# mysql = MySQL()
# app.config['MYSQL_DATABASE_USER'] = os.getenv('MYSQL_DATABASE_USER')
# app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('MYSQL_DATABASE_PASSWORD')
# app.config['MYSQL_DATABASE_DB'] = os.getenv('MYSQL_DATABASE_DB')
# app.config['MYSQL_DATABASE_HOST'] = os.getenv('MYSQL_DATABASE_HOST')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# mysql.init_app(app)

user = Blueprint("user", __name__)

logger = get_logger(__name__)

DATABASE_URL = f"postgres://{os.getenv('PGUSER')}:{os.getenv('PGPASSWORD')}@{os.getenv('PGHOST')}/{os.getenv('PGDATABASE')}"
if os.getenv("DATABASE_URL") != "":
    DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)

def get_request_context(f):
    @wraps(f)
    def decorated_function(*args, **kws):

        loggedInUserData = g.loggedInUserData
        return f(loggedInUserData, *args, **kws)

    return decorated_function

@user.route("/status/live", methods=["GET", "POST"])
def liveness_user_service():
    return jsonify({
        "status" : "success", 
        "message": "This is user-service liveness probe, service is up and running !"
        }), 200

@user.route("/status/health", methods=["GET", "POST"])
def health_check_user_service():

    POSTGRES_SUCCESS, APP_SUCCESS = True, True
    components_check = [
        {"postgresDB": POSTGRES_SUCCESS},
        {"application": APP_SUCCESS}
    ]

    try:
        subprocess_output = subprocess.run(["pg_isready", "-h", f"{os.getenv('PGHOST')}"])
        if subprocess_output.returncode != 0:
            POSTGRES_SUCCESS = False
    except Exception as e:
        logger.info(e)

    return jsonify({
        "status" : "success", 
        "component_status": components_check
        }), 200

@user.route("/users", methods=["GET"])
@get_request_context
def get_all_current_users(loggedInUser):

    # conn = mysql.connect()
    cursor = conn.cursor()
    affected_count = 0

    query = "SELECT * FROM users"
    try:
        cursor.execute(query)
        affected_count = cursor.rowcount
        db_data = cursor.fetchall()
        logger.info("----------------------------------------------------")
        logger.info(cursor.query.decode())
        logger.info(f"{affected_count} rows affected")
    except Exception as e:
        logger.info(e)
    finally:
        cursor.close()

    logger.info("----------------------------------------------------")

    users_data = []
    for item in db_data:
        users_data.append(item)

    response = {}
    response["status"] = "success"
    if affected_count != 0:
        response["message"] = "Users fetched successfully !"
        response["users_data"] = users_data
    else:
        response["message"] = "No active users found in records !"

    return jsonify(response), 200


@user.route("/data", methods=["POST"])
@get_request_context
def upsert_user_data(loggedInUser):

    user_id = loggedInUser["user_id"]
    post_request = request.get_json(force=True)
    profile_pic_url = post_request["profile_pic"]
    # conn = mysql.connect()
    cursor = conn.cursor()
    affected_count = 0

    try:

        selectUserQuery = (
            "SELECT * FROM users WHERE user_id = %s"
        )

        cursor.execute(selectUserQuery, (user_id,))
        affected_count = cursor.rowcount
        logger.info("----------------------------------------------------")
        logger.info("Check if user already exists ...")
        logger.info(cursor.query.decode())
        logger.info(f"{affected_count} rows affected")
        db_data = cursor.fetchone()
        logger.info("db_data: %s", db_data)

        if affected_count == 0:

            logger.info("User doesn't exists ! Creating new user .....")
            insertUserQuery = "INSERT INTO users(user_id, username, firstname, lastname, email, profile_pic_url) VALUES(%s, %s, %s, %s, %s, %s)"
            cursor.execute(
                insertUserQuery,
                (
                    user_id,
                    loggedInUser["username"],
                    loggedInUser["firstname"],
                    loggedInUser["lastname"],
                    loggedInUser["email"],
                    profile_pic_url,
                ),
            )
            conn.commit()
            affected_count = cursor.rowcount
            logger.info(cursor.query.decode())
            logger.info(f"{affected_count} rows affected")
        else:
            logger.info("User already exists ..., skip creation of new entity")


    except Exception as e:
        logger.info(e)
    finally:
        cursor.close()

    logger.info("----------------------------------------------------")

    response = {}
    response["status"] = "success"
    response["message"] = "User data updated succesfully"

    return jsonify(response), 200


@user.route("/status", methods=["POST"])
@get_request_context
def fetch_user_status_auth(loggedInUser):

    post_request = request.get_json(force=True)

    # conn = mysql.connect()
    cursor = conn.cursor()
    affected_count = 0

    query = "SELECT * FROM users WHERE username = %s"
    try:
        cursor.execute(query, (post_request["username"],))
        affected_count = cursor.rowcount
        logger.info("----------------------------------------------------")
        logger.info(cursor.query.decode())
        logger.info(f"{affected_count} rows affected")
        user_data = cursor.fetchone()
        logger.info("DB DATA : %s", user_data)
    except Exception as e:
        logger.info(e)
    finally:
        cursor.close()

    logger.info("----------------------------------------------------")

    response = {}
    if affected_count == 0:
        response["status"] = "failure"
        response["message"] = "No user is found with the given username !"
        return jsonify(response), 401
    else:
        response["status"] = "success"
        response["message"] = "User is active and found in our records !"
        response["user_data"] = {"firstname": user_data[3], "email": user_data[5]}
        return jsonify(response), 200


@user.route("/subscription", methods=["POST"])
@get_request_context
def subscribe_user(loggedInuser):

    # conn = mysql.connect()
    cursor = conn.cursor()
    affected_count = 0

    post_request = request.get_json(force=True)
    list_id = post_request["list_id"]
    email_id = post_request.get("email_id")

    subscribedByUserFetchQuery = (
        "SELECT t.user_id FROM task_list t WHERE t.list_id = %s"
    )
    db_user_data = None
    try:
        cursor.execute(subscribedByUserFetchQuery, (list_id,))
        affected_count = cursor.rowcount
        logger.info("----------------------------------------------------")
        logger.info(cursor.query.decode())
        logger.info(f"{affected_count} rows affected")
        db_user_data = cursor.fetchone()
        logger.info("DB DATA : %s", db_user_data)
    except Exception as e:
        logger.info(e)

    response = {}
    if affected_count == 0:
        response["status"] = "failure"
        response["message"] = "Unauthorized request for user subscription !"
        return jsonify(response), 401

    subscribedForUserId = db_user_data[0]
    subscribedByUserId = loggedInuser["user_id"]

    selectUserSubscriberListFetchQuery = (
        "SELECT u.subscribed_by FROM users u WHERE u.user_id = %s"
    )
    subscribedByUsersList = []
    try:
        cursor.execute(selectUserSubscriberListFetchQuery, (subscribedForUserId,))
        affected_count = cursor.rowcount
        logger.info("----------------------------------------------------")
        logger.info(cursor.query.decode())
        logger.info(f"{affected_count} rows affected")
        db_data = cursor.fetchone()
        subscribedByUsersList = db_data[0]
        logger.info("DB DATA : %s", db_data)
    except Exception as e:
        logger.info(e)

    # check if user already subscribes for this creator
    ifUserAlreadySubscribed = False
    for id in subscribedByUsersList:
        if id == subscribedByUserId:
            ifUserAlreadySubscribed = True

    response = {}
    if ifUserAlreadySubscribed:
        response["subscription_status"] = "INACTIVE"
        updateFlaggedByUsersquery = "UPDATE users SET subscriber_count = subscriber_count - 1, subscribed_by=array_remove(subscribed_by, %s) WHERE user_id = %s"
        try:
            cursor.execute(
                updateFlaggedByUsersquery,
                (
                    subscribedByUserId,
                    subscribedForUserId,
                ),
            )
            conn.commit()
            affected_count = cursor.rowcount
            logger.info("----------------------------------------------------")
            logger.info(cursor.query.decode())
            logger.info(f"{affected_count} rows affected")
            db_data = cursor.fetchone()
            logger.info("DB DATA : %s", db_data)
        except Exception as e:
            logger.info(e)
        finally:
            cursor.close()

    else:
        response["subscription_status"] = "ACTIVE"
        updateFlaggedByUsersquery = "UPDATE users SET subscriber_count = subscriber_count + 1, subscribed_by=array_append(subscribed_by, %s) WHERE user_id = %s"
        try:
            cursor.execute(
                updateFlaggedByUsersquery,
                (
                    subscribedByUserId,
                    subscribedForUserId,
                ),
            )
            conn.commit()
            affected_count = cursor.rowcount
            logger.info("----------------------------------------------------")
            logger.info(cursor.query.decode())
            logger.info(f"{affected_count} rows affected")
            db_data = cursor.fetchone()
            logger.info("DB DATA : %s", db_data)
        except Exception as e:
            logger.info(e)
        finally:
            updateUserEmailquery = "UPDATE users SET email = %s WHERE user_id = %s"
            cursor.execute(
                updateUserEmailquery,
                (
                    email_id,
                    subscribedByUserId,
                ),
            )
            conn.commit()
            affected_count = cursor.rowcount
            logger.info(cursor.query.decode())
            logger.info(f"{affected_count} rows affected")
            cursor.close()

    logger.info("----------------------------------------------------")

    if affected_count == 0:
        response["status"] = "failure"
        response["message"] = "User subscription failed !"
        return jsonify(response), 500
    else:
        response["status"] = "success"
        if response["subscription_status"] == "ACTIVE":
            response[
                "message"
            ] = "User has been subscribed to the creator's space successfully !, you will get timely notifications when new posts come out."
        elif response["subscription_status"] == "INACTIVE":
            response[
                "message"
            ] = "User has been unsubscribed to the creator's space successfully !, you will not receive any notifications for this creator's new posts."

        return jsonify(response), 200


@user.route("/data", methods=["DELETE"])
@get_request_context
def delete_user_data(loggedInUser):

    post_request = request.get_json(force=True)

    # conn = mysql.connect()
    cursor = conn.cursor()
    affected_count = 0

    deleteUserDataQuery = "DELETE FROM users u WHERE u.user_id = %s"
    try:
        cursor.execute(deleteUserDataQuery, (loggedInUser["user_id"],))
        conn.commit()
        affected_count = cursor.rowcount
        logger.info("----------------------------------------------------")
        logger.info(cursor.query.decode())
        logger.info(f"{affected_count} rows affected")
    except Exception as e:
        logger.info(e)

    deleteSessionsDataQuery = "DELETE FROM login_sessions ls WHERE ls.user_id = %s"
    try:
        cursor.execute(deleteSessionsDataQuery, (loggedInUser["user_id"],))
        conn.commit()
        affected_count = cursor.rowcount
        logger.info("----------------------------------------------------")
        logger.info(cursor.query.decode())
        logger.info(f"{affected_count} rows affected")
    except Exception as e:
        logger.info(e)

    deleteNotificationsDataQuery = (
        "DELETE FROM user_notifications un WHERE un.user_id = %s"
    )
    try:
        cursor.execute(deleteNotificationsDataQuery, (loggedInUser["user_id"],))
        conn.commit()
        affected_count = cursor.rowcount
        logger.info("----------------------------------------------------")
        logger.info(cursor.query.decode())
        logger.info(f"{affected_count} rows affected")
    except Exception as e:
        logger.info(e)
    finally:
        cursor.close()

    logger.info("----------------------------------------------------")

    response = {}
    if affected_count == 0:
        response["status"] = "failure"
        response["message"] = "Deletion of user failed !"
        return jsonify(response), 500
    else:
        response["status"] = "success"
        response["message"] = "User data deleted successfully !"
        return jsonify(response), 200
