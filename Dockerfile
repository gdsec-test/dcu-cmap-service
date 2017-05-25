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
COPY trusted_certs /usr/local/share/ca-certificates
COPY . /tmp

# pip install private pips staged by Makefile
RUN update-ca-certificates && for entry in blindAl; \
    do \
    pip install --compile "/tmp/private_pips/$entry"; \
    done

# install other requirements
RUN pip install --compile /tmp

# cleanup
RUN rm -rf /tmp/* && chown -R dcu:dcu /app

WORKDIR /app
ENTRYPOINT ["/app/runserver.sh"]
