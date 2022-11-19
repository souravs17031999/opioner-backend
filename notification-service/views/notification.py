from flask import Flask, json, jsonify, request, Response, Blueprint, g 
from werkzeug.datastructures import Headers

import jwt
import datetime
from functools import wraps
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import jinja2
import os
import psycopg2
import subprocess
import requests
from utils.log_util import get_logger

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

notification = Blueprint("notification", __name__)
logger = get_logger(__name__)

DATABASE_URL = f"postgres://{os.getenv('PGUSER')}:{os.getenv('PGPASSWORD')}@{os.getenv('PGHOST')}/{os.getenv('PGDATABASE')}"
if os.getenv("DATABASE_URL") != "":
    DATABASE_URL = os.getenv("DATABASE_URL")

SENDGRID_API_KEY_PROD = os.getenv("SENDGRID_API_KEY_PROD")
SENDGRID_SENDER_EMAIL = "opinic.contact@gmail.com"
SENDGRID_STATUS_API = "https://status.sendgrid.com/api/v2/summary.json"

conn = psycopg2.connect(DATABASE_URL)


def get_request_context(f):
    @wraps(f)
    def decorated_function(*args, **kws):

        loggedInUserData = g.loggedInUserData
        return f(loggedInUserData, *args, **kws)

    return decorated_function

def generate_mail_content(template_name, **template_vars):

    templateLoader = jinja2.FileSystemLoader(searchpath="templates")
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template(template_name)
    return template.render(**template_vars)


def send_sendgrid_mail(emailData, template_name):

    sender_email = SENDGRID_SENDER_EMAIL
    subject = None
    receiver_email = None
    if "subject" in emailData:
        subject = emailData["subject"]
    else:
        subject = ""
        logger.info("[WARNING]: Subject not present, sending mail with empty subject")

    if "user_email" in emailData:
        receiver_email = emailData["user_email"]
    else:
        logger.info("[WARNING]: Receiver email not found in request")
        return {
            "status": "failure",
            "message": "Email notification failed due to receiver email's not found",
        }

    logger.info("SENDER EMAIL : ", sender_email)
    logger.info("RECEIVER EMAIL : ", receiver_email)
    logger.info("Subject: ", subject)
    logger.info("EmailData: ", emailData)

    mail_body = generate_mail_content(template_name, emailData=emailData)
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
        logger.info(response.status_code)
    except Exception as e:
        logger.info(e)
        logger.info("failure !")
        return {"status": "failure", "message": "Email reminder sending failed !"}

    logger.info("success !")
    return {
        "status": "success",
        "message": "Email reminder to user send successfully !",
    }


@notification.route("/status/live", methods=["GET", "POST"])
def liveness_notification_service():
    return jsonify({
        "status" : "success", 
        "message": "This is notification-service liveness probe, service is up and running !"
        }), 200

@notification.route("/status/health", methods=["GET", "POST"])
def health_check_notification_service():

    POSTGRES_SUCCESS, APP_SUCCESS, SENDGRID_SUCCESS = True, True, True
    components_check = [
        {"postgresDB": POSTGRES_SUCCESS},
        {"application": APP_SUCCESS},
        {"sendgrid": SENDGRID_SUCCESS}
    ]
    try:
        subprocess_output = subprocess.run(["pg_isready", "-h", f"{os.getenv('PGHOST')}"])
        if subprocess_output.returncode != 0:
            POSTGRES_SUCCESS = False
    except Exception as e:
        logger.info(e)

    try:
        logger.info(
            "[debug] Requesting to SendGrid: %s",
            SENDGRID_STATUS_API,
        )
        sendgridResponse = requests.get(
            SENDGRID_STATUS_API,
            timeout=10,
        )
        logger.info("[debug] sendgrid-service status: %s", sendgridResponse)
        logger.info("[debug] sendgrid-service response: %s", sendgridResponse.text)
        if sendgridResponse.status_code != 200 or (sendgridResponse.components[0].name == "Mail Sending" and sendgridResponse.components[0].status != "operational"):
            SENDGRID_SUCCESS = False 
    except Exception as e:
        logger.info(e)

    return jsonify({
        "status" : "success", 
        "component_status": components_check
        }), 200

