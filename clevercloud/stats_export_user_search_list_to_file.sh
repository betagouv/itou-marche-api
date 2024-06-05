#!/bin/bash -l

# Do not run if this env var is not set:
if [[ -z "$CRON_SIAE_EXPORT_ENABLED" ]]; then
    echo "CRON_SIAE_EXPORT_ENABLED not set. Exiting..."
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

django-admin export_user_search_list
