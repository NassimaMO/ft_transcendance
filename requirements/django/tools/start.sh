#!/bin/sh

sleep 3

python3 srcs/manage.py collectstatic --no-input

python3 srcs/manage.py migrate

python3 srcs/manage.py runserver 0.0.0.0:8000