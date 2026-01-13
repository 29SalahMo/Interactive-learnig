@echo off
cd /d "%~dp0"
git init
git remote add origin https://github.com/29SalahMo/Interactive-learnig.git
git add .
git commit -m "Initial commit: Interactive English Learning Quiz System"
git branch -M main
git push -u origin main
pause
