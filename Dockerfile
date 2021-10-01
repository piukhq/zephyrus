FROM ghcr.io/binkhq/python:3.9

WORKDIR /app
ADD . .
RUN pipenv install --system --deploy --ignore-pipfile

ENV PROMETHEUS_MULTIPROC_DIR=/dev/shm
ENTRYPOINT [ "linkerd-await", "--" ]
CMD [ "gunicorn", "--workers=2", "--threads=2", "--error-logfile=-", \
    "--logger-class=gunicorn_logger.Logger", \
    "--access-logfile=-", "--bind=0.0.0.0:9000", \
    "--bind=0.0.0.0:9100", "wsgi:app" ]
