FROM python:3.11.0b1-slim-bullseye
COPY . /fevr
RUN groupadd -g 1000 fevr && useradd -u 1000 -g fevr -d /fevr fevr && \
    chown -R 1000:1000 /fevr && \
    apt-get update && \
    apt-get install --no-install-recommends -y \
    python3-paho-mqtt python3-requests python3-dotenv
WORKDIR /fevr
USER fevr