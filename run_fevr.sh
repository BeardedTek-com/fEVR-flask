#!/bin/bash
[ ! -d "/fevr/venv" ] && \
    echo "Initializing Virtual Environment" && \
    python -m venv venv && \
    echo "Starting Virtual Environment" && \
    source /fevr/venv/bin/activate && \
    echo "pip install wheel" && \
    pip install wheel && \
    echo "pip install requirements" && \
    pip install -r /fevr/app/requirements.txt && \
    echo "Done Installing python requirements" \
|| \
    echo "Python Virtual Environment already installed."
    echo "Activating Python Virtual Environment"
    source /fevr/venv/bin/activate

echo "Starting fEVR"
export FLASK_ENV='development'
flask run -h "0.0.0.0" -p 5090