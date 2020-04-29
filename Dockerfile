FROM python:3.6

WORKDIR /app
ADD . .
ARG DEPLOY_KEY
RUN mkdir -p /root/.ssh && \
    echo $DEPLOY_KEY | base64 -d > /root/.ssh/id_rsa && \
    chmod 600 /root/.ssh/id_rsa && \
    ssh-keyscan git.bink.com > /root/.ssh/known_hosts && \
    pip install uwsgi pipenv && \
    pipenv install --system && \
    rm -rf /root/.ssh
