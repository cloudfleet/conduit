FROM debian:jessie

ADD . /opt/conduit
WORKDIR /opt/conduit

RUN ./scripts/install_docker.sh

RUN apt-get install -y python-pip

RUN pip install -r requirements.txt

CMD /usr/bin/python -u conduit.py

EXPOSE 5000
