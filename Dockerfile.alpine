FROM python:3.6-alpine3.7

MAINTAINER buluba89

RUN mkdir /build &&\
    pip3 install pipenv

ADD Pipfile* /build/

RUN cd /build &&\
    pipenv install --system


ADD requirements.txt README.rst setup.py /build/

ADD yatcobot /build/yatcobot

RUN cd /build &&\
    python setup.py install

VOLUME ["/yatcobot"]

WORKDIR /yatcobot

ENTRYPOINT ["yatcobot"]
CMD []