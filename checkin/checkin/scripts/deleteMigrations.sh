#!/bin/bash
sudo su - postgres -c "psql -c \"delete from django_migrations where app='attendance';\""
rm attendance/migrations/0*.py
rm attendance/migrations/__pycache__/0*.py
