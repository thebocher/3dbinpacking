FROM python:3.10.9

WORKDIR /var/api

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY api/ .

ENV DEBUG=1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
