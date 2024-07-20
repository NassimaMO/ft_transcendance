#!/bin/sh
cd srcs
if [ "$DEBUG" -eq 1 ]; then
    python3 manage.py makemigrations
    python3 manage.py migrate
    python3 manage.py runserver 0.0.0.0:8000
    #python manage.py createsuperuser --username admin --email admin@example.com
else
    python3 manage.py collectstatic --no-input
    python3 manage.py migrate
    daphne -b 0.0.0.0 -p 8000 transcendance.asgi:application
fi
