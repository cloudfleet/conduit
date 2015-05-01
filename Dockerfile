FROM ubuntu:14.04

RUN apt-get update -y
RUN apt-get install -y python-pip

ADD . /opt/conduit
WORKDIR /opt/conduit

RUN pip install -r requirements.txt

EXPOSE 5000
