@echo off
title Calculadora Altamente Profissional
cd /d "%~dp0"
if exist "venv\Scripts\pythonw.exe" (
    start "" "venv\Scripts\pythonw.exe" "main.py"
) else (
    echo [ERRO] O ambiente virtual (venv) nao foi encontrado!
    echo Por favor, certifique-se de que as dependencias foram instaladas.
    pause
)
