@echo off
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" x86 >nul
if errorlevel 1 exit /b 1
cl /nologo /O2 /EHsc /MT /std:c++17 /utf-8 /I. /LD "..\content_options.cpp" /link /OUT:FairytaleContent.dll /EXPORT:ContentAction=_ContentAction@8 user32.lib
