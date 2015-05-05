FROM debian:jessie

RUN echo "deb http://ftp.de.debian.org/debian experimental main" >> /etc/apt/sources.list

RUN apt-get update -y
RUN apt-get install -y python-pip docker.io

ADD . /opt/conduit
WORKDIR /opt/conduit

RUN pip install -r requirements.txt

CMD /usr/bin/python -u conduit.py

EXPOSE 5000
