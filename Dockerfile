FROM python:3.9.7

RUN sudo apt-get install sqlite3 &&
	python3 setup.py install