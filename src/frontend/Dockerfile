FROM node:24-alpine

WORKDIR /app

COPY ./src/package.json /app/src/package.json
RUN npm install --prefix src

COPY ./src /app/src

RUN npm run build --prefix src

COPY ./entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]