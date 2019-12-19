#!/bin/bash
if ! [ -d ../output/ ]; then
  echo Creating output/ subdir
  mkdir ../output/
fi
docker-compose run wildland-model
