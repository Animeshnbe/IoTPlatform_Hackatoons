FROM alpine:latest

RUN apk update && apk add python3 py3-pip
ADD . ./app1
RUN cd app1 && pip install -r /app1/requirements.txt

ENTRYPOINT python3 -u /app1/app.py