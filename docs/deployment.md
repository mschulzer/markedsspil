Deployment for Markedsspillet
=============================

Docker setup for development
----------------------------
For development we run the following services as docker-containers:

 - `db`: PostgreSQL (w. db in a docker volume)
 - `web`: The development django server (python manage.py runserver)

The `web` container executes `entrypoint.dev.sh` on start-up which:
 1. Resets the database entirely
 2. Runs migrations for the database
 3. Collects static files
 4. Generate translation files
 5. Populate a test-database
 6. Runs the Django development webserver exposed on port 8000

The database is reset in production to ensure that we use the same
starting point for any manual tests that we do.

Docker setup in production
--------------------------
In production we run the following services as docker containers:
 - `db`: PostgreSQL (w. db in a docker volume)
 - `web`: Gunicorn to serve Django files on port 8000
 - `nginx`: Nginx on port 80, in front of Gunicorn and to serve static files
 - `pgbackups`: prodrigestivill/postgres-backup-local: an image that automatically makes backups every night

The `web` container executes `entrypoint.prod.sh` on start-up which:
 1. Runs migrations for the database
 2. Collects static files
 3. Generate translation files
 4. Runs the Gunicorn server exposed on port 8000

Backups
-------
Backups are written to the local directory `backups`. The backups are
not replicated to any other servers (perhaps could be set up in the
future with rsync.net for example)

New backups are made every day at midnight. Older backups are removed,
such that we keep:
 - daily backups a week back are kept
 - weekly backups 4 weeks back are kept
 - monthly backups 6 months are kept

(these settings are configured in `docker-compose.prod.yml`

You can manually backup the database (e.g. before performing
maintenance work on the server), using the following command:

```
make production_create_backup
```

NOTE: The backup-directory `backups` has it's ownership set to user-id
999 and group-id 999 OUTSIDE the docker container (`chown -R 999:999
./backups`). The same ownership rights are mapped to the mounted
directory INSIDE the docker-container, where 999:999 maps to the
`postgres` user. This is necessary for the backup-script to be able to
write to the directory. See also documentation for
`prodrigestivill/postgres-backup-local`

Restoring a backup
------------------

To restore a backup, invoke the script `./restore-backup.sh` with a
given backup-file as argument. For example:
 
```
./restore-backup.sh ./backups/weekly/app-202142.sql.gz
```

.env file
---------

To hide secret keys, and allow different settings in development and
production, we use `.env` files. Examples for both production and development below:
o
Example .env file for production (*.env.prod*)
```
SECRET_KEY=*************
DEBUG=0
DJANGO_ALLOWED_HOSTS="localhost 127.0.0.1 [::1] .markedsspillet.dk web"
COMPOSE_PROJECT_NAME=market_production
EMAIL_HOST=smtp.eu.mailgun.org
EMAIL_HOST_USER=mailgun_username@mg.domain.com
EMAIL_HOST_PASSWORD=****************
EMAIL_PORT=587
POSTGRES_HOST=db
POSTGRES_DB=app
POSTGRES_USER=postgres
POSTGRES_PASSWORD=***************
```

Example .env file for development (*.env.dev*)
```
SECRET_KEY=*************
DEBUG=1
DJANGO_ALLOWED_HOSTS="localhost 127.0.0.1 [::1]"
COMPOSE_PROJECT_NAME=market_dev
EMAIL_HOST=
EMAIL_HOST_USER=
EMAIL_HOST_PASS=
EMAIL_PORT=
POSTGRES_HOST=db
POSTGRES_DB=app
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```
