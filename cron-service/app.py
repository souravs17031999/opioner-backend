from flask import Flask, json, jsonify, request, Response, render_template
from apscheduler.schedulers.blocking import BlockingScheduler
import datetime
import json
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from utils.log_util import get_logger
import logging

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

import datetime
import jinja2
import os
import psycopg2
import pytz

app = Flask(__name__)
logger = get_logger(__name__)

DATABASE_URL = f"postgres://{os.getenv('PGUSER')}:{os.getenv('PGPASSWORD')}@{os.getenv('PGHOST')}/{os.getenv('PGDATABASE')}"
if os.getenv("DATABASE_URL") != "":
    DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)

SENDGRID_API_KEY_PROD = os.getenv("SENDGRID_API_KEY_PROD")
SENDGRID_SENDER_EMAIL = "opinic.contact@gmail.com"

CRON_TIME_FLAGGED_COMMENTS_MINUTES = int(os.getenv("CRON_TIME_FLAGGED_COMMENTS_MINUTES")) if os.getenv("CRON_TIME_FLAGGED_COMMENTS_MINUTES") is not None else 1
CRON_TIME_FLAGGED_FEEDS_MINUTES = int(os.getenv("CRON_TIME_FLAGGED_FEEDS_MINUTES")) if os.getenv("CRON_TIME_FLAGGED_FEEDS_MINUTES") is not None else 1
CRON_TIME_DAILY_FEED_EXP = os.getenv("CRON_TIME_DAILY_FEED_EXP") if os.getenv("CRON_TIME_DAILY_FEED_EXP") is not None and os.getenv("CRON_TIME_DAILY_FEED_EXP") != "" else "13-30-00"
CRON_TIME_DAILY_FEED_EXP_HR = CRON_TIME_DAILY_FEED_EXP.split("-")[0]
CRON_TIME_DAILY_FEED_EXP_MIN = CRON_TIME_DAILY_FEED_EXP.split("-")[1]
CRON_TIME_DAILY_FEED_EXP_SEC = CRON_TIME_DAILY_FEED_EXP.split("-")[2]

oidc_config = json.loads(os.getenv("OIDC_CONFIG"))
app.config['SERVER_URL'] = oidc_config["server_url"]
app.config['TOKEN_ISSUER'] = oidc_config["issuer"]
app.config['AUDIENCE_CLAIM'] = oidc_config["audience"]

SIGNATURE_EXPIRED = "SIGNATURE_EXPIRED"
INVALID_ISSUER = "INVALID_ISSUER"
INVALID_TOKEN = "INVALID_TOKEN"
INVALID_AUDIENCE = "INVALID_AUDIENCE"
PUBLIC_KEY_SERVER_ERROR = "PUBLIC_KEY_SERVER_ERROR"
SIGNATURE_VERIFICATION_FAILED = "SIGNATURE_VERIFICATION_FAILED"

# Instantiating the scheduler for the cronjob
cron_schedular = BlockingScheduler(timezone="Asia/Kolkata")

# generate and execute template for sending mails with dynamic vars
logger.info("Initializing CRON Schedular.... ")


def generate_mail_content(template_name, **template_vars):

    templateLoader = jinja2.FileSystemLoader(searchpath="templates")
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template(template_name)
    return template.render(**template_vars)


def send_mail(emailData, template_name):

    sender_email = SENDGRID_SENDER_EMAIL
    subject = emailData["subject"]
    receiver_email = emailData["user_email"]

    logger.info("SENDER EMAIL : %s", sender_email)
    logger.info("RECEIVER EMAIL : %s", receiver_email)
    logger.info("Subject: %s", subject)

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
        logger.info(
            "status: failure, message: Email for newly created feeds sending failed !"
        )


