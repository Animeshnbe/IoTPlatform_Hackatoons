FROM ubuntu:22.04

RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip3 install flask
RUN pip3 install kafka ; exit 0
RUN pip3 install uuid ; exit 0

ADD kafka_expt.py .

ENTRYPOINT python3 -u kafka_expt.py thermometer air_quality pressure ac gate_opener 