FROM python:3.6

WORKDIR /app
ADD . .

RUN pip install uwsgi pipenv && \
    cd /app && pipenv install --system
