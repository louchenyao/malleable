#! /bin/bash

set -e

cd ..

git fetch --all
git reset --hard origin/master

docker-compose build
docker-compose down
docker-compose up -d
