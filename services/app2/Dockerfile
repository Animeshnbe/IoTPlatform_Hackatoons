FROM alpine:latest

RUN apk update && apk add python3 py3-pip
ADD . ./app2
RUN cd app2 && pip install -r /app2/requirements.txt

ENTRYPOINT python3 -u /app2/app.py