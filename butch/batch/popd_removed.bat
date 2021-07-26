cd %temp%
echo %errorlevel%
echo %cd%
mkdir butch-tmp-folder
echo %errorlevel%
echo %cd%
pushd butch-tmp-folder
echo %errorlevel%
echo %cd%
pushd ..
echo %errorlevel%
echo %cd%
rmdir butch-tmp-folder
echo %errorlevel%
echo %cd%
popd
echo %errorlevel%
echo %cd%
popd
echo %errorlevel%
echo %cd%
