FROM python:3.9-alpine

RUN apk update && apk add --no-cache curl unzip
# COPY requirements.txt ./ActionManager/requirements.txt
ADD . ./monitoring
RUN cd monitoring && pip install -r /monitoring/requirements.txt

ENTRYPOINT python3 -u /monitoring/main.py