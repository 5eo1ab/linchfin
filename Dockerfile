FROM python:3.8-slim

ARG UID=1000
ARG GID=1000
ENV WORKDIR=/opt/linchfin
RUN mkdir /opt/linchfin \
  && groupadd -g $GID linchfin \
  && useradd -g $GID -u $UID -d /home/linchfin -s /bin/bash linchfin

ADD . /opt/linchfin
WORKDIR /opt/linchfin
RUN pip install -r requirements.txt \
  && python setup.py install
USER linchfin
WORKDIR /home/linchfin
CMD ["python"]
