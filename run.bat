@echo off
REM MC Bot Suite — единый запуск
cd /d "%~dp0"

REM Проверка Python
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python не найден в PATH.
    echo Установите Python 3.11+ с https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Проверка Node
where node >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Node.js не найден в PATH.
    echo Установите Node.js 18+ с https://nodejs.org/
    pause
    exit /b 1
)

python run.py
if errorlevel 1 (
    echo.
    echo [ERROR] Запуск завершился с ошибкой.
    pause
)