FROM ubuntu:latest

RUN apt-get update && apt-get upgrade -y

RUN apt-get install python3 python3-dev python3-pip python3-numpy python3-wheel swig -y

RUN locale-gen en_US.UTF-8

ENV LANG=en_US.UTF-8 LANGUAGE=en_US:en LC_ALL=en_US.UTF-8

WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip3 install -r requirements.txt

COPY . /usr/src/app

CMD python3 main.py