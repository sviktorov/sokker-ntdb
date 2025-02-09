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



 psql -U debug  -h localhost -p 5432 -d  sokker_web2 < structure.sql

 pg_dump -U sokker_web -h localhost -p  5432 --schema-only -f structure.sql sokker_web


source /Users/svetlozar.viktorov/Projects/envs/sokker/env/bin/activate
source load_env.sh 

docker-compose up db -d

# NTDB TEAM STATS
 python manage.py teams_nt_attribute_stat --stat-type=team --stat-field=ntmatches
 python manage.py teams_nt_attribute_stat --stat-type=team --stat-field=ntassists
 python manage.py teams_nt_attribute_stat --stat-type=team --stat-field=ntgoals

python manage.py teams_nt_attribute_stat --stat-type=youth --stat-field=ntmatches
python manage.py teams_nt_attribute_stat --stat-type=youth --stat-field=ntassists
python manage.py teams_nt_attribute_stat --stat-type=youth --stat-field=ntgoals

# CL GAMES FETCH
python manage.py fetch_cl_games --c_id=460

# CL STANDINGS
python manage.py update_standings_arcades

# NTDB update active players
python manage.py sokker_update_public

# Clear cache
python manage.py clear_cache
