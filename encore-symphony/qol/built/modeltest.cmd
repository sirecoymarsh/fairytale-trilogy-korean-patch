@echo off
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" x86 >nul
if errorlevel 1 exit /b 1
cl /nologo /O2 /EHsc /MT /std:c++17 /utf-8 /I. "..\record_test.cpp" /link /OUT:record_test.exe user32.lib
if errorlevel 1 exit /b 1
record_test.exe
