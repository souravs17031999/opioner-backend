from flask import Flask, json, jsonify, request, Response, render_template
from apscheduler.schedulers.blocking import BlockingScheduler
import datetime
import json
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# from flaskext.mysql import MySQL
import datetime
import jinja2
import os
import psycopg2
import pytz

app = Flask(__name__)
DATABASE_URL = f"postgres://{os.getenv('PGUSER')}:{os.getenv('PGPASSWORD')}@{os.getenv('PGHOST')}/{os.getenv('PGDATABASE')}"
if os.getenv("DATABASE_URL") != "":
    DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)

# Instantiating the scheduler for the cronjob
cron_schedular = BlockingScheduler()

# # Defining a cronjob function to run alongside the Flask app
# mysql = MySQL()
# app.config['MYSQL_DATABASE_USER'] = os.getenv('MYSQL_DATABASE_USER')
# app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('MYSQL_DATABASE_PASSWORD')
# app.config['MYSQL_DATABASE_DB'] = os.getenv('MYSQL_DATABASE_DB')
# app.config['MYSQL_DATABASE_HOST'] = os.getenv('MYSQL_DATABASE_HOST')
# app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# mysql.init_app(app)

# generate and execute template for sending mails with dynamic vars
print("Initializing CRON Schedular.... ")


def generate_mail_content(template_name, **template_vars):

    templateLoader = jinja2.FileSystemLoader(searchpath="templates")
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template(template_name)
    return template.render(**template_vars)


# send reminder mails to user for subscribed task on 09:00 AM IST
@cron_schedular.scheduled_job(trigger="cron", hour="14", minute="54", second="00")
def send_email_notification_to_user():

    print("CRON for sending morning IST reminder mails ....")
    print("CRON TIME (UTC): ", datetime.datetime.utcnow())
    # conn = mysql.connect()
    cursor = conn.cursor()
    query = "SELECT u.firstname, u.email, t.description, t.status_tag FROM users u INNER JOIN task_list t ON t.user_id = u.user_id WHERE t.is_email_pushed = 1"
    cursor.execute(query)
    db_data = cursor.fetchall()
    cursor.close()
    print("----------------------------------------------------")
    print(cursor.query.decode())
    affected_count = cursor.rowcount
    print(f"{affected_count} rows affected")
    print("DB DATA : ", db_data)
    print("----------------------------------------------------")

    sender_email = "taskly.contact@gmail.com"
    subject = "Reminder for your task on Taskly - let's do it !"
    print("SENDER EMAIL : ", sender_email)
    print("Subject: ", subject)
    tz_NY = pytz.timezone("Asia/Kolkata")
    datetime_NY = datetime.datetime.now(tz_NY)
    print("DATE FOR SENDING MAILS: ", datetime_NY.strftime("%A, %d %B %Y %I:%M%p"))
    print("----------------------------------------------------")

    for item in db_data:

        if item[1] != "":
            print(f"Sending mail for: {item[0]} at {item[1]}")

            mail_body = generate_mail_content(
                "reminder_email.html",
                firstname=item[0],
                date=datetime_NY.strftime("%A, %d %B %Y %I:%M%p"),
                description=item[2],
                tag=item[3],
            )

            message = Mail(
                from_email=sender_email,
                to_emails=item[1],
                subject=subject,
                html_content=mail_body,
            )

            try:
                sendgridAPIClientKey = os.getenv("SENDGRID_API_KEY_PROD")
                sg = SendGridAPIClient(sendgridAPIClientKey)
                response = sg.send(message)
                print(response.status_code)
            except Exception as e:
                print(e)
                print(e.body)
                print(e.message)
                print("failure !")

            print("success !")

    cursor.close()


# set flag status for comments every 5 min if flagged count > 5
@cron_schedular.scheduled_job(trigger="interval", minutes=5)
def set_flag_status_for_comments():

    print("CRON for setting flag status for comments ....")
    affected_count = 0
    TOTAL_FLAGGED_COMMENT_CONSTRAINT = 5
    cursor = conn.cursor()
    fetchAllCommentsquery = "SELECT * FROM feed_tracking_comments"
    comment_data = None
    try:
        cursor.execute(fetchAllCommentsquery)
        affected_count = cursor.rowcount
        comment_data = cursor.fetchall()
        print("----------------------------------------------------")
        print(cursor.query.decode())
        print(f"{affected_count} rows affected")
        print("DB DATA : ", comment_data)

    except Exception as e:
        print(e)

    updateFlagStatusQuery = (
        "UPDATE feed_tracking_comments SET is_flagged = 1 WHERE comment_id = %s"
    )
    # mark flag status only if not marked already, unflag should be manually done
    for comment in comment_data:
        if len(comment[9]) > TOTAL_FLAGGED_COMMENT_CONSTRAINT and not comment[6]:
            try:
                cursor.execute(updateFlagStatusQuery, (comment[0],))
                conn.commit()
                affected_count = cursor.rowcount
                print(cursor.query.decode())
                print(f"{affected_count} rows affected")

            except Exception as e:
                print(e)

    print("----------------------------------------------------")
    cursor.close()


cron_schedular.start()
