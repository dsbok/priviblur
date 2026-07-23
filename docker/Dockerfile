FROM python:3.13-alpine
WORKDIR /priviblur

COPY ./requirements.txt ./requirements.txt
COPY ./src/ ./src/
COPY ./assets/ ./assets/

RUN apk update && apk upgrade --no-cache && \
    apk add --no-cache tini && \
    addgroup -g 1000 -S priviblur && \
    adduser -u 1000 -S priviblur -G priviblur && \
    pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    chown -R priviblur:priviblur /priviblur

EXPOSE 8000
USER priviblur
ENTRYPOINT [ "/sbin/tini", "--"]
CMD [ "python", "-m", "src.server" ]

