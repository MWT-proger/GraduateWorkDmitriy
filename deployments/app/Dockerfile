FROM python:3.11-slim

ENV HOME_DIR=/usr/app
ENV LOCAL_DIR=app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR $HOME_DIR

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    pip install --upgrade pip 

COPY $LOCAL_DIR/requirements.txt .

RUN pip install -r requirements.txt

COPY $LOCAL_DIR/src ./src

WORKDIR $HOME_DIR/src
