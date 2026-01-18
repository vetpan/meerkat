release: python manage.py migrate --noinput
web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
worker: celery -A config worker --loglevel=info --concurrency=1