# send gist of newly created feeds in last 24 hrs subscribed by followers at 07:00 PM IST
@cron_schedular.scheduled_job(trigger="cron", hour=CRON_TIME_DAILY_FEED_EXP_HR, minute=CRON_TIME_DAILY_FEED_EXP_MIN, second=CRON_TIME_DAILY_FEED_EXP_SEC)
def send_new_feeds_notification_for_creators():

    logger.info(
        "*********************** CRON for sending notifications for newly created feeds ********************"
    )
    logger.info("CRON TIME (UTC): %s", datetime.datetime.utcnow())
    # conn = mysql.connect()
    cursor = conn.cursor()
    feedFetchQuery = "SELECT t.user_id, t.description, t.created_at, t.likes, t.comments, u.subscribed_by, u.username, u.firstname FROM task_list t \
    INNER JOIN users u \
    ON t.user_id=u.user_id \
    WHERE DATE_PART('day', NOW() - t.created_at) = 0 AND privacy = 'public' AND is_flagged = 0 AND u.subscriber_count > 0"
    cursor.execute(feedFetchQuery)
    feeds = cursor.fetchall()
    logger.info("----------------------------------------------------")
    logger.info(cursor.query.decode())
    affected_count = cursor.rowcount
    logger.info(f"{affected_count} rows affected")
    logger.info("DB DATA : %s", feeds)
    logger.info("----------------------------------------------------")

    tz_NY = pytz.timezone("Asia/Kolkata")
    datetime_NY = datetime.datetime.now(tz_NY)
    logger.info("DATE FOR SENDING MAILS: %s", datetime_NY.strftime("%A, %d %B %Y %I:%M%p"))
    logger.info("----------------------------------------------------")

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

        logger.info("----------------------------------------------------")
        logger.info(cursor.query.decode())
        affected_count = cursor.rowcount
        logger.info(f"{affected_count} rows affected")
        logger.info("DB DATA : %s", user_subscribers_data)
        logger.info("----------------------------------------------------")

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
        logger.info("============= NO NEW FEEDS FOUND IN LAST 24 HOURS =================")

    cursor.close()


# set flag status for comments every 5 min if flagged count > 5
@cron_schedular.scheduled_job(trigger="interval", minutes=CRON_TIME_FLAGGED_COMMENTS_MINUTES)
def set_flag_status_for_comments():

    logger.info(
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
        logger.info("----------------------------------------------------")
        logger.info(cursor.query.decode())
        logger.info(f"{affected_count} rows affected")
        logger.info("DB DATA : %s", comment_data)

    except Exception as e:
        logger.info(e)
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
                logger.info(cursor.query.decode())
                logger.info(f"{affected_count} rows affected")

            except Exception as e:
                logger.info(e)
                conn.rollback()

    logger.info("----------------------------------------------------")
    cursor.close()


# set flag status for public feed every 8 min if flagged count > 5
@cron_schedular.scheduled_job(trigger="interval", minutes=CRON_TIME_FLAGGED_FEEDS_MINUTES)
def set_flag_status_for_feeds():

    logger.info(
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
        logger.info("----------------------------------------------------")
        logger.info(cursor.query.decode())
        logger.info(f"{affected_count} rows affected")
        logger.info("DB DATA : %s", feed_data)

    except Exception as e:
        logger.info(e)
        conn.rollback()

    updateFlagStatusQuery = "UPDATE task_list SET is_flagged = 1 WHERE task_id = %s"
    # mark flag status only if not marked already, unflag should be manually done
    for feed in feed_data:
        if len(feed[10]) > TOTAL_FLAGGED_FEEDS_CONSTRAINT and not feed[9]:
            try:
                cursor.execute(updateFlagStatusQuery, (feed[0],))
                conn.commit()
                affected_count = cursor.rowcount
                logger.info(cursor.query.decode())
                logger.info(f"{affected_count} rows affected")

            except Exception as e:
                logger.info(e)
                conn.rollback()

    logger.info("----------------------------------------------------")
    cursor.close()

logger.info(">>>>>>>>>>>>>> Registered Jobs <<<<<<<<<<<<<<<<<<<<")
cron_schedular.print_jobs()
logger.info(">>>>>>>>>>>>>> <<<<<<<<<<<<<<<<<<<<")
cron_schedular.start()
