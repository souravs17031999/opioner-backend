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

conn = psycopg2.connect(DATABASE_URL)


def get_password_hash(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    print("hashedpwd:", hashed)
    return hashed.decode()


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
        print("****** PASSWORD AUTHENTICATION STARTED *******")
        if bcrypt.checkpw(post_request["password"].encode(), db_data[2].encode()):
            # auth user request
            # token = jwt.encode({'user': post_request["username"], 'exp': datetime.datetime.utcnow(
            # ) + datetime.timedelta(minutes=5)}, app.config['SECRET_KEY'])

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


@auth.route("/signup-user", methods=["POST"])
def signup_to_app():
    post_request = request.get_json(force=True)
    hashed_password = get_password_hash(post_request["password"])

    # conn = mysql.connect()
    cursor = conn.cursor()

    authSelectQuery = "SELECT * FROM users WHERE username = %s"
    affected_count = 0
    try:
        cursor.execute(authSelectQuery, (post_request["username"],))
        affected_count = cursor.rowcount
        print("----------------------------------------------------")
        print(cursor.query.decode())
        print(f"{affected_count} rows affected")
    except Exception as e:
        print(e)
    finally:
        if affected_count != 0:
            cursor.close()

    response = {}
    if affected_count != 0:
        response["status"] = "failure"
        response["message"] = "Chosen username already exists !"
        return jsonify(response), 403

    insertQuery = "INSERT INTO users(username, password, firstname, lastname) VALUES(%s, %s, %s, %s)"

    try:
        cursor.execute(
            insertQuery,
            (
                post_request["username"],
                hashed_password,
                post_request["firstname"],
                post_request["lastname"],
            ),
        )
        conn.commit()
        print(cursor.query.decode())
        print(f"{cursor.rowcount} rows affected")
    except Exception as e:
        print(e)
    finally:
        selectQuery = "SELECT * FROM users WHERE username = %s"
        cursor.execute(selectQuery, (post_request["username"],))
        print(cursor.query.decode())
        affected_count = cursor.rowcount
        print(f"{cursor.rowcount} rows affected")
        db_data = cursor.fetchone()
        print("DB DATA : ", db_data)

    print("----------------------------------------------------")

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
        print(cursor.query.decode())
        print(f"{cursor.rowcount} rows affected")
    except Exception as e:
        print(e)
    finally:
        cursor.close()

    print("----------------------------------------------------")

    if affected_count == 0:
        response["status"] = "failure"
        response["message"] = "INSERTION OF RECORD FAILED !, User already exists"
        return jsonify(response), 500

    else:
        # auth user request
        # token = jwt.encode({'user': post_request["username"], 'exp': datetime.datetime.utcnow(
        # ) + datetime.timedelta(minutes=5)}, app.config['SECRET_KEY'])

        user_data = {
            "user_id": db_data[0],
            "username": db_data[1],
            "firstname": db_data[4],
        }
        response["user_data"] = user_data
        # response["token"] = token.decode()
        response["status"] = "success"
        response["message"] = "DATA INSERTED SUCCESSFULLY !"
        return jsonify(response), 200


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

    response = {}
    if affected_count == 0:
        response["status"] = "failure"
        response["message"] = "Unauthorized request, cannot update password for user !"
        return jsonify(response), 401

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
