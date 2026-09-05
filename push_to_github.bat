@echo off
echo =======================================================
echo Pushing code to GitHub: smart-hostel-system23
echo =======================================================
cd /d "%~dp0"

echo [1/3] Clearing old cached GitHub credentials...
cmdkey /delete:git:https://github.com >nul 2>&1
git credential reject https://github.com >nul 2>&1

echo [2/3] Preparing files and main branch...
git add .
git commit -m "Push smart hostel booking system" >nul 2>&1
git branch -M main

echo [3/3] Pushing to GitHub...
echo (If a browser window opens, click 'Sign in with your browser' / 'Authorize')
git push -u origin main --force

echo.
echo =======================================================
echo Process finished!
echo =======================================================
pause
