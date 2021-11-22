FROM python:3.9.7

COPY . .

RUN apt-get -y update

RUN apt-get -y install sqlite3 

RUN pip3 install -r requirements.txt && python3 setup.py install