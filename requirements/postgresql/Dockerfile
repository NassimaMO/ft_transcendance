FROM python:3.10

COPY . .

WORKDIR /conf

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

FROM postgres:15

COPY . .

WORKDIR /tools

RUN chmod 777 dbscript.sh

ENTRYPOINT [ "dbscript.sh" ]