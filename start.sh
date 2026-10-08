#!/bin/sh
set -e
uv run python library/manage.py migrate --noinput
uv run python library/manage.py seed_db --no-input
exec uv run gunicorn --chdir library config.wsgi:application --bind 0.0.0.0:${PORT:-10000}