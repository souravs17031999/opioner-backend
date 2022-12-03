from flask import Flask, jsonify, request, Blueprint, g

from functools import wraps
import os
import psycopg2
import subprocess
from utils.log_util import get_logger

app = Flask(__name__)

product = Blueprint("product", __name__)
logger = get_logger(__name__)

DATABASE_URL = f"postgres://{os.getenv('PGUSER')}:{os.getenv('PGPASSWORD')}@{os.getenv('PGHOST')}/{os.getenv('PGDATABASE')}"
if os.getenv("DATABASE_URL") != "":
    DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)

@product.route("/status/live", methods=["GET", "POST"])
def liveness_product_service():
    return jsonify({
        "status" : "success", 
        "message": "This is product-service liveness probe, service is up and running !"
        }), 200

@product.route("/status/health", methods=["GET", "POST"])
def health_check_product_service():

    POSTGRES_SUCCESS, APP_SUCCESS = True, True
    components_check = [
        {"postgresDB": POSTGRES_SUCCESS},
        {"application": APP_SUCCESS}
    ]

    try:
        subprocess_output = subprocess.run(["pg_isready", "-h", f"{os.getenv('PGHOST')}"])
        if subprocess_output.returncode != 0:
            POSTGRES_SUCCESS = False
    except Exception as e:
        logger.info(e)

    return jsonify({
        "status" : "success", 
        "component_status": components_check
        }), 200

def get_request_context(f):
    @wraps(f)
    def decorated_function(*args, **kws):

        loggedInUserData = g.loggedInUserData
        return f(loggedInUserData, *args, **kws)

    return decorated_function


@product.route("/my/feed", methods=["GET"])
@get_request_context
def fetch_user_list(loggedInUser):

    # conn = mysql.connect()
    cursor = conn.cursor()

    fetchQuery = "SELECT t.* FROM task_list t WHERE t.user_id = %s"

    affected_count = 0
    db_list_data = None
    try:
        cursor.execute(fetchQuery, (loggedInUser["user_id"],))
        affected_count = cursor.rowcount
        db_list_data = cursor.fetchall()
        logger.info("----------------------------------------------------")
        logger.info(cursor.query.decode())
        logger.info(f"{affected_count} rows affected")
        conn.commit()
    except Exception as e:
        logger.error(e)
    finally:
        cursor.close()

    logger.info("DB DATA : %s", db_list_data)
    logger.info("----------------------------------------------------")

    response = {}

    if affected_count == 0:
        response["status"] = "failure"
        response["message"] = "Empty lists for given user !"
        return jsonify(response), 200

    else:
        tasks = []
        for item in db_list_data:
            tasks.append(
                {
                    "id": item[0],
                    "description": item[2],
                    "privacy_status": item[4],
                }
            )

        response["status"] = "success"
        response["task"] = tasks

        return jsonify(response), 200


