FROM ghcr.io/binkhq/python:3.9 AS build

WORKDIR /src

RUN apt update && apt -y install git
RUN pip install poetry
RUN poetry self add "poetry-dynamic-versioning[plugin]"

COPY . .

RUN poetry build

FROM ghcr.io/binkhq/python:3.9

ARG PIP_INDEX_URL

WORKDIR /app

COPY --from=build /src/dist/*.whl .
RUN pip install *.whl && rm *.whl

COPY --from=build /src/wsgi.py .

CMD [ "gunicorn", "--workers=2", "--threads=2", "--error-logfile=-", "--logger-class=gunicorn_logger.Logger", \
    "--access-logfile=-", "--bind=0.0.0.0:9000", "wsgi:app" ]
