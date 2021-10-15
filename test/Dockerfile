# syntax=docker/dockerfile:1

FROM node:16-alpine

WORKDIR /apitest

COPY . .

RUN npm update && \
    npm install --save mocha chai \ 
    npm install --save request \ 
    npm install --save express


# CMD ["mocha", "/apitest/test.js", "--reporter", "spec"]
# npx mocha --reporter spec

ENTRYPOINT ["sh", "/apitest/docker-entrypoint.sh"]