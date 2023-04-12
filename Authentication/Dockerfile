FROM alpine:latest

RUN apk update && apk add python3 py3-pip
# COPY requirements.txt ./ActionManager/requirements.txt
ADD . ./Authentication
RUN cd Authentication && pip install -r /Authentication/requirements.txt

ENTRYPOINT python3 -u /Authentication/app.py
