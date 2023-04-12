FROM alpine:latest

RUN apk update && apk add python3 py3-pip
ADD . ./workflow
RUN cd workflow && pip install -r ./workflow/requirements.txt


ENTRYPOINT python3 -u ./workflow/main.py