FROM ubuntu:latest

RUN apt-get -y update && apt-get install -y net-tools iputils-ping python3
RUN apt-get install -y python3-dev python3-pip git
RUN python3 -m pip install --upgrade pip

RUN pip3 install zmq
RUN pip3 install flask

WORKDIR /root/
RUN git clone https://github.com/blakedq/4287-Final
WORKDIR /root/4287-Final/website