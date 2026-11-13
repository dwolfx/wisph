@echo off
chcp 65001 > nul
title OpenWhispr Windows (Debug Console)
cd /d "%~dp0"

set PYTHONUNBUFFERED=1

echo ====================================================
echo  OpenWhispr Windows (Voice Flow) - Modo Console
echo  Criado por Victor Hugo e Maya
echo ====================================================
echo.

"%~dp0.venv\Scripts\python.exe" -u "%~dp0main.py"
pause
