FROM docker-dcu-local.artifactory.secureserver.net/dcu-python3.11:1.1
LABEL MAINTAINER=dcueng@godaddy.com

USER root
RUN apt-get update && apt-get install gcc -y
RUN pip3 install -U pip

# Compile the Flask API
RUN mkdir -p /tmp/build
RUN apt-get update && apt-get install gcc libffi-dev -y
COPY requirements.txt /tmp/build/
COPY pip_config /tmp/build/pip_config
RUN PIP_CONFIG_FILE=/tmp/build/pip_config/pip.conf pip3 install -r /tmp/build/requirements.txt

COPY *.py /tmp/build/
COPY test_requirements.txt /tmp/build/
COPY README.md /tmp/build/
COPY service /tmp/build/service
COPY trusted_certs /tmp/build/service
RUN PIP_CONFIG_FILE=/tmp/build/pip_config/pip.conf pip3 install --compile /tmp/build
RUN apt-get remove gcc libffi-dev -y
# Move files to new dir
COPY ./run.py ./settings.py ./kubetipper.sh ./*.ini /app/

# Cleanup
RUN rm -rf /tmp/build

# Grab the latest TLD list, and verify it is valid.
RUN update-tld-names
RUN python -c 'import tld; tld.get_tld("https://godaddy.com")'

# Fix permissions.
RUN chown -R dcu:dcu /usr/local/lib/python3.11/site-packages/tld/res
RUN chown dcu:dcu -R /app

# Configure container level settings.
ENV TLS_MIN_VERSION 1.2
EXPOSE 5000

USER dcu
ENTRYPOINT ["/usr/local/bin/uwsgi", "--ini", "/app/uwsgi.ini", "--need-app"]