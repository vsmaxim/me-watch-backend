FROM python:3.7.3-alpine3.9

WORKDIR /app

COPY . /app

RUN apk update && \
    apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps \
    postgresql-dev gcc python3-dev musl-dev && \
    pip install -r requirements.txt && \
    apk del --no-cache .build-deps

ENTRYPOINT ["/app/entrypoint.sh"]