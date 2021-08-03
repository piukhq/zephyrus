FROM ghcr.io/binkhq/python:3.9

WORKDIR /app
ADD . .
RUN pipenv install --system --deploy --ignore-pipfile

ENTRYPOINT [ "linkerd-await", "--" ]
CMD [ "gunicorn", "--workers=2", "--threads=2", "--error-logfile=-", \
    "--access-logfile=-", "--bind=0.0.0.0:9000", "wsgi:app" ]
