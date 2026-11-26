@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe python -m venv .venv
if errorlevel 1 goto fail
call .venv\Scripts\activate.bat
python -m pip install -r requirements.txt || goto fail
python manage.py makemigrations api || goto fail
python manage.py migrate || goto fail
python populate_data.py || goto fail
python manage.py check || goto fail
python manage.py runserver
pause
exit /b
:fail
echo Error durante la preparacion.
pause
