# syntax=docker/dockerfile:1

FROM souravkumardevadmin/baseos-python_baseos_python:0.0.0

WORKDIR /app

COPY requirements.txt requirements.txt

RUN python3 -m pip install -r requirements.txt --no-cache-dir

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