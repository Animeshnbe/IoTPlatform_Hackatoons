FROM python:3

RUN apt update && apt install curl unzip
ADD . ./home
RUN cd home && pip3 install --no-cache-dir -r /home/requirements.txt

ENTRYPOINT python3 -u /home/deployer.py