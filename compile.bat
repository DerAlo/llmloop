@echo off
REM MetaEditor Compile Script
REM Parameter: %1=MetaEditor.exe %2=Source.mq5 %3=LogFile %4=IncludePath

echo Kompiliere: %2
echo Log: %3
echo Include: %4

%1 /compile:%2 /log:%3 /inc:%4

echo Fertig. Exit Code: %ERRORLEVEL%
