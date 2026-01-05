#!/bin/sh

# Removed wait loop for Supabase/Remote DB


echo "Running migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --no-input

exec "$@"
