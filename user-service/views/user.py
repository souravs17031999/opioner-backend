from flask import Flask, json, jsonify, request, Response, Blueprint
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

app = Flask(__name__)

# mysql = MySQL()
# app.config['MYSQL_DATABASE_USER'] = os.getenv('MYSQL_DATABASE_USER')
# app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('MYSQL_DATABASE_PASSWORD')
# app.config['MYSQL_DATABASE_DB'] = os.getenv('MYSQL_DATABASE_DB')
# app.config['MYSQL_DATABASE_HOST'] = os.getenv('MYSQL_DATABASE_HOST')
# app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# mysql.init_app(app)

user = Blueprint("user", __name__)

DATABASE_URL = f"postgres://{os.getenv('PGUSER')}:{os.getenv('PGPASSWORD')}@{os.getenv('PGHOST')}/{os.getenv('PGDATABASE')}"
if os.getenv("DATABASE_URL") != "":
    DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)

firebaseConfig = {
    "apiKey": "AIzaSyBL6NJtZjwP2XztD-Hz2I9GQoeYXCu6lWU",
    "authDomain": "todo-customized-list.firebaseapp.com",
    "projectId": "todo-customized-list",
    "storageBucket": "todo-customized-list.appspot.com",
    "messagingSenderId": "318415610285",
    "appId": "1:318415610285:web:86b7214fc51d13be9c4124",
    "measurementId": "G-3B3EKNCNJ6",
    "databaseURL": "",
}

FIREBASE_PROFILE_PIC_PATH = os.getenv("FIREBASE_PROFILE_PIC_PATH")

firebase = pyrebase.initialize_app(firebaseConfig)
storage = firebase.storage()


def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("access-token")
        response = {}

        if not token:
            response["status"] = "failure"
            response["message"] = "Invalid token !"
            return jsonify(response), 401

        try:
            data = jwt.decode(token, app.config["SECRET_KEY"])
        except:
            response["status"] = "failure"
            response["message"] = "User not authorized !"
            return jsonify(response), 401

        return f(*args, **kwargs)

    return wrapper


def authorize(f):
    @wraps(f)
    def decorated_function(*args, **kws):

        cursor = conn.cursor()

        request_user_id = -1
        if request.method == "GET":
            request_user_id = request.args.get("user_id")
        else:
            request_user_id = request.get_json(force=True).get("user_id")

        print("Authorization for user_id: ", request_user_id)
        authorizeUserQuery = "SELECT u.* FROM users u WHERE u.user_id = %s"
        affected_count = 0
        user_data = None
        try:
            cursor.execute(authorizeUserQuery, (request_user_id,))
            affected_count = cursor.rowcount
            user_data = cursor.fetchone()
            print(cursor.query.decode())
            print(f"{affected_count} rows affected")
            print("----------------------------------------------------")
            print("logged in authorized user data: ", user_data)
            print("----------------------------------------------------")
            conn.commit()
        except Exception as e:
            print(e)
            conn.rollback()
        finally:
            cursor.close()

        if affected_count == 0:
            return (
                jsonify(
                    {
                        "status": "failure",
                        "message": "unauthorized request !",
                    }
                ),
                401,
            )

        loggedInUser = {
            "user_id": user_data[0],
            "username": user_data[1],
            "firstname": user_data[3],
            "lastname": user_data[4],
            "email": user_data[5],
            "phone": user_data[6],
            "created_at": user_data[7],
            "subscriber_count": user_data[8],
            "subscribed_by": user_data[9],
        }

        return f(loggedInUser, *args, **kws)

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
        print(e)

    return jsonify({
        "status" : "success", 
        "component_status": components_check
        }), 200

@user.route("/fetch-users", methods=["GET"])
def get_all_current_users():

    # conn = mysql.connect()
    cursor = conn.cursor()
    affected_count = 0

    query = "SELECT * FROM users"
    try:
        cursor.execute(query)
        affected_count = cursor.rowcount
        db_data = cursor.fetchall()
        print("----------------------------------------------------")
        print(cursor.query.decode())
        print(f"{affected_count} rows affected")
    except Exception as e:
        print(e)
    finally:
        cursor.close()

    print("----------------------------------------------------")

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


@user.route("/fetch-user-data", methods=["GET"])
def fetch_user_data():

    user_id = request.args.get("user_id")
    # conn = mysql.connect()
    cursor = conn.cursor()
    affected_count = 0

    query = "SELECT username,firstname,lastname,phone,email,is_google_verified,google_profile_url,is_facebook_verified,facebook_profile_url FROM users WHERE user_id = %s"
    try:
        cursor.execute(query, (user_id,))
        affected_count = cursor.rowcount
        print("----------------------------------------------------")
        print(cursor.query.decode())
        print(f"{affected_count} rows affected")
        db_data = cursor.fetchone()
        print("DB DATA : ", db_data)
    except Exception as e:
        print(e)
    finally:
        cursor.close()

    print("----------------------------------------------------")

    # storage.child("profile_avatar/1.jpg").put(
    #     "/home/souravcovenant/Desktop/MENU_grocery_template/avatar.png")
    # print(storage)
    print("****** FETCHING PROFILE PIC FROM FIREBASE *******")
    APP_UPLOAD_FIREBASE_PATH = f"{FIREBASE_PROFILE_PIC_PATH}/{user_id}.png"
    print(
        "[debug]: fetching from firebase at APP_UPLOAD_FIREBASE_PATH: ",
        APP_UPLOAD_FIREBASE_PATH,
    )
    avatar_fetched_image_path = storage.child(APP_UPLOAD_FIREBASE_PATH).get_url(user_id)
    print("============ Got user image: ", avatar_fetched_image_path)

    response = {}
    response["status"] = "success"
    if affected_count != 0:
        response["message"] = "Users fetched successfully !"
        response["user_data"] = {
            "username": db_data[0],
            "firstname": db_data[1],
            "lastname": db_data[2],
            "phone": db_data[3],
            "email": db_data[4],
            "profile_picture_url": avatar_fetched_image_path,
            "is_google_verified": db_data[5],
            "google_profile_url": db_data[6],
            "is_facebook_verified": db_data[7],
            "facebook_profile_url": db_data[8],
        }

        return jsonify(response), 200

    else:
        response["message"] = "Unauthorized, No active users found in records !"
        return jsonify(response), 401


