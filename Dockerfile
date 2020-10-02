FROM binkhq/python:3.8

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

WORKDIR /app
ADD . .
RUN apt-get update && apt-get -y install gcc && \
    pip install gunicorn pipenv==2020.8.13 && \
    pipenv install --system --deploy --ignore-pipfile && \
    apt-get -y autoremove gcc && rm -rf /var/lib/apt/lists

CMD [ "gunicorn", "--workers=2", "--threads=2", "--error-logfile=-", \
                  "--access-logfile=-", "--bind=0.0.0.0:9000", "wsgi:app" ]
