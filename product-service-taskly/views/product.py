from flask import Flask, json, jsonify, request, Response, Blueprint
from werkzeug.datastructures import Headers

# from flaskext.mysql import MySQL
import jwt
import datetime
from functools import wraps
import os
import psycopg2


app = Flask(__name__)

# mysql = MySQL()
# app.config['MYSQL_DATABASE_USER'] = os.getenv('MYSQL_DATABASE_USER')
# app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('MYSQL_DATABASE_PASSWORD')
# app.config['MYSQL_DATABASE_DB'] = os.getenv('MYSQL_DATABASE_DB')
# app.config['MYSQL_DATABASE_HOST'] = os.getenv('MYSQL_DATABASE_HOST')
# app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# mysql.init_app(app)

product = Blueprint("product", __name__)
DATABASE_URL = f"postgres://{os.getenv('PGUSER')}:{os.getenv('PGPASSWORD')}@{os.getenv('PGHOST')}/{os.getenv('PGDATABASE')}"

conn = psycopg2.connect(DATABASE_URL)


@product.route("/test", methods=["GET", "POST"])
def test_auth_service():
    return "<h1> This is product service testing, service is up and running !</h1>"


@product.route("/fetch-list", methods=["GET"])
def fetch_user_list():
    user_id = request.args.get("user_id")

    # conn = mysql.connect()
    cursor = conn.cursor()

    if user_id == "null" or user_id is None:
        return (
            jsonify(
                {
                    "status": "failure",
                    "message": "unauthorized request to fetch lists for the user !",
                }
            ),
            401,
        )

    query = "SELECT u.*, t.* FROM users u INNER JOIN task_list t ON t.user_id = u.user_id WHERE u.user_id = %s ORDER BY t.list_id"

    affected_count = 0
    try:
        cursor.execute(query, (user_id,))
        affected_count = cursor.rowcount
        db_data = cursor.fetchall()
        print("----------------------------------------------------")
        print(cursor.query.decode())
        print(f"{affected_count} rows affected")
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        cursor.close()

    print("DB DATA : ", db_data)
    print("----------------------------------------------------")

    response = {}

    if affected_count == 0:
        response["status"] = "failure"
        response["message"] = "Empty lists for given user !"
        return jsonify(response), 200

    else:
        tasks = []
        is_reminder_set = False
        for item in db_data:
            if item[11] or item[12]:
                is_reminder_set = True
            else:
                is_reminder_set = False

            tasks.append(
                {
                    "id": item[7],
                    "description": item[9],
                    "status": item[10],
                    "is_reminder_set": is_reminder_set,
                }
            )

        user_data = {
            "user_id": db_data[0][0],
            "firstname": db_data[0][3],
            "phone": db_data[0][6],
            "email": db_data[0][5],
        }
        response["user_data"] = user_data
        response["status"] = "success"
        response["task"] = tasks

        return jsonify(response), 200


@product.route("/upsert-task", methods=["POST"])
def submit_or_update_user_task():

    post_request = request.get_json(force=True)

    # conn = mysql.connect()
    cursor = conn.cursor()
    affected_count = 0
    user_id = post_request["user_id"]
    description = post_request["item"]
    list_id = post_request.get("id")

    db_data = None
    if post_request["update_flag"] == 0:
        query = "INSERT INTO task_list(user_id, description) VALUES(%s, %s)"

        try:
            affected_count = cursor.execute(
                query,
                (
                    user_id,
                    description,
                ),
            )
            conn.commit()
            affected_count = cursor.rowcount
            print("----------------------------------------------------")
            print(cursor.query.decode())
            print(f"{affected_count} rows affected")
            db_data = cursor.fetchone()
            print("db_data: ", db_data)

        except Exception as e:
            print(e)
        finally:
            selectQuery = (
                "SELECT * FROM task_list WHERE user_id = %s AND description = %s"
            )
            cursor.execute(selectQuery, (user_id, description))
            affected_count = cursor.rowcount
            db_data = cursor.fetchone()

            print(cursor.query.decode())
            print(f"{affected_count} rows affected")
            print("db_data: ", db_data)
            print("----------------------------------------------------")

            cursor.close()

    else:
        query = (
            "UPDATE task_list SET description = %s WHERE user_id = %s AND list_id = %s"
        )

        try:
            affected_count = cursor.execute(
                query,
                (
                    description,
                    user_id,
                    list_id,
                ),
            )
            conn.commit()
            affected_count = cursor.rowcount
            print("----------------------------------------------------")
            print(cursor.query.decode())
            print(f"{affected_count} rows affected")
            db_data = cursor.fetchone()
            print("db_data: ", db_data)

        except Exception as e:
            print(e)
        finally:
            cursor.close()

    print("----------------------------------------------------")

    response = {}
    if affected_count == 0 and post_request["update_flag"] == 0:
        response["status"] = "failure"
        response["message"] = "NO lists found for the requested user !"
        return jsonify(response), 500
    else:
        if db_data is not None:
            response["id"] = db_data[0]
            response["status_tag"] = db_data[3]
        response["status"] = "success"
        response["message"] = "INSERTION/UPDATION SUCCESFULLY DONE !"
        return jsonify(response), 200


@product.route("/delete-task", methods=["POST"])
def delete_user_list_item():

    post_request = request.get_json(force=True)
    user_id = post_request["user_id"]
    list_id = post_request.get("id")
    list_ids = post_request.get("list_ids")

    # conn = mysql.connect()
    cursor = conn.cursor()
    affected_count = 0

    if post_request["all_flag"] == 0:
        query = "DELETE FROM task_list WHERE user_id = %s AND list_id = %s"
        try:
            cursor.execute(
                query,
                (
                    user_id,
                    list_id,
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

    else:

        list_ids = list_ids.split(",")
        query = "DELETE FROM task_list WHERE user_id = %s AND list_id IN %s"
        try:
            cursor.execute(query, (user_id, list_ids))
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

    response = {}
    if affected_count == 0:
        response["status"] = "failure"
        response[
            "message"
        ] = "DELETION OF RECORD FAILED !, NO record found with given id"
        return jsonify(response), 500
    else:
        response["status"] = "success"
        response["message"] = "DELETION OF RECORD SUCCESSFULLY DONE !"
        return jsonify(response), 200


@product.route("/update-task-status", methods=["POST"])
def update_user_task_status():

    post_request = request.get_json(force=True)
    user_id = post_request["user_id"]
    status_tag = post_request["tag"]
    task_id = post_request["task_id"]

    # conn = mysql.connect()
    cursor = conn.cursor()
    affected_count = 0

    updateSTatusQuery = (
        "UPDATE task_list SET status_tag = %s WHERE list_id = %s AND user_id = %s"
    )
    try:
        cursor.execute(
            updateSTatusQuery,
            (
                status_tag,
                task_id,
                user_id,
            ),
        )
        conn.commit()
        affected_count = cursor.rowcount
        print("----------------------------------------------------")
        print(cursor.query.decode())
        print(f"{affected_count} rows affected")

    except Exception as e:
        print(e)

    finally:
        if status_tag != "Done":
            cursor.close()

    if status_tag == "Done":
        updateEmailStatusQuery = "UPDATE task_list SET is_phone_pushed = %s, is_email_pushed = %s WHERE list_id = %s AND user_id = %s"
        try:
            cursor.execute(
                updateEmailStatusQuery,
                (
                    0,
                    0,
                    task_id,
                    user_id,
                ),
            )
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

    return (
        jsonify({"status": "success", "message": "Task status updated successfully"}),
        200,
    )
