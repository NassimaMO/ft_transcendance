FROM python:3.10

COPY . .

WORKDIR /requirements/django/conf/

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

WORKDIR /srcs