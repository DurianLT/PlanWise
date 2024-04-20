@echo off
cd /d %~dp0/planWise
python manage.py makemigrations
python manage.py migrate
pause
