:: @echo off
::
:: :: default status is 0
:: echo %errorlevel%
::
:: :: single wrapped command
:: (
::     ver > nul
:: )
:: :: zero
:: echo %errorlevel%
::
:: (
::     :: zero
::     ver > nul
::     :: non-zero
::     type nonexisting
:: )
:: :: non-zero
:: echo %errorlevel%
::
:: (
::     :: non-zero
::     type nonexisting
::     :: zero
::     ver > nul
:: )
:: :: zero
:: echo %errorlevel%
