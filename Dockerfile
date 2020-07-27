FROM python:3.6

WORKDIR /app
ADD . .
RUN pip install uwsgi pipenv==2018.11.26 && \
    pipenv install --system && \
    rm -rf /root/.ssh
