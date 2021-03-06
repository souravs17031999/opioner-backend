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

SENDGRID_API_KEY_PROD = os.getenv("SENDGRID_API_KEY_PROD")
SENDGRID_SENDER_EMAIL = "opinic.contact@gmail.com"

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


def send_mail(emailData, template_name):

    sender_email = SENDGRID_SENDER_EMAIL
    subject = emailData["subject"]
    receiver_email = emailData["user_email"]

    print("SENDER EMAIL : ", sender_email)
    print("RECEIVER EMAIL : ", receiver_email)
    print("Subject: ", subject)

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
        print(
            "status: failure, message: Email for newly created feeds sending failed !"
        )


# send gist of newly created feeds in last 24 hrs subscribed by followers at 07:00 PM IST
@cron_schedular.scheduled_job(trigger="cron", hour="13", minute="30", second="00")
def send_new_feeds_notification_for_creators():

    print(
        "*********************** CRON for sending notifications for newly created feeds ********************"
    )
    print("CRON TIME (UTC): ", datetime.datetime.utcnow())
    # conn = mysql.connect()
    cursor = conn.cursor()
    feedFetchQuery = "SELECT t.user_id, t.description, t.created_at, t.likes, t.comments, u.subscribed_by, u.username, u.firstname FROM task_list t \
    INNER JOIN users u \
    ON t.user_id=u.user_id \
    WHERE DATE_PART('day', NOW() - t.created_at) = 0 AND privacy = 'public' AND is_flagged = 0 AND u.subscriber_count > 0"
    cursor.execute(feedFetchQuery)
    feeds = cursor.fetchall()
    print("----------------------------------------------------")
    print(cursor.query.decode())
    affected_count = cursor.rowcount
    print(f"{affected_count} rows affected")
    print("DB DATA : ", feeds)
    print("----------------------------------------------------")

    tz_NY = pytz.timezone("Asia/Kolkata")
    datetime_NY = datetime.datetime.now(tz_NY)
    print("DATE FOR SENDING MAILS: ", datetime_NY.strftime("%A, %d %B %Y %I:%M%p"))
    print("----------------------------------------------------")

    if len(feeds) != 0:
        user_feed_info = {}
        subscribers = set()
        for feed in feeds:
            if feed[0] in user_feed_info:
                user_feed_info[feed[0]].append(
                    {
                        "description": feed[1],
                        "created_at": feed[2],
                        "likes": feed[3],
                        "comments": feed[4],
                        "subscribed_by": feed[5],
                        "username": feed[6],
                        "firstname": feed[7],
                    }
                )
            else:
                user_feed_info[feed[0]] = [
                    {
                        "description": feed[1],
                        "created_at": feed[2],
                        "likes": feed[3],
                        "comments": feed[4],
                        "subscribed_by": feed[5],
                        "username": feed[6],
                        "firstname": feed[7],
                    }
                ]

            for id in feed[5]:
                subscribers.add(id)

        userInfoFetchQuery = (
            "SELECT u.user_id, u.firstname, u.email FROM users u WHERE user_id IN %s"
        )

        cursor.execute(userInfoFetchQuery, (tuple(subscribers),))

        user_subscribers_data = cursor.fetchall()

        print("----------------------------------------------------")
        print(cursor.query.decode())
        affected_count = cursor.rowcount
        print(f"{affected_count} rows affected")
        print("DB DATA : ", user_subscribers_data)
        print("----------------------------------------------------")

        subscribers_email_data = {}

        for user in user_subscribers_data:
            subscribers_email_data[user[0]] = {"name": user[1], "email": user[2]}

        for user_id, user_data in user_feed_info.items():
            emailData = {}
            for subscriber_id in user_data[0]["subscribed_by"]:

                emailData[
                    "subject"
                ] = f"Hi {subscribers_email_data[subscriber_id]['name']}, Top opinions only for you by your favourite creators"
                emailData["user_email"] = subscribers_email_data[subscriber_id]["email"]
                emailData["mail_content"] = {"feeds": []}
                for feed in user_data:
                    emailData["mail_content"]["feeds"].append(
                        {
                            "created_by_username": feed["username"],
                            "created_by_firstname": feed["firstname"],
                            "created_at": feed["created_at"],
                            "description": feed["description"],
                            "likes": feed["likes"],
                            "comments": feed["comments"],
                        }
                    )

                send_mail(emailData, "feeds.html")

    else:
        print("============= NO NEW FEEDS FOUND IN LAST 24 HOURS =================")

    cursor.close()


# set flag status for comments every 5 min if flagged count > 5
@cron_schedular.scheduled_job(trigger="interval", minutes=5)
def set_flag_status_for_comments():

    print(
        "******************* CRON for setting flag status for comments ********************"
    )
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
        conn.rollback()

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
                conn.rollback()

    print("----------------------------------------------------")
    cursor.close()


# set flag status for public feed every 8 min if flagged count > 5
@cron_schedular.scheduled_job(trigger="interval", minutes=8)
def set_flag_status_for_feeds():

    print(
        "***************** CRON for setting flag status for feeds *******************"
    )
    affected_count = 0
    TOTAL_FLAGGED_FEEDS_CONSTRAINT = 5
    cursor = conn.cursor()
    fetchAllFeedsquery = "SELECT * FROM task_list"
    feed_data = None
    try:
        cursor.execute(fetchAllFeedsquery)
        affected_count = cursor.rowcount
        feed_data = cursor.fetchall()
        print("----------------------------------------------------")
        print(cursor.query.decode())
        print(f"{affected_count} rows affected")
        print("DB DATA : ", feed_data)

    except Exception as e:
        print(e)
        conn.rollback()

    updateFlagStatusQuery = "UPDATE task_list SET is_flagged = 1 WHERE task_id = %s"
    # mark flag status only if not marked already, unflag should be manually done
    for feed in feed_data:
        if len(feed[10]) > TOTAL_FLAGGED_FEEDS_CONSTRAINT and not feed[9]:
            try:
                cursor.execute(updateFlagStatusQuery, (feed[0],))
                conn.commit()
                affected_count = cursor.rowcount
                print(cursor.query.decode())
                print(f"{affected_count} rows affected")

            except Exception as e:
                print(e)
                conn.rollback()

    print("----------------------------------------------------")
    cursor.close()


cron_schedular.start()
