#!/usr/bin/env sh

python -c "import re;ns='172.31.251.11';f=open('/etc/resolv.conf','r');t=f.read();regexp=re.compile(r'{}'.format(ns));t=re.sub(r'(nameserver \S+)',r'\1\nnameserver {}'.format(ns),t) if not regexp.search(t) else t;t=re.sub(r'ndots:\d+',r'ndots:1',t);open('/etc/resolv.conf','w').write(t)"
sed -i 's/MinProtocol = TLSv1.2/MinProtocol = TLSv'$TLS_MIN_VERSION'/' /etc/ssl/openssl.cnf

if [ -z "$HTTP_ONLY" ]
then
    exec /usr/local/bin/uwsgi --ini /app/uwsgi_ssl.ini --need-app
else
    exec /usr/local/bin/uwsgi --ini /app/uwsgi.ini --need-app
fi
