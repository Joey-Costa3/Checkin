#!/bin/bash

if [[ $# -ne 1 ]]; then
	echo "usage: $0 <database_name>"
	exit 1
fi

sudo apt install python3.5 python3-pip postgresql

sudo su - postgres -c "psql -c\"
CREATE DATABASE $1
\""

sudo pip3 install django==1.10 psycopg2

python3.5 ../manage.py makemigrations
python3.5 ../manage.py migrate
python3.5 ../manage.py collectstatic

printf "would you like to create a superuser for admnistration purposes (Y/n)? "
read var
if [[ "$var" != 'n' ]]; then
	python3.5 ../manage.py createsuperuser
fi

echo "installation complete! Be sure to modify the DATABASES variable in attendance_tracker/settings.py with the postgres user's password and the correct database name"
