#!/bin/bash

./scripts/deleteMigrations.sh
./scripts/dropTables.sh

python3.5 manage.py makemigrations
python3.5 manage.py migrate
./scripts/dbPopulate.sh

python3 manage.py createsuperuser
python3 manage.py collectstatic
