#!/usr/bin/env sh

python -c "import re;ns='172.31.251.11';f=open('/etc/resolv.conf','r');t=f.read();regexp=re.compile(r'{}'.format(ns));t=re.sub(r'(nameserver \S+)',r'\1\nnameserver {}'.format(ns),t) if not regexp.search(t) else t;t=re.sub(r'ndots:\d+',r'ndots:1',t);open('/etc/resolv.conf','w').write(t)"

if [ -z "$HTTP_ONLY" ]
then
    exec /usr/bin/uwsgi --ini /app/uwsgi_ssl.ini --need-app --lazy-apps
else
    exec /usr/bin/uwsgi --ini /app/uwsgi.ini --need-app --lazy-apps
fi
