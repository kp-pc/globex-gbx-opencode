@echo off
cd /d "%~dp0electron"
echo Installing Electron dependencies...
call npm install
if %errorlevel% neq 0 (
    echo npm install failed. Make sure Node.js is installed.
    pause
    exit /b 1
)
echo Starting Globex GBX Desktop...
npm start
