#!/bin/bash

python3.5 manage.py dbrestore
python3.5 manage.py makemigrations
python3.5 manage.py migrate
