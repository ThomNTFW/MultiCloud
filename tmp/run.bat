@echo off

cd server 
call python3 -m pip install -r requirements.txt 
cd ..

cd client 
call npm install 
cd ..

cd server
start python3 run.py
cd ..

cd client
start npm start
cd ..