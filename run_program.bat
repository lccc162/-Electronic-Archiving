@echo off
set "PYTHON_PATH=C:\ZKBioTime\Python37\python.exe"
set "USER_SITE=C:\Users\itadmin\AppData\Roaming\Python\Python37\site-packages"
set "PYTHONPATH=%USER_SITE%;%PYTHONPATH%"

echo Checking Flask installation...
"%PYTHON_PATH%" -m flask --version
if %errorlevel% neq 0 (
    echo Flask not found in standard paths, checking user site...
    "%PYTHON_PATH%" -c "import flask; print('Flask version:', flask.__version__)"
)

echo.
echo Starting Archive Program on http://localhost:8080 ...
"%PYTHON_PATH%" wsgi.py
pause
