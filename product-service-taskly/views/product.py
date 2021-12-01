from flask import Flask, json, jsonify, request, Response, Blueprint
from werkzeug.datastructures import Headers

# from flaskext.mysql import MySQL
import jwt
import datetime
from functools import wraps
import os
import psycopg2
import requests


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
            if item[12] or item[13]:
                is_reminder_set = True
            else:
                is_reminder_set = False

            tasks.append(
                {
                    "id": item[8],
                    "description": item[10],
                    "status": item[11],
                    "is_reminder_set": is_reminder_set,
                    "privacy_status": item[15],
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


@product.route("/fetch-feeds", methods=["GET"])
def fetch_feed_for_user():

    user_id = request.args.get("user_id")

    if user_id == "null" or user_id is None:
        return (
            jsonify(
                {
                    "status": "failure",
                    "message": "unauthorized request to fetch feeds for the user !",
                }
            ),
            401,
        )

    page = request.args.get("page")
    size = request.args.get("size")
    if page is None:
        page = 1
    if size is None:
        size = 10
    skip = (int(page) - 1) * int(size)
    select_query = "SELECT u.username, u.firstname, t.list_id, t.description, t.created_at, t.likes, t.comments FROM task_list t INNER JOIN users u ON t.user_id = u.user_id WHERE t.privacy = %s ORDER BY t.created_at DESC OFFSET %s LIMIT %s"
    cursor = conn.cursor()
    affected_count = 0

    try:
        cursor.execute(
            select_query,
            (
                "public",
                skip,
                size,
            ),
        )
        affected_count = cursor.rowcount
        db_data_feeds = cursor.fetchall()
        print("----------------------------------------------------")
        print(cursor.query.decode())
        print(f"{affected_count} rows affected")
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        if affected_count == 0:
            cursor.close()

    print("DB DATA : ", db_data_feeds)

    print("----------------------------------------------------")

    response = {}
    lists = []

    if affected_count == 0:
        response["status"] = "failure"
        response["message"] = "Empty feed for the user !"
        return jsonify(response), 404
    else:
        # get all the feeds created by user itself and liked
        select_events_likes_for_user = (
            "SELECT list_id FROM task_list WHERE user_id = %s AND has_liked = 1"
        )
        select_comments_likes_for_user = (
            "SELECT list_id FROM task_list WHERE user_id = %s AND has_commented = 1"
        )
        db_data_likes_ids = None
        db_data_comments_ids = None
        db_data_all_likes_ids = None
        try:
            cursor.execute(select_events_likes_for_user, (user_id,))
            affected_count = cursor.rowcount
            db_data_likes_ids = cursor.fetchall()
            print(cursor.query.decode())
            print(f"{affected_count} rows affected")
            conn.commit()
        except Exception as e:
            print(e)

        try:
            cursor.execute(select_comments_likes_for_user, (user_id,))
            affected_count = cursor.rowcount
            db_data_comments_ids = cursor.fetchall()
            print(cursor.query.decode())
            print(f"{affected_count} rows affected")
            conn.commit()
        except Exception as e:
            print(e)

        # get all the feeds which user has liked but not created by itself
        select_all_events_likes_for_user = "SELECT list_id FROM feed_tracking_user_status WHERE user_id = %s AND liked = 1"

        try:
            cursor.execute(select_all_events_likes_for_user, (user_id,))
            affected_count = cursor.rowcount
            db_data_all_likes_ids = cursor.fetchall()
            print(cursor.query.decode())
            print(f"{affected_count} rows affected")
            conn.commit()
        except Exception as e:
            print(e)

        for i in db_data_all_likes_ids:
            db_data_likes_ids.append(i)

        print("[debug]: likes ids: ", db_data_likes_ids)
        start_param_for_page = 1
        if page is not None and size is not None:
            start_param_for_page = skip + 1

        for iter, item in enumerate(db_data_feeds, start=start_param_for_page):

            has_liked = False
            has_commented = False
            for id in db_data_likes_ids:
                if id[0] == item[2]:
                    has_liked = True

            for id in db_data_comments_ids:
                if id[0] == item[2]:
                    has_commented = True

            lists.append(
                {
                    "id": iter,
                    "username": item[0],
                    "firstname": item[1],
                    "list_id": item[2],
                    "description": item[3],
                    "created_at": item[4],
                    "likes": item[5],
                    "comments": item[6],
                    "has_liked": has_liked,
                    "has_commented": has_commented,
                }
            )

        response["status"] = "success"
        response["message"] = "All public feeds for user fetched successfully !"
        response["feeds"] = lists
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
    privacy = post_request.get("privacy_status")
    user_email = post_request.get("email")

    if post_request.get("reminder_set"):
        is_email_pushed = 1
    else:
        is_email_pushed = 0

    task_status = post_request.get("status")

    db_data = None
    response = {}

    if post_request["update_flag"] == 0:
        query = (
            "INSERT INTO task_list(user_id, description, privacy) VALUES(%s, %s, %s)"
        )
        PRIVACY_STATUS = "private"

        if privacy is not None:
            query = "INSERT INTO task_list(user_id, description, privacy) VALUES(%s, %s, %s)"
            PRIVACY_STATUS = privacy

        try:
            affected_count = cursor.execute(
                query,
                (
                    user_id,
                    description,
                    PRIVACY_STATUS,
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

        if affected_count == 0:
            response["status"] = "failure"
            response["message"] = "Task insertion for user failed !"
            return jsonify(response), 500
        else:
            if db_data is not None:
                response["id"] = db_data[0]
                response["status_tag"] = db_data[3]
            response["status"] = "success"
            response["message"] = "INSERTION for User tasks SUCCESFULLY DONE !"
            return jsonify(response), 200

    else:

        # check notification status and send notification if required, then update other fields
        check_notification_status_user = (
            "SELECT is_email_pushed FROM task_list WHERE user_id = %s AND list_id = %s"
        )
        user_notification_already_set = 0
        try:
            cursor.execute(
                check_notification_status_user,
                (
                    user_id,
                    list_id,
                ),
            )
            affected_count = cursor.rowcount
            db_data_notification = cursor.fetchone()
            print("DB DATA: ", db_data_notification)
            print(cursor.query.decode())
            print(f"{affected_count} rows affected")
            user_notification_already_set = db_data_notification[0]
            conn.commit()
        except Exception as e:
            print(e)

        # user input and db data doesnot match, meaning we are good for sending notifications
        if user_notification_already_set != is_email_pushed:

            if is_email_pushed and user_email is not None:
                payload = {
                    "user_id": user_id,
                    "email": user_email,
                    "phone": "123456",
                    "list_id": list_id,
                }
                notifyServiceReply = requests.post(
                    "http://notification_service:8084/notification/subscribe-notification",
                    json=payload,
                )
                jsonifiedReply = notifyServiceReply.json()
                if jsonifiedReply["status"] != "success":
                    response["status"] = "failure"
                    response[
                        "message"
                    ] = "Error while suscribing user to notifications, INSERTION/UPDATION FAILED !"
                    return jsonify(response), 500
            else:
                payload = {
                    "user_id": user_id,
                    "email": user_email,
                    "phone": "123456",
                    "list_id": list_id,
                }
                notifyServiceReply = requests.post(
                    "http://notification_service:8084/notification/unsubscribe-notification",
                    json=payload,
                )
                jsonifiedReply = notifyServiceReply.json()
                if jsonifiedReply["status"] != "success":
                    response["status"] = "failure"
                    response[
                        "message"
                    ] = "Error while suscribing user to notifications, INSERTION/UPDATION FAILED !"
                    return jsonify(response), 500

        update_query = "UPDATE task_list SET description = %s, privacy = %s, is_email_pushed = %s, status_tag = %s WHERE user_id = %s AND list_id = %s"

        try:
            affected_count = cursor.execute(
                update_query,
                (
                    description,
                    privacy,
                    is_email_pushed,
                    task_status,
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

        if affected_count == 0:
            response["status"] = "failure"
            response["message"] = "Task Updation for user failed !"
            return jsonify(response), 500
        else:
            response["status"] = "success"
            response["message"] = "Updation for User tasks SUCCESFULLY DONE !"
            return jsonify(response), 200

    print("----------------------------------------------------")


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


@product.route("/update-feedtask-status", methods=["POST"])
def update_user_task_status():

    post_request = request.get_json(force=True)
    user_id = post_request["user_id"]
    list_id = post_request["list_id"]
    clicked_event_type = post_request["update_status_event"]
    has_deleted_comment = post_request.get("has_deleted_comment")

    # conn = mysql.connect()
    cursor = conn.cursor()
    affected_count = 0

    if clicked_event_type == "like_event":

        selectUserForCalledListQuery = (
            "SELECT user_id, has_liked FROM task_list WHERE list_id = %s"
        )
        db_user_id = None
        has_liked = None
        try:
            cursor.execute(
                selectUserForCalledListQuery,
                (list_id,),
            )
            conn.commit()
            affected_count = cursor.rowcount
            db_data = cursor.fetchone()
            print("DB DATA: ", db_data)
            db_user_id = db_data[0]
            has_liked = db_data[1]
            print("----------------------------------------------------")
            print(cursor.query.decode())
            print(f"{affected_count} rows affected")

        except Exception as e:
            print(e)

        if user_id == db_user_id:
            # when the user liking is same as who created that feed
            print("[debug]: Called by same user for like ")
            updateLikeCountQuery = ""
            updateStatusQuery = ""
            if has_liked:
                updateLikeCountQuery = (
                    "UPDATE task_list SET likes = likes - 1 WHERE list_id = %s"
                )

                updateStatusQuery = "UPDATE task_list SET has_liked = 0 WHERE list_id = %s AND user_id = %s"

            else:

                updateLikeCountQuery = (
                    "UPDATE task_list SET likes = likes + 1 WHERE list_id = %s"
                )

                updateStatusQuery = "UPDATE task_list SET has_liked = 1 WHERE list_id = %s AND user_id = %s"

            try:
                cursor.execute(
                    updateLikeCountQuery,
                    (list_id,),
                )
                conn.commit()
                affected_count = cursor.rowcount
                print(cursor.query.decode())
                print(f"{affected_count} rows affected")

            except Exception as e:
                print(e)

            try:
                cursor.execute(
                    updateStatusQuery,
                    (
                        list_id,
                        user_id,
                    ),
                )
                conn.commit()
                affected_count = cursor.rowcount
                print(cursor.query.decode())
                print(f"{affected_count} rows affected")

            except Exception as e:
                print(e)
            finally:
                cursor.close()

        else:
            # when the user liking is not same as who created that feed
            selectFeedStatusQuery = "SELECT * FROM feed_tracking_user_status WHERE list_id = %s AND user_id = %s"
            try:
                cursor.execute(
                    selectFeedStatusQuery,
                    (
                        list_id,
                        user_id,
                    ),
                )
                conn.commit()
                selected_feed_status_count = cursor.rowcount
                print(cursor.query.decode())
                print(f"{selected_feed_status_count} rows affected")

            except Exception as e:
                print(e)

            updateSTatusQuery = ()
            # if user already liked this feed
            if selected_feed_status_count > 0:
                updateSTatusQuery = (
                    "UPDATE task_list SET likes = likes - 1 WHERE list_id = %s"
                )
                deleteUserFeedLikedStatusQuery = "DELETE FROM feed_tracking_user_status WHERE user_id = %s AND list_id = %s"
                try:
                    cursor.execute(
                        deleteUserFeedLikedStatusQuery,
                        (
                            user_id,
                            list_id,
                        ),
                    )
                    conn.commit()
                    affected_count = cursor.rowcount
                    print(cursor.query.decode())
                    print(f"{affected_count} rows affected")

                except Exception as e:
                    print(e)

            else:
                # if user has not liked this feed
                updateSTatusQuery = (
                    "UPDATE task_list SET likes = likes + 1 WHERE list_id = %s"
                )
                insertUserFeedLikedStatusQuery = "INSERT INTO feed_tracking_user_status(user_id, list_id, liked) VALUES(%s, %s, %s)"

                try:
                    cursor.execute(
                        insertUserFeedLikedStatusQuery,
                        (
                            user_id,
                            list_id,
                            1,
                        ),
                    )
                    conn.commit()
                    affected_count = cursor.rowcount
                    print(cursor.query.decode())
                    print(f"{affected_count} rows affected")

                except Exception as e:
                    print(e)

            # finally update the status in task_list
            try:
                cursor.execute(
                    updateSTatusQuery,
                    (list_id,),
                )
                conn.commit()
                affected_count = cursor.rowcount
                print(cursor.query.decode())
                print(f"{affected_count} rows affected")

            except Exception as e:
                print(e)
            finally:
                cursor.close()

    if clicked_event_type == "comment_event":
        updateSTatusQuery = "UPDATE task_list SET comments = comments + 1 WHERE list_id = %s AND user_id = %s"

        try:
            cursor.execute(
                updateSTatusQuery,
                (
                    list_id,
                    user_id,
                ),
            )
            conn.commit()
            affected_count = cursor.rowcount
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
        response["message"] = "Feed task status updation for like/comment failed !"
        return jsonify(response), 500
    else:
        response["status"] = "success"
        response["message"] = "Feed task status for like/comment updated !"
        return jsonify(response), 200


@product.route("/upsert-comments", methods=["POST"])
def insert_or_update_comments():

    post_request = request.get_json(force=True)
    user_id = post_request["user_id"]
    list_id = post_request["list_id"]
    comment = post_request.get("comment_text")
    is_flagged = post_request.get("is_flagged")
    comment_id = post_request.get("comment_id")
    cursor = conn.cursor()
    affected_count = 0
    created_comment_id = None
    if post_request["update_flag"] == 0:
        # insert comment for the user
        insertUserCommentsQuery = "INSERT INTO feed_tracking_comments(user_id, list_id, comment_description) VALUES(%s, %s, %s)"
        try:
            cursor.execute(
                insertUserCommentsQuery,
                (
                    user_id,
                    list_id,
                    comment,
                ),
            )
            conn.commit()
            affected_count = cursor.rowcount
            print(cursor.query.decode())
            print(f"{affected_count} rows affected")

        except Exception as e:
            print(e)

        # update the total comments
        updateSTatusQuery = (
            "UPDATE task_list SET comments = comments + 1 WHERE list_id = %s"
        )

        try:
            cursor.execute(
                updateSTatusQuery,
                (list_id,),
            )
            conn.commit()
            affected_count = cursor.rowcount
            print(cursor.query.decode())
            print(f"{affected_count} rows affected")

        except Exception as e:
            print(e)

        # fetch select query for this newly created comment
        selectCommentQuery = "SELECT comment_id FROM feed_tracking_comments WHERE user_id = %s AND comment_description = %s"

        try:
            cursor.execute(
                selectCommentQuery,
                (
                    user_id,
                    comment,
                ),
            )
            conn.commit()
            affected_count = cursor.rowcount
            new_comment = cursor.fetchone()
            created_comment_id = new_comment[0]
            print(cursor.query.decode())
            print(f"{affected_count} rows affected")

        except Exception as e:
            print(e)

        finally:
            cursor.close()

    else:

        if is_flagged is None:
            # update comment query
            updateUserCommentsQuery = "UPDATE feed_tracking_comments SET comment_description = %s WHERE comment_id = %s"
            try:
                cursor.execute(
                    updateUserCommentsQuery,
                    (
                        comment,
                        comment_id,
                    ),
                )
                conn.commit()
                affected_count = cursor.rowcount
                print(cursor.query.decode())
                print(f"{affected_count} rows affected")

            except Exception as e:
                print(e)

            finally:
                cursor.close()

        if is_flagged is not None:
            # flag comment query
            updateUserCommentsQuery = "UPDATE feed_tracking_comments SET flag_on_comments = flag_on_comments + 1, flagged_by = array_append(flagged_by, %s) WHERE comment_id = %s"
            try:
                cursor.execute(
                    updateUserCommentsQuery,
                    (
                        user_id,
                        comment_id,
                    ),
                )
                conn.commit()
                affected_count = cursor.rowcount
                print(cursor.query.decode())
                print(f"{affected_count} rows affected")

            except Exception as e:
                print(e)

            finally:
                cursor.close()

    response = {}
    if affected_count == 0:
        response["status"] = "failure"
        response["message"] = "User comments insertion/updation failed !"
        return jsonify(response), 500
    else:
        response["status"] = "success"
        response["message"] = "User comments inserted/updated successfully !"
        response["comment"] = {"comment_id": created_comment_id}
        return jsonify(response), 200


@product.route("/delete-comments", methods=["POST"])
def delete_comments_for_user():

    post_request = request.get_json(force=True)
    user_id = post_request["user_id"]
    list_id = post_request["list_id"]
    comment_id = post_request["comment_id"]

    cursor = conn.cursor()
    affected_count = 0

    deleteUserCommentsQuery = (
        "DELETE FROM feed_tracking_comments WHERE comment_id = %s AND user_id = %s"
    )
    try:
        cursor.execute(
            deleteUserCommentsQuery,
            (
                comment_id,
                user_id,
            ),
        )
        conn.commit()
        affected_count = cursor.rowcount
        print(cursor.query.decode())
        print(f"{affected_count} rows affected")

    except Exception as e:
        print(e)

    # update the total comments
    updateSTatusQuery = (
        "UPDATE task_list SET comments = comments - 1 WHERE list_id = %s"
    )

    try:
        cursor.execute(
            updateSTatusQuery,
            (list_id,),
        )
        conn.commit()
        affected_count = cursor.rowcount
        print(cursor.query.decode())
        print(f"{affected_count} rows affected")

    except Exception as e:
        print(e)

    finally:
        cursor.close()

    response = {}
    if affected_count == 0:
        response["status"] = "failure"
        response["message"] = "User comments deletion failed !"
        return jsonify(response), 500
    else:
        response["status"] = "success"
        response["message"] = "User comments deleted successfully !"
        return jsonify(response), 200


@product.route("/fetch-all-comments", methods=["GET"])
def fetch_comments_for_user():

    user_id = request.args.get("user_id")
    list_id = request.args.get("list_id")
    cursor = conn.cursor()
    affected_count = 0

    page = request.args.get("page")
    size = request.args.get("size")
    if page is None:
        page = 1
    if size is None:
        size = 2
    skip = (int(page) - 1) * int(size)

    fetchAllUserCommentsQuery = "SELECT ftc.comment_id, ftc.comment_description, ftc.created_at, u.username FROM feed_tracking_comments ftc INNER JOIN users u ON ftc.user_id = u.user_id WHERE ftc.list_id = %s AND is_flagged = 0 ORDER BY ftc.created_at DESC OFFSET %s LIMIT %s"
    db_data = None
    try:
        cursor.execute(
            fetchAllUserCommentsQuery,
            (
                list_id,
                skip,
                size,
            ),
        )
        conn.commit()
        affected_count = cursor.rowcount
        db_data = cursor.fetchall()
        print("DB DATA: ", db_data)
        print(cursor.query.decode())
        print(f"{affected_count} rows affected")

    except Exception as e:
        print(e)

    finally:
        cursor.close()

    commentsData = []
    for comment in db_data:
        commentsData.append(
            {
                "comment_id": comment[0],
                "comment_text": comment[1],
                "created_at": comment[2],
                "username": comment[3],
            }
        )

    response = {}
    if affected_count == 0:
        response["status"] = "failure"
        response["message"] = "Found empty comments for user !"
        return jsonify(response), 404
    else:
        response["status"] = "success"
        response["message"] = "All user comments fetched successfully !"
        response["comments"] = commentsData
        return jsonify(response), 200