@product.route("/public/feeds", methods=["GET"])
@get_request_context
def fetch_feed_for_user(loggedInUser):

    user_id = loggedInUser["user_id"]

    page = request.args.get("page")
    size = request.args.get("size")
    if page is None:
        page = 1
    if size is None:
        size = 10
    skip = (int(page) - 1) * int(size)
    select_query = "SELECT u.username, u.firstname, u.lastname, t.list_id, t.description, t.created_at, \
                    t.likes, t.comments, t.flagged_by, u.subscribed_by, u.profile_pic_url \
                    FROM task_list t \
                    INNER JOIN users u ON t.user_id = u.user_id \
                    WHERE t.privacy = %s AND t.is_flagged = %s \
                    ORDER BY t.created_at DESC OFFSET %s LIMIT %s"
    cursor = conn.cursor()
    affected_count = 0

    try:
        cursor.execute(
            select_query,
            (
                "public",
                0,
                skip,
                size,
            ),
        )
        affected_count = cursor.rowcount
        db_data_feeds = cursor.fetchall()
        logger.info("----------------------------------------------------")
        logger.info(cursor.query.decode())
        logger.info(f"{affected_count} rows affected")
        conn.commit()
    except Exception as e:
        logger.info(e)
    finally:
        if affected_count == 0:
            cursor.close()

    logger.info("DB DATA : %s", db_data_feeds)

    logger.info("----------------------------------------------------")

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
            logger.info(cursor.query.decode())
            logger.info(f"{affected_count} rows affected")
            conn.commit()
        except Exception as e:
            logger.info(e)

        try:
            cursor.execute(select_comments_likes_for_user, (user_id,))
            affected_count = cursor.rowcount
            db_data_comments_ids = cursor.fetchall()
            logger.info(cursor.query.decode())
            logger.info(f"{affected_count} rows affected")
            conn.commit()
        except Exception as e:
            logger.info(e)

        # get all the feeds which user has liked but not created by itself
        select_all_events_likes_for_user = "SELECT list_id FROM feed_tracking_user_status WHERE user_id = %s AND liked = 1"

        try:
            cursor.execute(select_all_events_likes_for_user, (user_id,))
            affected_count = cursor.rowcount
            db_data_all_likes_ids = cursor.fetchall()
            logger.info(cursor.query.decode())
            logger.info(f"{affected_count} rows affected")
            conn.commit()
        except Exception as e:
            logger.info(e)

        for i in db_data_all_likes_ids:
            db_data_likes_ids.append(i)

        logger.info("[debug]: likes ids: %s", db_data_likes_ids)
        start_param_for_page = 1
        if page is not None and size is not None:
            start_param_for_page = skip + 1

        for iter, item in enumerate(db_data_feeds, start=start_param_for_page):

            has_liked = False
            has_commented = False
            for id in db_data_likes_ids:
                if id[0] == item[3]:
                    has_liked = True

            for id in db_data_comments_ids:
                if id[0] == item[3]:
                    has_commented = True

            hasUserFlaggedThePost = False
            flaggedByUsersList = item[8]
            for id in flaggedByUsersList:
                if id == user_id:
                    hasUserFlaggedThePost = True

            hasUserSubscribedThisCreator = False
            subscribedByUsersList = item[9]
            for id in subscribedByUsersList:
                if id == user_id:
                    hasUserSubscribedThisCreator = True

            lists.append(
                {
                    "id": iter,
                    "username": item[0],
                    "firstname": item[1],
                    "lastname": item[2],
                    "list_id": item[3],
                    "description": item[4],
                    "created_at": item[5],
                    "likes": item[6],
                    "comments": item[7],
                    "has_liked": has_liked,
                    "has_commented": has_commented,
                    "is_flagged": hasUserFlaggedThePost,
                    "has_subscribed": hasUserSubscribedThisCreator,
                    "profile_pic_url_creator": item[10],
                }
            )

        response["status"] = "success"
        response["message"] = "All public feeds for user fetched successfully !"
        response["feeds"] = lists
        return jsonify(response), 200


@product.route("/feed/upsert", methods=["POST"])
@get_request_context
def submit_or_update_user_post(loggedInUser):

    post_request = request.get_json(force=True)

    # conn = mysql.connect()
    cursor = conn.cursor()
    affected_count = 0
    user_id = loggedInUser["user_id"]
    description = post_request["item"]
    list_id = post_request.get("id")
    privacy = post_request.get("privacy_status")

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
            logger.info("----------------------------------------------------")
            logger.info(cursor.query.decode())
            logger.info(f"{affected_count} rows affected")
            db_data = cursor.fetchone()
            logger.info("db_data: %s", db_data)

        except Exception as e:
            logger.info(e)
        finally:
            selectQuery = (
                "SELECT * FROM task_list WHERE user_id = %s AND description = %s"
            )
            cursor.execute(selectQuery, (user_id, description))
            affected_count = cursor.rowcount
            db_data = cursor.fetchone()

            logger.info(cursor.query.decode())
            logger.info(f"{affected_count} rows affected")
            logger.info("db_data: %s", db_data)
            logger.info("----------------------------------------------------")

            cursor.close()

        if affected_count == 0:
            response["status"] = "failure"
            response["message"] = "Feed insertion for user failed !"
            return jsonify(response), 500
        else:
            if db_data is not None:
                response["id"] = db_data[0]
            response["status"] = "success"
            response["message"] = "INSERTION for User feed SUCCESFULLY DONE !"
            return jsonify(response), 200

    else:

        update_query = "UPDATE task_list SET description = %s, privacy = %s WHERE user_id = %s AND list_id = %s"

        try:
            affected_count = cursor.execute(
                update_query,
                (
                    description,
                    privacy,
                    user_id,
                    list_id,
                ),
            )
            conn.commit()
            affected_count = cursor.rowcount
            logger.info("----------------------------------------------------")
            logger.info(cursor.query.decode())
            logger.info(f"{affected_count} rows affected")
            db_data = cursor.fetchone()
            logger.info("db_data: %s", db_data)

        except Exception as e:
            logger.info(e)
        finally:
            cursor.close()

        if affected_count == 0:
            response["status"] = "failure"
            response["message"] = "Feed Updation for user failed !"
            return jsonify(response), 500
        else:
            response["status"] = "success"
            response["message"] = "Updation for User Feed SUCCESFULLY DONE !"
            return jsonify(response), 200

    logger.info("----------------------------------------------------")