@user.route("/update-profile-pic", methods=["POST"])
def update_profile_pic_for_user():

    if request.files.get("file") is None:
        return (
            jsonify(
                {
                    "status": "failure",
                    "message": "No file sent for uploading or wrong format sent for request ! Try again",
                }
            ),
            401,
        )

    profile_avatar_user = request.files["file"]
    user_id = request.form["user_id"]
    APP_UPLOAD_FIREBASE_PATH = f"{FIREBASE_PROFILE_PIC_PATH}/{user_id}.png"
    print(
        "[debug]: uploading to firebase at APP_UPLOAD_FIREBASE_PATH: ",
        APP_UPLOAD_FIREBASE_PATH,
    )
    storage.child(APP_UPLOAD_FIREBASE_PATH).put(profile_avatar_user)

    response = {}
    response["status"] = "success"
    response["message"] = "Profile upload successfully !"

    return jsonify(response), 200


@user.route("/fetch/user-status", methods=["POST"])
def fetch_user_status_auth():

    post_request = request.get_json(force=True)

    # conn = mysql.connect()
    cursor = conn.cursor()
    affected_count = 0

    query = "SELECT * FROM users WHERE username = %s"
    try:
        cursor.execute(query, (post_request["username"],))
        affected_count = cursor.rowcount
        print("----------------------------------------------------")
        print(cursor.query.decode())
        print(f"{affected_count} rows affected")
        user_data = cursor.fetchone()
        print("DB DATA : ", user_data)
    except Exception as e:
        print(e)
    finally:
        cursor.close()

    print("----------------------------------------------------")

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
@authorize
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
        print("----------------------------------------------------")
        print(cursor.query.decode())
        print(f"{affected_count} rows affected")
        db_user_data = cursor.fetchone()
        print("DB DATA : ", db_user_data)
    except Exception as e:
        print(e)

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
        print("----------------------------------------------------")
        print(cursor.query.decode())
        print(f"{affected_count} rows affected")
        db_data = cursor.fetchone()
        subscribedByUsersList = db_data[0]
        print("DB DATA : ", db_data)
    except Exception as e:
        print(e)

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
            print("----------------------------------------------------")
            print(cursor.query.decode())
            print(f"{affected_count} rows affected")
            db_data = cursor.fetchone()
            print("DB DATA : ", db_data)
        except Exception as e:
            print(e)
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
            print("----------------------------------------------------")
            print(cursor.query.decode())
            print(f"{affected_count} rows affected")
            db_data = cursor.fetchone()
            print("DB DATA : ", db_data)
        except Exception as e:
            print(e)
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
            print(cursor.query.decode())
            print(f"{affected_count} rows affected")
            cursor.close()

    print("----------------------------------------------------")

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
def delete_user_data():

    post_request = request.get_json(force=True)

    # conn = mysql.connect()
    cursor = conn.cursor()
    affected_count = 0

    deleteUserDataQuery = "DELETE FROM users u WHERE u.user_id = %s"
    try:
        cursor.execute(deleteUserDataQuery, (post_request["user_id"],))
        conn.commit()
        affected_count = cursor.rowcount
        print("----------------------------------------------------")
        print(cursor.query.decode())
        print(f"{affected_count} rows affected")
    except Exception as e:
        print(e)

    deleteSessionsDataQuery = "DELETE FROM login_sessions ls WHERE ls.user_id = %s"
    try:
        cursor.execute(deleteSessionsDataQuery, (post_request["user_id"],))
        conn.commit()
        affected_count = cursor.rowcount
        print("----------------------------------------------------")
        print(cursor.query.decode())
        print(f"{affected_count} rows affected")
    except Exception as e:
        print(e)

    deleteNotificationsDataQuery = (
        "DELETE FROM user_notifications un WHERE un.user_id = %s"
    )
    try:
        cursor.execute(deleteNotificationsDataQuery, (post_request["user_id"],))
        conn.commit()
        affected_count = cursor.rowcount
        print("----------------------------------------------------")
        print(cursor.query.decode())
        print(f"{affected_count} rows affected")
    except Exception as e:
        print(e)
    finally:
        cursor.close()

    print("----------------------------------------------------")

    response = {}
    if affected_count == 0:
        response["status"] = "failure"
        response["message"] = "Deletion of user failed !"
        return jsonify(response), 500
    else:
        response["status"] = "success"
        response["message"] = "User data deleted successfully !"
        return jsonify(response), 200
