#!/bin/bash

cd "$(dirname "$0")"
cd server && python3 -m pip install -r requirements.txt && cd ..
cd client && npm install && cd ..

PID_LIST=''

cd server
python3 run.py & pid=$!
PID_LIST+=" $pid"
cd ..

cd client
npm start & pid=$!
PID_LIST+=" $pid"
cd ..

trap "kill $PID_LIST" SIGINT
wait $PID_LIST
