@echo off
title Leave Approval API Server (Port 3000)
cd /d "%~dp0"
echo ===================================================
echo  LEAVE APPROVAL SYSTEM: API SERVER
echo  Port: 3000
echo  Keep this window open while testing in Postman!
echo ===================================================
node server.js
pause