# only for Internal usage
@notification.route("/send/email", methods=["POST"])
def send_email_notifications_for_user():

    post_request = request.get_json(force=True)
    emailData = post_request["email_data"]
    templateName = post_request["template_name"]
    serviceName = post_request["service"]
    response = {}
    logger.info("====== serving for service: %s", serviceName)
    if send_sendgrid_mail(emailData, templateName)["status"] == "success":
        response["status"] = "success"
        response["message"] = "Email notifications send to user successfully !"
        return jsonify(response), 200
    else:
        response["status"] = "failure"
        response["message"] = "Failed to send email notifications !"
        return jsonify(response), 500


@notification.route("/me", methods=["POST"])
@get_request_context
def insert_notifications_for_user(loggedInUser):

    post_request = request.get_json(force=True)
    event_type = post_request["event_type"]
    event_description = post_request["event_description"]
    user_id = loggedInUser["user_id"]
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
        logger.info("----------------------------------------------------")
        logger.info(cursor.query.decode())
        logger.info(f"{affected_count} rows affected")
        db_data = cursor.fetchone()
        logger.info("DB DATA : %s", db_data)
    except Exception as e:
        logger.info(e)
    finally:
        selectQuery = "SELECT * FROM user_notifications WHERE user_id = %s"
        cursor.execute(selectQuery, (user_id,))

        affected_count = cursor.rowcount
        logger.info(cursor.query.decode())
        logger.info(f"{affected_count} rows affected")
        db_data = cursor.fetchone()
        logger.info("DB DATA : %s", db_data)

        cursor.close()

    logger.info("----------------------------------------------------")

    response = {}
    if affected_count == 0:
        response["status"] = "failure"
        response["message"] = "Failed to insert notification for user"
        return jsonify(response), 500
    else:
        response["status"] = "success"
        response["message"] = "Notification inserted successfully for user!"
        return jsonify(response), 200


@notification.route("/all", methods=["GET"])
@get_request_context
def fetch_notifications_for_user(loggedInUser):

    user_id = loggedInUser["user_id"]
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
        logger.info("----------------------------------------------------")
        logger.info(cursor.query.decode())
        logger.info(f"{affected_count} rows affected")
        all_db_data = cursor.fetchall()
        logger.info("DB DATA : %s", all_db_data)
        total_notifications = len(all_db_data)

    except Exception as e:
        logger.info(e)
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


@notification.route("/unread-count", methods=["GET"])
@get_request_context
def fetch_unread_count_notifications_for_user(loggedInUser):

    user_id = loggedInUser["user_id"]

    cursor = conn.cursor()
    affected_count = 0

    selectQuery = (
        "SELECT COUNT(*) FROM user_notifications WHERE user_id = %s AND read_flag = 0"
    )
    try:
        cursor.execute(selectQuery, (user_id,))
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

    logger.info("----------------------------------------------------")

    response = {}
    response["status"] = "success"
    response[
        "message"
    ] = "Unread count for notifications fetched successfully for user!"
    response["unread_count"] = db_data[0]
    return jsonify(response), 200


@notification.route("/status", methods=["PUT"])
@get_request_context
def update_read_status_notifications_for_user(loggedInUser):

    post_request = request.get_json(force=True)
    event_id = post_request["event_id"]
    user_id = loggedInUser["user_id"]

    cursor = conn.cursor()
    affected_count = 0

    updateQuery = (
        "UPDATE user_notifications SET read_flag = 1 WHERE user_id = %s AND id = %s"
    )
    try:
        cursor.execute(updateQuery, (user_id, event_id))
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

    logger.info("----------------------------------------------------")

    response = {}

    if affected_count == 0:
        response["status"] = "failure"
        response["message"] = "Failed to insert notification for user"
        return jsonify(response), 500
    else:
        response["status"] = "success"
        response["message"] = "Read status updated for notifications !"
        return jsonify(response), 200
