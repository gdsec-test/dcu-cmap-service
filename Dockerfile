# CMAP Service
#

FROM alpine:3.6
MAINTAINER DCU <DCUEng@godaddy.com>

RUN addgroup -S dcu && adduser -H -S -G dcu dcu
# apk installs
RUN apk --no-cache add build-base \
    ca-certificates \
    coreutils \
    bc \
    libffi-dev \
    linux-headers \
    libxml2-dev \
    libxslt-dev \
    python3-dev \
    py3-pip \
    gcc \
    musl-dev \
    libressl-dev

# Expose Flask port 5000
EXPOSE 5000

# Move files to new dir
COPY ./logging.yaml ./run.py ./runserver.sh ./settings.py ./kubetipper.sh ./*.ini /app/
COPY . /tmp
RUN chown -R dcu:dcu /app

# pip install private pips staged by Makefile
RUN for entry in PyAuth; \
    do \
    CRYPTOGRAPHY_DONT_BUILD_RUST=1 pip3 install --compile "/tmp/private_pips/$entry"; \
    done

COPY trusted_certs/* /usr/local/share/ca-certificates/
RUN update-ca-certificates && pip3 install -U cffi && pip3 install --compile /tmp && rm -rf /tmp/*

# Chown Public Suffix list so we can update it
RUN chown -R dcu:dcu /usr/lib/python3.6/site-packages/tld/res

WORKDIR /app
ENTRYPOINT ["/app/runserver.sh"]
