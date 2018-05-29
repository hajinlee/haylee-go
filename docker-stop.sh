#!/bin/sh

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

docker-compose -p haylee-go down
docker system prune --volumes -f

# get rid of any lingering .pid files
rm -f tmp/pids/*