@product.route("/my/feed", methods=["DELETE"])
@get_request_context
def delete_user_list_item(loggedInUser):

    post_request = request.get_json(force=True)
    user_id = loggedInUser["user_id"]
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
            logger.info("----------------------------------------------------")
            logger.info(cursor.query.decode())
            logger.info(f"{affected_count} rows affected")
            logger.info("----------------------------------------------------")

        except Exception as e:
            logger.info(e)
        finally:
            cursor.close()

    else:

        list_ids = list_ids.split(",")
        query = "DELETE FROM task_list WHERE user_id = %s AND list_id IN %s"
        try:
            cursor.execute(query, (user_id, list_ids))
            conn.commit()
            affected_count = cursor.rowcount
            logger.info("----------------------------------------------------")
            logger.info(cursor.query.decode())
            logger.info(f"{affected_count} rows affected")
            logger.info("----------------------------------------------------")

        except Exception as e:
            logger.info(e)
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


@product.route("/feed/status", methods=["PUT"])
@get_request_context
def update_user_task_status(loggedInUser):

    post_request = request.get_json(force=True)
    user_id = loggedInUser["user_id"]
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
            logger.info("DB DATA: %s", db_data)
            db_user_id = db_data[0]
            has_liked = db_data[1]
            logger.info("----------------------------------------------------")
            logger.info(cursor.query.decode())
            logger.info(f"{affected_count} rows affected")

        except Exception as e:
            logger.info(e)

        if user_id == db_user_id:
            # when the user liking is same as who created that feed
            logger.info("[debug]: Called by same user for like ")
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
                logger.info(cursor.query.decode())
                logger.info(f"{affected_count} rows affected")

            except Exception as e:
                logger.info(e)

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
                logger.info(cursor.query.decode())
                logger.info(f"{affected_count} rows affected")

            except Exception as e:
                logger.info(e)
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
                logger.info(cursor.query.decode())
                logger.info(f"{selected_feed_status_count} rows affected")

            except Exception as e:
                logger.info(e)

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
                    logger.info(cursor.query.decode())
                    logger.info(f"{affected_count} rows affected")

                except Exception as e:
                    logger.info(e)

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
                    logger.info(cursor.query.decode())
                    logger.info(f"{affected_count} rows affected")

                except Exception as e:
                    logger.info(e)

            # finally update the status in task_list
            try:
                cursor.execute(
                    updateSTatusQuery,
                    (list_id,),
                )
                conn.commit()
                affected_count = cursor.rowcount
                logger.info(cursor.query.decode())
                logger.info(f"{affected_count} rows affected")

            except Exception as e:
                logger.info(e)
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
            logger.info(cursor.query.decode())
            logger.info(f"{affected_count} rows affected")

        except Exception as e:
            logger.info(e)

        finally:
            cursor.close()

    logger.info("----------------------------------------------------")

    response = {}
    if affected_count == 0:
        response["status"] = "failure"
        response["message"] = "Feed task status updation for like/comment failed !"
        return jsonify(response), 500
    else:
        response["status"] = "success"
        response["message"] = "Feed task status for like/comment updated !"
        return jsonify(response), 200


