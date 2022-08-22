#!/bin/sh

# echo $SHELL

# alias python='python3'

if [ "$DATABASE" = "du_db" ]
then
    echo "Waiting for du_db..."

    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py flush --no-input
python manage.py makemigrations authentication
python manage.py migrate
# python manage.py test
            
exec "$@"