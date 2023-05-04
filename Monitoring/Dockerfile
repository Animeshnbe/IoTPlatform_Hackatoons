FROM python:3.9-alpine

RUN apk update && apk add --no-cache curl unzip
# COPY requirements.txt ./ActionManager/requirements.txt
ADD . ./Monitoring
RUN cd Monitoring && pip install -r /Monitoring/requirements.txt

ENTRYPOINT python3 -u /Monitoring/main.py