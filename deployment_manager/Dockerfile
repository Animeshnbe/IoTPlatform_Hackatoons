FROM base_image

RUN pip3 install flask
RUN pip3 install numpy ; exit 0
RUN pip3 install uuid ; exit 0

ADD kafka_expt.py .

ENTRYPOINT python3 -u kafka_expt.py thermometer air_quality pressure ac gate_opener 