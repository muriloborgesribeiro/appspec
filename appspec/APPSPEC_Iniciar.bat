@echo off
chcp 65001 >nul 2>&1
title APPSPEC - Inicializando Sistema...
color 0B
echo.
echo  ============================================================
echo   APPSPEC -- Inicializando Sistema de Diagnostico
echo   Aguarde enquanto o sistema e preparado...
echo  ============================================================
echo.
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File "%~dp0launcher.ps1"
