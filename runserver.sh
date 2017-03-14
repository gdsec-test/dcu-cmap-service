#!/usr/bin/env sh

if [ -z "$HTTP_ONLY" ]
then
    exec /usr/bin/uwsgi --ini /app/uwsgi_ssl.ini --need-app
else
    exec /usr/bin/uwsgi --ini /app/uwsgi.ini --need-app
fi
