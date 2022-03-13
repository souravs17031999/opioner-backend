# syntax=docker/dockerfile:1

FROM node:16-alpine

WORKDIR /apitest

COPY . .

RUN apk add curl

RUN npm --prefix apitest install
RUN npm --prefix postdeploy install

ENTRYPOINT ["sh", "/apitest/docker-entrypoint.sh"]