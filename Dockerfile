FROM python:3.13-alpine
WORKDIR /hyperblur

COPY ./requirements.txt ./requirements.txt

# ponytail: docker layer caching optimization -> copy requirements & install before src copy
RUN apk update && apk upgrade --no-cache && \
    apk add --no-cache tini && \
    addgroup -g 1000 -S hyperblur && \
    adduser -u 1000 -S hyperblur -G hyperblur && \
    pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

COPY ./src/ ./src/
COPY ./assets/ ./assets/

RUN chown -R hyperblur:hyperblur /hyperblur

EXPOSE 8000
USER hyperblur
ENTRYPOINT [ "/sbin/tini", "--"]
CMD [ "python", "-m", "src.server" ]


