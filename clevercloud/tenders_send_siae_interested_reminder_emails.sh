#!/bin/bash -l

# Send TenderSiae interested reminder emails

# Do not run if this env var is not set:
if [[ -z "$CRON_TENDER_SEND_SIAE_INTERESTED_REMINDER_EMAILS_ENABLED" ]]; then
    echo "CRON_TENDER_SEND_SIAE_INTERESTED_REMINDER_EMAILS_ENABLED not set. Exiting..."
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

django-admin send_siae_interested_reminder_emails --days-since-detail-contact-click-date 2
