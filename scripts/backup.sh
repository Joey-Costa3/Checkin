#!/bin/bash

#backup database
python3.5 manage.py dbbackup --clean
