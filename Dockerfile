FROM python:3.7.10-slim as base

LABEL DCUENG <dcueng@godaddy.com>

RUN apt-get update && apt-get install gcc -y
RUN pip3 install -U pip

FROM base as deliverable

# Move files to new dir
COPY ./run.py ./runserver.sh ./settings.py ./kubetipper.sh ./*.ini /app/

# Compile the Flask API
RUN mkdir /tmp/build
COPY . /tmp/build
RUN PIP_CONFIG_FILE=/tmp/build/pip_config/pip.conf pip3 install --compile /tmp/build
RUN rm -rf /tmp/build

# Grab the latest TLD list, and verify it is valid.
RUN update-tld-names
RUN python -c 'import tld; tld.get_tld("https://godaddy.com")'

# Fix permissions.
RUN addgroup dcu && adduser --disabled-password --disabled-login --no-create-home --ingroup dcu --system dcu
RUN chown -R dcu:dcu /usr/local/lib/python3.7/site-packages/tld/res
RUN chown dcu:dcu -R /app

# Configure container level settings.
ENV TLS_MIN_VERSION 1.2
EXPOSE 5000

ENTRYPOINT ["/app/runserver.sh"]