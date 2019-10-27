FROM ubuntu:19.10

RUN apt-get update && \
    apt-get install -y python3 python3-pip
