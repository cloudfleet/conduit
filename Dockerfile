FROM debian:jessie

ADD ./scripts .
RUN ./scripts/install_docker.sh
RUN apt-get install -y python-pip
WORKDIR /opt/conduit
ADD requirements.txt /opt/conduit/requirements.txt
RUN pip install -r requirements.txt

ADD . /opt/conduit


CMD /usr/bin/python -u conduit.py

EXPOSE 5000
