# CMAP Service
#

FROM alpine:3.5
MAINTAINER DCU <DCUEng@godaddy.com>

# apk installs
RUN apk update && \
    apk --no-cache add build-base \
    ca-certificates \
    linux-headers \
    python-dev \
    py-pip


# Expose Flask port 5000
EXPOSE 5000

# Move files to new dir
ADD . /app
WORKDIR /app
COPY trusted_certs /usr/local/share/ca-certificates

# pip install private pips staged by Makefile
RUN update-ca-certificates && for entry in blindAl; \
    do \
    pip install --compile "private_pips/$entry"; \
    done

# install other requirements
RUN pip install --compile -r requirements.txt

# cleanup
RUN rm -rf private_pips

ENTRYPOINT ["/app/runserver.sh"]
