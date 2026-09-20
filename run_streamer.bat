@echo off
title Netra AI - Edge-to-Cloud Video Streamer
cd /d "%~dp0"

echo ========================================================
echo   Netra AI - Edge-to-Cloud Live Streamer
echo ========================================================
echo.

IF EXIST "..\venv\Scripts\python.exe" (
    "..\venv\Scripts\python.exe" stream_to_cloud.py %*
) ELSE IF EXIST "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" stream_to_cloud.py %*
) ELSE (
    python stream_to_cloud.py %*
)

pause
