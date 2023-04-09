FROM alpine:latest

RUN apk update && apk add python3 py3-pip
# COPY requirements.txt ./ActionManager/requirements.txt
ADD . ./ActionManager
RUN cd ActionManager && pip install -r /ActionManager/requirements.txt

ENTRYPOINT python3 -u /ActionManager/main.py