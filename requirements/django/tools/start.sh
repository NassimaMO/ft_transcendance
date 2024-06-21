#!/bin/sh
cd srcs
if [ "$DEBUG" -eq 1 ]; then
    python3 manage.py makemigrations
    python3 manage.py migrate
    python3 manage.py runserver 0.0.0.0:8000
else
    python3 manage.py collectstatic --no-input
    python3 manage.py migrate
    gunicorn transcendance.wsgi:application --bind 0.0.0.0:8000
fi
