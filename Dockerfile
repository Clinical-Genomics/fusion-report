FROM python:3.9.7

RUN sudo apt-get install sqlite3 && pip3 install -r requirements.txt && python3 setup.py install