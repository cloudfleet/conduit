#! /bin/bash

apt-get update && \
apt-get upgrade -y && \
apt-get install python-pip docker.io nginx -y && \
(cd /vagrant && pip install -r requirements.txt) && \
adduser vagrant docker && \
mkdir -p /opt/cloudfleet && \
chown vagrant /opt/cloudfleet
