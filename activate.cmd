IF EXIST "%~dp0venv" GOTO ACTIVATE
py -3 -mvenv "%~dp0venv"
"%~dp0venv\Scripts\pip.exe" install -r "%~dp0requirements.txt"
:ACTIVATE
CALL "%~dp0venv\Scripts\activate.bat"
