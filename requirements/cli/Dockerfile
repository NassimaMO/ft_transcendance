FROM python:3.10

WORKDIR /app

COPY requirements/cli/conf /app/conf

RUN pip install --upgrade pip

RUN pip install pip-tools

RUN pip-compile conf/requirements.in -o conf/requirements.txt

RUN pip install --no-cache-dir -r conf/requirements.txt

COPY srcs/cli /app/srcs