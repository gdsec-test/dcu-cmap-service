# PhishNet
#
# V 5.0 Shared Volume Multi Docker

FROM ubuntu:14.04
MAINTAINER CSIRT-CSA <csa@godaddy.com>

# apt-get installs
RUN apt-get update && \
    apt-get install -y build-essential \
    gcc \
    libssl-dev \
    python \
    python-dev \
    python-pip


# Expose Flask port 5000
EXPOSE 5000

# Move files to new dir
ADD . /app

# pip install private pips staged by Makefile
#RUN for entry in blindAl; \
#    do \
#    pip install --compile "/app/private_pips/$entry"; \
#    done

# install other requirements
RUN pip install --compile -r /app/requirements.txt

# cleanup
RUN apt-get remove --purge -y gcc \
    libssl-dev \
    python-dev && \
    rm -rf /var/lib/apt/lists/*
    #rm -rf /home/phishstory/phishnet/private_pips

ENTRYPOINT ["/app/runserver.sh"]
