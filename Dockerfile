FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN apt-get update \
	&& apt-get install -y --no-install-recommends sqlite3 procps \
	&& rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt \
	&& pip install --no-cache-dir .
