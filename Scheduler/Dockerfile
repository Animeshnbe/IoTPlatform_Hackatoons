FROM alpine:latest

RUN apk update && apk add python3 py3-pip curl unzip
COPY requirements.txt ./home/requirements.txt
ADD scheduler.py ./home
ADD heartBeat.py ./home
RUN cd home && pip3 install --no-cache-dir -r /home/requirements.txt

ENTRYPOINT python3 -u /home/scheduler.py