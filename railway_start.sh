#!/usr/bin/env sh
set -eu

python manage.py migrate --noinput
python manage.py seed_demo_data
python manage.py collectstatic --noinput
gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-8080}"
