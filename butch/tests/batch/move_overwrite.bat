:: run from test.py cwd assuming repo root
cd butch
cd tests
echo %errorlevel%

type source\file1
type source\file2
type dest\file1
type dest\file2

move /Y source\* dest
echo %errorlevel%
type dest\file1
type dest\file2

rmdir source
echo %errorlevel%
del dest\file1
echo %errorlevel%
del dest\file2
echo %errorlevel%
rmdir dest
echo %errorlevel%
cd ..
cd ..
