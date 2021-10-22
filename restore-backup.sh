#!/bin/bash
CONTAINER=markedsspillet_db_1

help() {
    echo "This command restores a backup of the Postgres database."
    echo ""
    echo "Example:"
    echo "  ./restore-backup.sh ./backups/weekly/app-202142.sql.gz"
}

do_restore() {
    source .env.dev
    gzip -dc $FILENAME | docker exec --interactive $CONTAINER psql --username=$POSTGRES_USER --dbname=$POSTGRES_DB -W
}

if [ "$1" != "" ]
then
    echo "Preparing to restore from database backup: $1"
    echo "NOTE: This operation is destructive and cannot be undone."
    read -p "Are you sure you want to restore the database from $1? (y/n) " -r
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        read -p "Are you really sure? (y/n) " -r
        if [[ $REPLY =~ ^[Yy]$ ]]
        then
            echo ""
            FILENAME=$1
            do_restore
        fi
    fi
else
    help
fi
