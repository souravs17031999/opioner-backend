# syntax=docker/dockerfile:1

FROM souravkumardevadmin/baseos-python_baseos_python:1.0.0

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
ENV SENDGRID_API_KEY_PROD=sendgrid  
ENV APM_MONITORING_NEWRELIC=False
ENV SECRET_KEY=""

ENTRYPOINT ["sh", "/app/docker-entrypoint.sh"]