@product.route("/public/comments", methods=["PUT"])
@get_request_context
def insert_or_update_comments(loggedInUser):

    post_request = request.get_json(force=True)
    user_id = loggedInUser["user_id"]
    list_id = post_request["list_id"]
    comment = post_request.get("comment_text")
    is_flagged = post_request.get("is_flagged")
    comment_id = post_request.get("comment_id")
    cursor = conn.cursor()
    affected_count = 0
    created_comment_id = None
    response = {}

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
            logger.info(cursor.query.decode())
            logger.info(f"{affected_count} rows affected")

        except Exception as e:
            logger.info(e)

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
            logger.info(cursor.query.decode())
            logger.info(f"{affected_count} rows affected")

        except Exception as e:
            logger.info(e)

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
            logger.info(cursor.query.decode())
            logger.info(f"{affected_count} rows affected")

        except Exception as e:
            logger.info(e)

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
                logger.info(cursor.query.decode())
                logger.info(f"{affected_count} rows affected")

            except Exception as e:
                logger.info(e)

            finally:
                cursor.close()

        if is_flagged is not None:
            # flag comment query
            flaggedByUsersList = []
            commentFlaggedByGetListFetchQuery = "SELECT ftc.flagged_by FROM feed_tracking_comments ftc WHERE comment_id = %s"
            try:
                cursor.execute(
                    commentFlaggedByGetListFetchQuery,
                    (comment_id,),
                )
                affected_count = cursor.rowcount
                comment_data = cursor.fetchone()
                logger.info("COMMENT_DATA: %s", comment_data)
                flaggedByUsersList = comment_data[0]
                logger.info(cursor.query.decode())
                logger.info(f"{affected_count} rows affected")

            except Exception as e:
                logger.info(e)

            # check if requested user already flagged this comment
            isCommentAlreadyFlaggedByUser = False
            for id in flaggedByUsersList:
                if id == user_id:
                    isCommentAlreadyFlaggedByUser = True

            if isCommentAlreadyFlaggedByUser:
                response["flagged_status"] = "FALSE"
                updateUserCommentsQuery = "UPDATE feed_tracking_comments SET flag_on_comments = flag_on_comments - 1, flagged_by = array_remove(flagged_by, %s) WHERE comment_id = %s"
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
                    logger.info(cursor.query.decode())
                    logger.info(f"{affected_count} rows affected")

                except Exception as e:
                    logger.info(e)

                finally:
                    cursor.close()
            else:
                response["flagged_status"] = "TRUE"
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
                    logger.info(cursor.query.decode())
                    logger.info(f"{affected_count} rows affected")

                except Exception as e:
                    logger.info(e)

                finally:
                    cursor.close()

    if affected_count == 0:
        response["status"] = "failure"
        response["message"] = "User comments insertion/updation failed !"
        return jsonify(response), 500
    else:
        response["status"] = "success"
        response["message"] = "User comments inserted/updated successfully !"
        response["comment"] = {"comment_id": created_comment_id}

        if post_request["update_flag"] == 1 and is_flagged is not None:
            if response["flagged_status"] == "TRUE":
                response[
                    "message"
                ] = "comment flagged by user ! We will soon take an action based on our internal investigation."
            else:
                response[
                    "message"
                ] = "comment unflagged by user ! Thanks for helping the community to grow."
        return jsonify(response), 200


@product.route("/comments", methods=["DELETE"])
@get_request_context
def delete_comments_for_user(loggedInUser):

    post_request = request.get_json(force=True)
    user_id = loggedInUser["user_id"]
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
        logger.info(cursor.query.decode())
        logger.info(f"{affected_count} rows affected")

    except Exception as e:
        logger.info(e)

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
        logger.info(cursor.query.decode())
        logger.info(f"{affected_count} rows affected")

    except Exception as e:
        logger.info(e)

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


