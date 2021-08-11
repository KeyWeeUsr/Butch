echo start
echo good1
goto mylabel3

:mylabel0
echo good6
goto :eof

:mylabel1
echo good3
goto mylabel4

:mylabel2
echo good5
goto mylabel0

:mylabel3
echo good2
goto mylabel1

:mylabel4
echo good4
goto mylabel2

echo bad
