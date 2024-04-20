@echo off
cd /d %~dp0
pip3 install -r requirements.txt
cd /d %~dp0/planWise
python manage.py makemigrations
python manage.py migrate
pause