@echo off
echo ==============================================
echo Pushing code to GitHub: smart-hostel-system23
echo ==============================================
cd /d "%~dp0"

git add .
git commit -m "Push smart hostel booking system"
git branch -M main
git push -u origin main --force

echo.
echo ==============================================
echo Push process completed! Press any key to exit.
echo ==============================================
pause
