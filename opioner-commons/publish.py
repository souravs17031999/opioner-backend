import json
import requests
import os
import datetime
import pytz

if __name__ == "__main__":

    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    print("========= SENDING DATA ON: ", webhook_url)
    slack_data_for_message = {
        "username": "TasklyNotificationBot",
        "icon_emoji": ":satellite:",
        "text": "test message",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"DOCKER BUILD #{os.getenv('BUILD_NUMBER')} ON JENKINS",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": "*Type:*\nNotification"},
                    {"type": "mrkdwn", "text": "*Created by:*\nJenkins build"},
                ],
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*When:*\n {datetime.datetime.now(pytz.timezone('Asia/Kolkata'))}",
                    }
                ],
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "auth service"},
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Click for dockerhub",
                        "emoji": True,
                    },
                    "value": "click_me_123",
                    "url": "https://hub.docker.com/repository/docker/souravkumardevadmin/taskly-backend-docker-app_auth_service",
                    "action_id": "button-action",
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "user service"},
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Click for dockerhub",
                        "emoji": True,
                    },
                    "value": "click_me_123",
                    "url": "https://hub.docker.com/repository/docker/souravkumardevadmin/taskly-backend-docker-app_user_service",
                    "action_id": "button-action",
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "product service"},
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Click for dockerhub",
                        "emoji": True,
                    },
                    "value": "click_me_123",
                    "url": "https://hub.docker.com/repository/docker/souravkumardevadmin/taskly-backend-docker-app_product_service",
                    "action_id": "button-action",
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "notification service"},
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Click for dockerhub",
                        "emoji": True,
                    },
                    "value": "click_me_123",
                    "url": "https://hub.docker.com/repository/docker/souravkumardevadmin/taskly-backend-docker-app_notification_service",
                    "action_id": "button-action",
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "cron service"},
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Click for dockerhub",
                        "emoji": True,
                    },
                    "value": "click_me_123",
                    "url": "https://hub.docker.com/repository/docker/souravkumardevadmin/taskly-backend-docker-app_cron_service",
                    "action_id": "button-action",
                },
            },
        ],
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(
        webhook_url, data=json.dumps(slack_data_for_message), headers=headers
    )
    print("============== RESPONSE: ", response)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
