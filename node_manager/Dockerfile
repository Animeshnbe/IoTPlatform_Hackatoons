FROM alpine:latest

RUN apk update && apk add python3 py3-pip curl linux-headers
ADD . ./home
RUN cd home && pip3 install --no-cache-dir -r /home/requirements.txt

ENTRYPOINT cd home && python3 -u /home/node_alloc.py