@echo off
del build.bat > nul 2>&1
del files.txt > nul 2>&1
del /f *.manifest > nul 2>&1
del /f update* > nul 2>&1
del /s /f /q .\disk1\*.* > nul 2>&1
rd /s /q .\disk1 > nul 2>&1
del *.cab > nul 2>&1