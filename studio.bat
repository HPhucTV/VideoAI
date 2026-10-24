@echo off
title OmniVideo Studio Local
chcp 65001 > nul
cls
echo Khoidong OmniVideo Studio Local...
powershell -ExecutionPolicy Bypass -NoProfile -File "%~dp0studio.ps1"
pause
