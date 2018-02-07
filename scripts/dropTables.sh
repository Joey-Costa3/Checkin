#!/bin/bash
tables=($(sudo su - postgres -c "psql -c '\dt'" | head -n -2 | tail -n +4 | awk '{print $3}' | tr "\n" " "))

for t in ${tables[@]}; do
	sudo su - postgres -c "psql -v ON_ERROR_STOP=0 -c \"drop table $t cascade;\""
done
