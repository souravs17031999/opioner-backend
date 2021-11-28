from flask import Flask, json, jsonify, request, Response, Blueprint
from werkzeug.datastructures import Headers

# from flaskext.mysql import MySQL
import jwt
import datetime
from functools import wraps
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import jinja2
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

notification = Blueprint("notification", __name__)
DATABASE_URL = f"postgres://{os.getenv('PGUSER')}:{os.getenv('PGPASSWORD')}@{os.getenv('PGHOST')}/{os.getenv('PGDATABASE')}"
SENDGRID_API_KEY_PROD = os.getenv("SENDGRID_API_KEY_PROD")

conn = psycopg2.connect(DATABASE_URL)


def generate_mail_content(template_name, **template_vars):

    templateLoader = jinja2.FileSystemLoader(searchpath="templates")
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template(template_name)
    return template.render(**template_vars)


def send_reminder_mail_notifications(email, name):

    sender_email = "taskly.contact@gmail.com"
    subject = "Reminder for your task created successfully on Taskly - let's do it !"
    receiver_email = email
    firstname = name

    print("SENDER EMAIL : ", sender_email)
    print("RECEIVER EMAIL : ", receiver_email)
    print("Subject: ", subject)

    mail_body = generate_mail_content("first_reminder_mail.html", firstname=firstname)
    message = Mail(
        from_email=sender_email,
        to_emails=receiver_email,
        subject=subject,
        html_content=mail_body,
    )

    try:
        sendgridAPIClientKey = SENDGRID_API_KEY_PROD
        sg = SendGridAPIClient(sendgridAPIClientKey)
        response = sg.send(message)
        print(response.status_code)
    except Exception as e:
        print(e)
        print(e.body)
        # print(e.message)
        print("failure !")
        return {"status": "failure", "message": "Email reminder sending failed !"}

    print("success !")
    return {
        "status": "success",
        "message": "Email reminder to user send successfully !",
    }


def stop_reminder_mail_notifications(email, name):

    sender_email = "taskly.contact@gmail.com"
    subject = "Reminder stopped successfully on Taskly"
    receiver_email = email
    firstname = name

    print("SENDER EMAIL : ", sender_email)
    print("RECEIVER EMAIL : ", receiver_email)
    print("Subject: ", subject)

    mail_body = generate_mail_content("unsubscribe_mail.html", firstname=firstname)
    message = Mail(
        from_email=sender_email,
        to_emails=receiver_email,
        subject=subject,
        html_content=mail_body,
    )

    try:
        sendgridAPIClientKey = SENDGRID_API_KEY_PROD
        sg = SendGridAPIClient(sendgridAPIClientKey)
        response = sg.send(message)
        print(response.status_code)
    except Exception as e:
        print(e)
        print(e.body)
        # print(e.message)
        print("failure !")
        return {"status": "failure", "message": "Email stop reminder sending failed !"}

    print("success !")
    return {
        "status": "success",
        "message": "Email stop reminder to user send successfully !",
    }


@notification.route("/test", methods=["GET", "POST"])
def test_notification_service():
    return "<h1> This is notification service testing, service is up and running !</h1>"


