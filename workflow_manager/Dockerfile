FROM alpine:latest

RUN apk update && apk add python3 py3-pip
ADD . ./home
RUN cd home && pip install -r ./requirements.txt


ENTRYPOINT python3 -u ./home/main.py