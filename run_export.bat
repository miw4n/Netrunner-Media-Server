@echo off
title TMDB Movie CSV Generator
echo ===============================
echo  TMDB Movie CSV Generator
echo   
echo ===============================
echo.

REM ---- CONFIG ----
set TMDB_API_KEY=PUT_YOUR_API_KEY_HERE
set PYTHON_EXE=python

echo Checking Python...
%PYTHON_EXE% --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    pause
    exit /b
)

echo Installing dependencies...
%PYTHON_EXE% -m pip install --quiet requests tqdm ollama fastmcp

echo Starting export...
%PYTHON_EXE% scripts/export_sql_fast.py %TMDB_API_KEY%

echo.
echo Export finished.
pause

