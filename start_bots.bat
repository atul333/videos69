@echo off
echo ========================================
echo   Starting Videos Bot System
echo ========================================
echo.

echo [1/2] Starting Main Bot (Videos)...
start "Videos Bot - Main" python bot.py
timeout /t 2 /nobreak >nul

echo [2/2] Starting Admin Bot (Support)...
start "Videos Bot - Admin Support" python admin_bot.py
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo   Both Bots Started Successfully!
echo ========================================
echo.
echo Main Bot: @Videos1_69_bot
echo Admin Bot: @videos69Admin_Bot
echo Admin: @Deep12048
echo.
echo Press any key to exit...
pause >nul