@product.route("/comments", methods=["GET"])
@get_request_context
def fetch_comments_for_user(loggedInUser):

    user_id = loggedInUser["user_id"]
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

    fetchAllUserCommentsQuery = "SELECT ftc.comment_id, ftc.comment_description, ftc.created_at, ftc.flagged_by, u.username, u.firstname, u.lastname FROM feed_tracking_comments ftc INNER JOIN users u ON ftc.user_id = u.user_id WHERE ftc.list_id = %s AND is_flagged = 0 ORDER BY ftc.created_at DESC OFFSET %s LIMIT %s"
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
        logger.info("DB DATA: %s", db_data)
        logger.info(cursor.query.decode())
        logger.info(f"{affected_count} rows affected")

    except Exception as e:
        logger.info(e)

    finally:
        cursor.close()

    commentsData = []
    for comment in db_data:

        hasUserFlaggedComment = False
        flaggedByUsersList = comment[3]
        for id in flaggedByUsersList:
            if id == user_id:
                hasUserFlaggedComment = True

        commentsData.append(
            {
                "comment_id": comment[0],
                "comment_text": comment[1],
                "created_at": comment[2],
                "username": comment[4],
                "firstname": comment[5],
                "lastname": comment[6],
                "is_flagged": hasUserFlaggedComment,
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


@product.route("/feed/flag", methods=["POST"])
@get_request_context
def flag_or_report_feed_by_user(loggedInUser):

    post_request = request.get_json(force=True)
    user_id = loggedInUser["user_id"]
    list_id = post_request["list_id"]
    response = {}
    cursor = conn.cursor()
    affected_count = 0

    flaggedByUsersList = []
    feedFlaggedByUserListGetQuery = (
        "SELECT t.flagged_by FROM task_list t WHERE list_id = %s"
    )

    try:
        cursor.execute(
            feedFlaggedByUserListGetQuery,
            (list_id,),
        )
        affected_count = cursor.rowcount
        feed_data = cursor.fetchone()
        logger.info(cursor.query.decode())
        logger.info("Feed Data: %s", feed_data)
        flaggedByUsersList = feed_data[0]
        logger.info(f"{affected_count} rows affected")

    except Exception as e:
        logger.info(e)

    # check if requested user already flagged this feed post
    isFeedAlreadyFlaggedByUser = False
    for id in flaggedByUsersList:
        if id == user_id:
            isFeedAlreadyFlaggedByUser = True

    if isFeedAlreadyFlaggedByUser:
        response["flagged_status"] = "FALSE"
        updateUserFeedFlagStatusQuery = "UPDATE task_list SET flags_on_feed = flags_on_feed - 1, flagged_by = array_remove(flagged_by, %s) WHERE list_id = %s"
        try:
            cursor.execute(
                updateUserFeedFlagStatusQuery,
                (
                    user_id,
                    list_id,
                ),
            )
            conn.commit()
            affected_count = cursor.rowcount
            logger.info(cursor.query.decode())
            logger.info(f"{affected_count} rows affected")

        except Exception as e:
            logger.info(e)

        finally:
            cursor.close()
    else:
        response["flagged_status"] = "TRUE"
        updateUserFeedFlagStatusQuery = "UPDATE task_list SET flags_on_feed = flags_on_feed + 1, flagged_by = array_append(flagged_by, %s) WHERE list_id = %s"
        try:
            cursor.execute(
                updateUserFeedFlagStatusQuery,
                (
                    user_id,
                    list_id,
                ),
            )
            conn.commit()
            affected_count = cursor.rowcount
            logger.info(cursor.query.decode())
            logger.info(f"{affected_count} rows affected")

        except Exception as e:
            logger.info(e)

        finally:
            cursor.close()

    if affected_count == 0:
        response["status"] = "failure"
        response["message"] = "Reporting of feed by user failed !"
        return jsonify(response), 500
    else:
        response["status"] = "success"
        if response["flagged_status"] == "TRUE":
            response[
                "message"
            ] = "post flagged by user ! We will soon take an action based on our internal investigation."
        elif response["flagged_status"] == "FALSE":
            response[
                "message"
            ] = "post unflagged by user ! Thanks for helping the community to grow."
        return jsonify(response), 200
