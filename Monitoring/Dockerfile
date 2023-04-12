FROM alpine:latest

RUN apk update && apk add python3 py3-pip
# COPY requirements.txt ./ActionManager/requirements.txt
ADD . ./Monitoring
RUN cd Monitoring && pip install -r /Monitoring/requirements.txt

ENTRYPOINT python3 -u /Monitoring/main.py