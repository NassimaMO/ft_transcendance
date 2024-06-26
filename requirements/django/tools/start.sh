#!/bin/sh

python3 srcs/manage.py collectstatic --no-input
python3 srcs/manage.py makemigrations
python3 srcs/manage.py migrate
# python3 srcs/manage.py createsuperuser
python3 srcs/manage.py runserver 0.0.0.0:8000