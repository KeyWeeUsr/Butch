:: run from test.py cwd assuming repo root
cd butch
cd tests
echo %errorlevel%
:: FNF
move nonexisting nonexisting
echo %errorlevel%

:: multi-FNF
move nonexisting nonexisting nonexisting
echo %errorlevel%

:: FNF to explicit dir
move nonexisting nonexisting nonexisting\
echo %errorlevel%

:: file renaming
move existing nonexisting
echo %errorlevel%
type nonexisting
echo %errorlevel%
del nonexisting
echo %errorlevel%

:: move to folder by wildcard
type first1
echo %errorlevel%
type first2
echo %errorlevel%

:: move multiple files to single file
move first* nonexisting
echo %errorlevel%
:: error

mkdir existing
echo %errorlevel%
move first* nonexisting\
echo %errorlevel%
move first* existing
echo %errorlevel%
cd existing
del first1
echo %errorlevel%
del first2
echo %errorlevel%
cd ..
rmdir existing
echo %errorlevel%
cd ..
cd ..
