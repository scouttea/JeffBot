#!/usr/bin/env bash

set -e

docker build --tag discordbot .
docker run -it discordbot


# This is for when no docker
#parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
#cd "$parent_path"
#
#modules=$(echo "$(python3 -m pip freeze)")
#
#for req in $(cat requirements.txt); do
#  echo "Checking for requirement $req"
#  if echo $modules | grep -vq $req; then
#    python3 -m pip install $req
#  fi
#done
#
#python3 bot/bot.py

