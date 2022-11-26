#!/bin/sh

python3 manage.py migrate --no-input
python3 manage.py initadmin
python3 manage.py collectstatic --no-input
python3 manage.py runserver 0.0.0.0:8080
