# syntax=docker/dockerfile:1

FROM python:3.8-alpine

WORKDIR /apitest

COPY . .

ENTRYPOINT ["sh", "/apitest/docker-entrypoint.sh"]