#! /bin/bash

set -e

cd ..
git pull
docker-compose build
docker-compose down
docker-compose up -d
