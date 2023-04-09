FROM alpine:latest

RUN apt-get update && apt-get install -y python3 py3-pip curl unzip
COPY requirements.txt ./home/requirements.txt
ADD app.py .
RUN cd home && pip3 install --no-cache-dir -r requirements.txt

# RUN curl -LO https://github.com/redpanda-data/redpanda/releases/latest/download/rpk-linux-amd64.zip && \
#     mkdir -p ~/.local/bin && \
#     unzip rpk-linux-amd64.zip -d ~/.local/bin/ && \
#     rm rpk-linux-amd64.zip

# ENV PATH="/root/.local/bin:${PATH}"

ENTRYPOINT python3 -u app.py thermometer pressure