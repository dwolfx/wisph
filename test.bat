@echo off
chcp 65001 > nul
title Testes OpenWhispr (pytest)
cd /d "%~dp0"
"%~dp0.venv\Scripts\python.exe" -m pytest -v
pause
