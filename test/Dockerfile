# syntax=docker/dockerfile:1

FROM node:16-alpine

WORKDIR /apitest

COPY . .

RUN npm install

# RUN apk add postgresql-client

# CMD ["mocha", "/apitest/test.js", "--reporter", "spec"]
# npx mocha --reporter spec

ENTRYPOINT ["sh", "/apitest/docker-entrypoint.sh"]