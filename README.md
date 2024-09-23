# sokker-ntdb

sokker-ntdb

## Development

### Docker setup

create the containers:
`docker compose build`

run the created containers:
`docker compose up -d`

### Creating migrations

Access docker terminal:
`docker exec -it web bash`

> _(while in docker terminal)_

Create migrations :
`python manage.py makemigrations`

Create named migration
`python manage.py makemigrations pages -n migration_name`

(Make sure to run `make fmt` to autoformat the new migration)

## Deployment

flyctl deploy --no-extensions

fly apps open

## Fly.io

### Extending volume

fly volumes extend vol_4okjlz83y7m0k5xv --size 20

### Export fly.toml

fly config save -a mrcps-db-dev

### Access server of app

-a mrcps-web-uat

### run a process in a server machine

flyctl console -C bash

### remote connection to db proxy on localhost

fly proxy 5432 -a mrcps-db-dev

### connect in terminal

flyctl postgres connect -a mrcps-db-dev

### scale memory of machine

flyctl machine update 48ed164c7d0d78 --vm-memory 512 --app sokker-db

## PostGIS

### install on fly.io

https://trac.osgeo.org/postgis/wiki/UsersWikiPostGIS3UbuntuPGSQLApt

## install on server

apt update

apt install postgresql-15-postgis-3

## install in psql

ALTER DATABASE mrcps_dev SET search_path=public,postgis,contrib;
\connect mrcps_dev;

CREATE SCHEMA postgis;

CREATE EXTENSION postgis SCHEMA postgis;

fly ssh console --app
