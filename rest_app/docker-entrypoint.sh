#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER
do
  echo "Waiting for PostgreSQL to start..."
  sleep 2
done
echo "PostgreSQL started"


echo "Applying migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Creating superuser..."
python manage.py createsuperuser --noinput || true

echo "Starting application..."
exec python manage.py runserver 0.0.0.0:8000