FROM python:3.10

COPY ./srcs /app

COPY ./requirements/django/conf /app/conf

WORKDIR /app/conf

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

WORKDIR /app/srcs