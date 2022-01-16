#!/bin/bash

OBS_SERVER_PORT=8045

docker kill obsreceiver
docker container rm obsreceiver

docker build -t obsreceiver .
docker run -d --name obsreceiver --env SERVER_PORT=$OBS_SERVER_PORT -p $OBS_SERVER_PORT:$OBS_SERVER_PORT -v $(pwd)/obsidian_conf:/root/obsidian_conf obsreceiver:latest
