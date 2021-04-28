FROM python:3.7.10-slim as base

LABEL DCUENG <dcueng@godaddy.com>

RUN apt-get update && apt-get install gcc -y
RUN pip3 install -U pip
COPY requirements.txt .
COPY ./private_pips /tmp/private_pips

RUN pip3 install --compile /tmp/private_pips/PyAuth
RUN pip3 install --compile /tmp/private_pips/dcu-structured-logging-flask
RUN pip3 install -r requirements.txt
RUN rm requirements.txt
RUN rm -rf /tmp/private_pips

FROM base as deliverable

# Move files to new dir
COPY ./run.py ./runserver.sh ./settings.py ./kubetipper.sh ./*.ini /app/

# Compile the Flask API
RUN mkdir /tmp/build
COPY . /tmp/build
RUN pip3 install --compile /tmp/build
RUN rm -rf /tmp/build

# Fix permissions.
RUN addgroup dcu && adduser --disabled-password --disabled-login --no-create-home --ingroup dcu --system dcu
RUN chown -R dcu:dcu /usr/local/lib/python3.7/site-packages/tld/res
RUN chown dcu:dcu -R /app

# Configure container level settings.
ENV prometheus_multiproc_dir /tmp
EXPOSE 5000

ENTRYPOINT ["/app/runserver.sh"]