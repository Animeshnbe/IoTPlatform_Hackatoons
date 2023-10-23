FROM alpine:latest

RUN apk update && apk add python3 py3-pip
ADD . ./app3
RUN cd app3 && pip install -r /app3/requirements.txt

ENTRYPOINT python3 -u /app3/app.py