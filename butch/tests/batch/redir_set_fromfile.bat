echo my-input > input.txt
echo %errorlevel%
set /p stored=stdout prompt < input.txt
echo %errorlevel%
echo %stored%
echo %errorlevel%
