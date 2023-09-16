FROM python:3.11-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y ffmpeg libavcodec-extra

COPY requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install -r ./requirements.txt --no-cache-di
COPY . .