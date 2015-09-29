FROM python:3

MAINTAINER buluba89

RUN export DEBIAN_FRONTEND='noninteractive' && \
          apt-get update -qq && \
          apt-get install git

RUN git clone --depth 1 https://github.com/buluba89/Yatcobot.git  /yatcobot &&\
    cd /yatcobot &&\
    pip3 install -r requirements.txt


WORKDIR /yatcobot

ENTRYPOINT python3 yatcobot.py  
