FROM alpine:latest

RUN apk update && apk add python3 py3-pip
# COPY requirements.txt ./action_manager/requirements.txt
ADD . ./action_manager
RUN cd action_manager && pip install -r /action_manager/requirements.txt

ENTRYPOINT python3 -u /action_manager/main.py