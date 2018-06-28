FROM python:3.6

WORKDIR /app
ADD . .

RUN pip install uwsgi pipenv && \
    pipenv install --system
