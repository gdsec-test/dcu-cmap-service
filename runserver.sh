#!/usr/bin/env bash

if [ -z "$HTTP_ONLY" ]
then
    exec /usr/local/bin/uwsgi --ini /app/uwsgi_ssl.ini --need-app
else
    exec /usr/local/bin/uwsgi --ini /app/uwsgi.ini --need-app
fi
