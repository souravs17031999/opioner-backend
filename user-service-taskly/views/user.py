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


@user.route("/test", methods=["GET", "POST"])
def test_user_service():
    return "<h1> This is user service testing, service is up and running !</h1>"


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

    query = (
        "SELECT username,firstname,lastname,phone,email FROM users WHERE user_id = %s"
    )
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
    APP_UPLOAD_FIREBASE_PATH = f"profile_avatar/{user_id}.png"
    avatar_fetched_image_path = storage.child(APP_UPLOAD_FIREBASE_PATH).get_url(user_id)

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
    APP_UPLOAD_FIREBASE_PATH = f"profile_avatar/{user_id}.png"
    storage.child(APP_UPLOAD_FIREBASE_PATH).put(profile_avatar_user)

    response = {}
    response["status"] = "success"
    response["message"] = "Profile upload successfully !"

    return jsonify(response), 200


@user.route("/fetch-user-status", methods=["POST"])
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
        db_data = cursor.fetchone()
        print("DB DATA : ", db_data)
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
        return jsonify(response), 200
