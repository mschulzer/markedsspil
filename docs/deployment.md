Deployment for Markedsspillet
=============================

Docker setup for development
----------------------------
For development we use a simple docker-container which:
 - mounts a docker volume on /db
 - flushes and runs migrations for the database
 - collect static files
 - runs the Django development webserver exposed on port 8000

Docker setup in production
--------------------------
In production we use:
 - Gunicorn to serve Django files on port 8000
 - Nginx on port 80, in front of Gunicorn and to serve static files
 - A docker volume for the database mounted at /db
 
Before Gunicorn are launched, we run migrations and collect static
files. (We don't flush the database)

.env file
---------

To hide secret keys, and allow different settings in development and
production, we use `.env` files. Examples for both production and development below:
o
Example .env file for production (*.env.prod*)
```
SECRET_KEY=*************
DEBUG=0
DJANGO_ALLOWED_HOSTS="localhost 127.0.0.1 [::1] domain.example.com web"
COMPOSE_PROJECT_NAME=market_production
EMAIL_HOST=smtp.eu.mailgun.org
EMAIL_HOST_USER=mailgun_username@mg.domain.com
EMAIL_HOST_PASSWORD=****************
EMAIL_PORT=587
```

Example .env file for development (*.env.dev*)
```
SECRET_KEY=*************
DEBUG=1
DJANGO_ALLOWED_HOSTS="localhost 127.0.0.1 [::1]"
COMPOSE_PROJECT_NAME=market_development
```
