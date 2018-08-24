# CMAP Service
#

FROM alpine:3.5
MAINTAINER DCU <DCUEng@godaddy.com>

RUN addgroup -S dcu && adduser -H -S -G dcu dcu
# apk installs
RUN apk --no-cache add build-base \
    ca-certificates \
    coreutils \
    bc \
    openssl-dev \
    linux-headers \
    python-dev \
    py-pip


# Expose Flask port 5000
EXPOSE 5000

# Move files to new dir
COPY ./logging.yml ./run.py ./runserver.sh ./settings.py ./kubetipper.sh ./*.ini /app/
COPY . /tmp
RUN chown -R dcu:dcu /app

COPY trusted_certs/* /usr/local/share/ca-certificates/
RUN update-ca-certificates && pip install --compile /tmp && rm -rf /tmp/*

WORKDIR /app
ENTRYPOINT ["/app/runserver.sh"]
