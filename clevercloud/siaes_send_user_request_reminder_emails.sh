#!/bin/bash -l

# Send SiaeUserRequest reminder emails

# Do not run if this env var is not set:
if [[ -z "$CRON_SIAE_SEND_USER_REQUEST_REMINDER_EMAILS_ENABLED" ]]; then
    echo "CRON_SIAE_SEND_USER_REQUEST_REMINDER_EMAILS_ENABLED not set. Exiting..."
    exit 0
fi

# About clever cloud cronjobs:
# https://developers.clever-cloud.com/doc/administrate/cron/

if [[ "$INSTANCE_NUMBER" != "0" ]]; then
    echo "Instance number is ${INSTANCE_NUMBER}. Stop here."
    exit 0
fi

# $APP_HOME is set by default by clever cloud.
cd $APP_HOME

django-admin send_siae_user_request_reminder_emails
