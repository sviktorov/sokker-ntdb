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

# export game sql example

SELECT
G.g_id AS id,
CASE
WHEN G.c_id = 1 THEN 6
WHEN G.c_id = 2 THEN 7
WHEN G.c_id = 3 THEN 8
WHEN G.c_id = 4 THEN 9
WHEN G.c_id = 5 THEN 10
ELSE G.c_id -- This ensures that other values remain unchanged
END AS c_id,
T1.t_sokker_id AS t_id_h,
T2.t_sokker_id AS t_id_v,
G.g_status,
G.group_id,  
 G.goals_home,
G.goals_away,
G.cup_round,
G.matchID,
G.playoff_position
FROM `games` AS G
JOIN `teams` AS T1 ON G.t_id_h = T1.t_id
JOIN `teams` AS T2 ON G.t_id_v = T2.t_id;
