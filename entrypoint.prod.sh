#!/bin/bash

set -e

echo "${0}: running production server."
pipenv run gunicorn config.wsgi:application --bind 0.0.0.0:8000
