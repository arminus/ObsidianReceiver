#!/bin/bash

export LC_ALL=C.UTF-8
export LANG=C.UTF-8

if [ -z "$SERVER_PORT" ]; then
    SERVER_PORT=8045
fi

uvicorn --host 0.0.0.0 --port $SERVER_PORT server:app
