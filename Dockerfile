FROM python:3.12-slim

COPY . .

RUN apt-get update

RUN apt-get install -y --no-install-recommends sqlite3 \
	&& rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt \
	&& pip install --no-cache-dir .
