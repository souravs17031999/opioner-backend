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
import subprocess
import requests

app = Flask(__name__)

# mysql = MySQL()
# app.config['MYSQL_DATABASE_USER'] = os.getenv('MYSQL_DATABASE_USER')
# app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('MYSQL_DATABASE_PASSWORD')
# app.config['MYSQL_DATABASE_DB'] = os.getenv('MYSQL_DATABASE_DB')
# app.config['MYSQL_DATABASE_HOST'] = os.getenv('MYSQL_DATABASE_HOST')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# mysql.init_app(app)

notification = Blueprint("notification", __name__)
DATABASE_URL = f"postgres://{os.getenv('PGUSER')}:{os.getenv('PGPASSWORD')}@{os.getenv('PGHOST')}/{os.getenv('PGDATABASE')}"
if os.getenv("DATABASE_URL") != "":
    DATABASE_URL = os.getenv("DATABASE_URL")

SENDGRID_API_KEY_PROD = os.getenv("SENDGRID_API_KEY_PROD")
SENDGRID_SENDER_EMAIL = "opinic.contact@gmail.com"
SENDGRID_STATUS_API = "https://status.sendgrid.com/api/v2/summary.json"

conn = psycopg2.connect(DATABASE_URL)


def decode_auth_token(auth_token):
    """
    Decodes the auth token
    :param auth_token:
    :return: integer|string
    """
    try:
        payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'), algorithms='HS256')
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'

def authorize(f):
    @wraps(f)
    def decorated_function(*args, **kws):

        cursor = conn.cursor()
        
        request_user_id = -1

        try:
            if 'Authorization' in request.headers:
                print("[debug]: Got token, Decoding JWT token.... ", request.headers['Authorization'])
                split_token = request.headers['Authorization'].split(" ")
                if split_token[0] == "Bearer":
                    authToken = decode_auth_token(split_token[1])
                else:
                    print("[Error]: Token not in valid format")
                print("[debug]: decode token=> ", authToken)
                request_user_id = authToken["user-id"]
        except Exception as e:
            print(e)
            return (
                jsonify(
                    {
                        "status": "failure",
                        "message": "Unauthorized request !, Token is Expired or Invalid !",
                    }
                ),
                401,
            )

        if request_user_id == -1:
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
        }

        return f(loggedInUser, *args, **kws)

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
        print("[WARNING]: Subject not present, sending mail with empty subject")

    if "user_email" in emailData:
        receiver_email = emailData["user_email"]
    else:
        print("[WARNING]: Receiver email not found in request")
        return {
            "status": "failure",
            "message": "Email notification failed due to receiver email's not found",
        }

    print("SENDER EMAIL : ", sender_email)
    print("RECEIVER EMAIL : ", receiver_email)
    print("Subject: ", subject)
    print("EmailData: ", emailData)

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
        print(response.status_code)
    except Exception as e:
        print(e)
        print("failure !")
        return {"status": "failure", "message": "Email reminder sending failed !"}

    print("success !")
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
        print(e)

    try:
        print(
            "[debug] Requesting to SendGrid: ",
            SENDGRID_STATUS_API,
        )
        sendgridResponse = requests.get(
            SENDGRID_STATUS_API,
            timeout=10,
        )
        print("[debug] sendgrid-service status: ", sendgridResponse)
        print("[debug] sendgrid-service response: ", sendgridResponse.text)
        if sendgridResponse.status_code != 200 or (sendgridResponse.components[0].name == "Mail Sending" and sendgridResponse.components[0].status != "operational"):
            SENDGRID_SUCCESS = False 
    except Exception as e:
        print(e)

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
    print("====== serving for service: ", serviceName)
    if send_sendgrid_mail(emailData, templateName)["status"] == "success":
        response["status"] = "success"
        response["message"] = "Email notifications send to user successfully !"
        return jsonify(response), 200
    else:
        response["status"] = "failure"
        response["message"] = "Failed to send email notifications !"
        return jsonify(response), 500


@notification.route("/me", methods=["POST"])
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


@notification.route("/all", methods=["GET"])
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


@notification.route("/unread-count", methods=["GET"])
@authorize
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


@notification.route("/status", methods=["PUT"])
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
