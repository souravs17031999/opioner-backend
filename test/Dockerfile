# syntax=docker/dockerfile:1

FROM node:16-alpine

WORKDIR /apitest

COPY . .

RUN npm update && \
    npm install -g mocha

CMD ["mocha", "apitest/test.js", "--reporter", "spec"]