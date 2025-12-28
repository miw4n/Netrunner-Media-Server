@echo off
title Netrunner Media Suite

echo =========================================
echo    INITIALIZING NETRUNNER SYSTEMS
echo =========================================

:: Lancer le tagging dans une nouvelle fenêtre
echo [+] Starting Marathon Tagging...
start "Marathon Tagging" cmd /k "python scripts/marathon_tagging.py"

:: Lancer les stats dans une autre nouvelle fenêtre
echo [+] Starting Real-time Stats...
start "Media Stats" cmd /k "python scripts/stat.py & pause"

echo =========================================
echo    SYSTEMS ARE RUNNING IN SEPARATE NODES
echo =========================================
pause