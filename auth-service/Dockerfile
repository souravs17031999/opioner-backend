# syntax=docker/dockerfile:1

FROM python:3.8-alpine

WORKDIR /app

COPY requirements.txt requirements.txt

RUN apk add --no-cache python3-dev openssl-dev libffi-dev gcc && pip3 install --upgrade pip
RUN apk add postgresql
RUN \
    apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    python3 -m pip install -r requirements.txt --no-cache-dir && \
    apk --purge del .build-deps

COPY . .

ENV PGHOST=postgres
ENV PGUSER=postgres
ENV PGPASSWORD=postgres
ENV PGDATABASE=postgres 
ENV ALLOWED_ORIGIN_HOST_PROD=*
ENV DATABASE_URL=postgres
ENV REDIS_URL=redis  
ENV NOTIFICATION_INTERNAL_URL=http://notification_service:8084

ENTRYPOINT ["sh", "/app/docker-entrypoint.sh"]