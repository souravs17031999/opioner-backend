# syntax=docker/dockerfile:1

FROM node:16-alpine

WORKDIR /apitest

COPY . .

RUN apk add curl

RUN npm --prefix apitest ci
RUN npm --prefix postdeploy ci

ENTRYPOINT ["sh", "/apitest/docker-entrypoint.sh"]