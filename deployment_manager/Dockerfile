FROM alpine:latest

RUN apk update && apk add python3 py3-pip curl unzip
ADD . ./home
RUN cd home && pip3 install --no-cache-dir -r /home/requirements.txt

ENTRYPOINT python3 -u /home/deployer.py