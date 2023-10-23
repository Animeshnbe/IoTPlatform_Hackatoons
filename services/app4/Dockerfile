FROM alpine:latest

RUN apk update && apk add python3 py3-pip
ADD . ./app4
RUN cd app4 && pip install -r /app4/requirements.txt

ENTRYPOINT python3 -u /app4/app.py