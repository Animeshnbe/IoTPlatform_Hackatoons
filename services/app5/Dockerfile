FROM alpine:latest

RUN apk update && apk add python3 py3-pip
ADD . ./app5
RUN cd app5 && pip install -r /app5/requirements.txt

ENTRYPOINT python3 -u /app5/app.py