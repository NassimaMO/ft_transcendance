FROM python:3.10

WORKDIR /app

RUN mkdir /app/staticfiles

COPY srcs /app/srcs

COPY requirements/django/conf /app/conf

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r conf/requirements.txt

COPY requirements/django/tools/start.sh .

RUN chmod 755 ./start.sh

ENTRYPOINT ["./start.sh"]