@notification.route("/subscribe-notification", methods=["POST"])
def subscribe_user_to_notifications():

    post_request = request.get_json(force=True)
    # conn = mysql.connect()
    cursor = conn.cursor()
    affected_count = 0

    updateQueryUserData = "UPDATE users SET phone = %s, email = %s WHERE user_id = %s"
    try:
        cursor.execute(
            updateQueryUserData,
            (
                post_request["phone"],
                post_request["email"],
                post_request["user_id"],
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
        selectQuery = "SELECT * FROM users WHERE user_id = %s"
        cursor.execute(selectQuery, (post_request["user_id"],))

        affected_count = cursor.rowcount
        print(cursor.query.decode())
        print(f"{affected_count} rows affected")
        db_data = cursor.fetchone()
        print("DB DATA : ", db_data)

    firstname = db_data[3]

    updateNotifyForText = "UPDATE task_list SET is_phone_pushed = %s, is_email_pushed = %s WHERE list_id = %s AND user_id = %s"
    try:
        affected_count = cursor.execute(
            updateNotifyForText,
            (
                post_request["is_phone"],
                post_request["is_email"],
                post_request["task_id"],
                post_request["user_id"],
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

    if (
        send_reminder_mail_notifications(post_request["email"], firstname)["status"]
        == "success"
    ):
        print("SUCCESS: REMINDER MAIL FOR NOTIFICATION USER SENT SUCCESFULLY !")
        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Push reminders set successfully, User subscribed to notifications !",
                }
            ),
            200,
        )
    else:
        print("FAILURE: REMINDER MAIL FOR NOTIFICATION USER FAILED !")
        return (
            jsonify(
                {
                    "status": "failure",
                    "message": "Push reminders failed, User not subscribed to notifications !",
                }
            ),
            500,
        )


@notification.route("/unsubscribe-notification", methods=["POST"])
def unsubscribe_user_to_notifications():

    post_request = request.get_json(force=True)
    # conn = mysql.connect()
    cursor = conn.cursor()
    affected_count = 0

    updateQueryUserData = "UPDATE task_list SET is_phone_pushed = %s, is_email_pushed = %s WHERE list_id = %s AND user_id = %s"
    try:
        affected_count = cursor.execute(
            updateQueryUserData,
            (
                0,
                0,
                post_request["task_id"],
                post_request["user_id"],
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
        selectQuery = "SELECT * FROM users WHERE user_id = %s"
        cursor.execute(selectQuery, (post_request["user_id"],))

        affected_count = cursor.rowcount
        print(cursor.query.decode())
        print(f"{affected_count} rows affected")
        db_data = cursor.fetchone()
        print("DB DATA : ", db_data)
        cursor.close()

    print("----------------------------------------------------")

    firstname = db_data[3]
    email = db_data[5]

    if stop_reminder_mail_notifications(email, firstname)["status"] == "success":
        print("SUCCESS: STOP REMINDER MAIL FOR NOTIFICATION USER SENT SUCCESFULLY !")
        return (
            jsonify(
                {
                    "status": "success",
                    "message": "User unsubscribed to notifications !",
                }
            ),
            200,
        )
    else:
        print("FAILURE: STOP REMINDER MAIL FOR NOTIFICATION USER FAILED !")
        return (
            jsonify(
                {
                    "status": "failure",
                    "message": "User failed to unsubscribe notifications !",
                }
            ),
            500,
        )


@notification.route("/insert-notification", methods=["POST"])
def insert_notifications_for_user():

    post_request = request.get_json(force=True)
    event_type = post_request["event_type"]
    event_description = post_request["event_description"]
    user_id = post_request["user_id"]
    # conn = mysql.connect()
    cursor = conn.cursor()
    affected_count = 0

    insertQuery = "INSERT INTO user_notifications(event_type, description, user_id) VALUES(%s, %s, %s)"
    try:
        cursor.execute(
            insertQuery,
            (
                event_type,
                event_description,
                user_id,
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
        selectQuery = "SELECT * FROM user_notifications WHERE user_id = %s"
        cursor.execute(selectQuery, (user_id,))

        affected_count = cursor.rowcount
        print(cursor.query.decode())
        print(f"{affected_count} rows affected")
        db_data = cursor.fetchone()
        print("DB DATA : ", db_data)

        cursor.close()

    print("----------------------------------------------------")

    response = {}
    if affected_count == 0:
        response["status"] = "failure"
        response["message"] = "Failed to insert notification for user"
        return jsonify(response), 500
    else:
        response["status"] = "success"
        response["message"] = "Notification inserted successfully for user!"
        return jsonify(response), 200


@notification.route("/fetch-notifications", methods=["GET"])
def fetch_notifications_for_user():

    user_id = request.args.get("user_id")
    all_flag = request.args.get("all_flag")

    # conn = mysql.connect()
    cursor = conn.cursor()
    affected_count = 0

    allSelectQuery = (
        "SELECT * FROM user_notifications WHERE user_id = %s ORDER BY created_at DESC"
    )

    try:
        cursor.execute(allSelectQuery, (user_id,))
        affected_count = cursor.rowcount
        print("----------------------------------------------------")
        print(cursor.query.decode())
        print(f"{affected_count} rows affected")
        all_db_data = cursor.fetchall()
        print("DB DATA : ", all_db_data)
        total_notifications = len(all_db_data)

    except Exception as e:
        print(e)
    finally:
        cursor.close()

    response = {}
    response["status"] = "success"
    response["message"] = "Notification fetched successfully for user!"
    response["see_all"] = False

    if total_notifications > 3:
        response["see_all"] = True

    if all_flag == "true":
        notification_arr = []
        for item in all_db_data:
            notification_arr.append(
                {
                    "id": item[0],
                    "event_type": item[1],
                    "event_description": item[2],
                    "read_flag": item[4],
                    "created_at": item[5],
                }
            )

        response["see_all"] = False
        response["data"] = notification_arr
    else:
        iterator = 0
        notification_arr = []
        for item in all_db_data:
            iterator += 1
            notification_arr.append(
                {
                    "id": item[0],
                    "event_type": item[1],
                    "event_description": item[2],
                    "read_flag": item[4],
                    "created_at": item[5],
                }
            )

            if iterator == 3:
                break

        response["data"] = notification_arr

    return jsonify(response), 200


@notification.route("/unread-count-notifications", methods=["GET"])
def fetch_unread_count_notifications_for_user():

    user_id = request.args.get("user_id")

    cursor = conn.cursor()
    affected_count = 0

    selectQuery = (
        "SELECT COUNT(*) FROM user_notifications WHERE user_id = %s AND read_flag = 0"
    )
    try:
        cursor.execute(selectQuery, (user_id,))
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
    response["status"] = "success"
    response[
        "message"
    ] = "Unread count for notifications fetched successfully for user!"
    response["unread_count"] = db_data[0]
    return jsonify(response), 200


@notification.route("/update-status-notifications", methods=["POST"])
def update_read_status_notifications_for_user():

    post_request = request.get_json(force=True)
    event_id = post_request["event_id"]
    user_id = post_request["user_id"]

    cursor = conn.cursor()
    affected_count = 0

    updateQuery = (
        "UPDATE user_notifications SET read_flag = 1 WHERE user_id = %s AND id = %s"
    )
    try:
        cursor.execute(updateQuery, (user_id, event_id))
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

    print("----------------------------------------------------")

    response = {}

    if affected_count == 0:
        response["status"] = "failure"
        response["message"] = "Failed to insert notification for user"
        return jsonify(response), 500
    else:
        response["status"] = "success"
        response["message"] = "Read status updated for notifications !"
        return jsonify(response), 200
