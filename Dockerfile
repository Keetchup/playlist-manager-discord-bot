FROM python:3.10-slim-bullseye AS builder

RUN mkdir /app
WORKDIR /app

#Python libraries
COPY requirements.txt .
RUN pip install --user -r requirements.txt

#Source code
COPY ./src .

#ffmpeg
RUN apt-get update && \
    apt-get install ffmpeg -y


CMD [ "python", "./main.py" ]