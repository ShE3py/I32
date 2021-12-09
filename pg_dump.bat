@echo off
title pg_dump.exe
echo Dump database
echo.

"C:\Program Files\PostgreSQL\14\bin\pg_dump.exe" --blobs --clean --if-exists -d postgres -U postgres -f database.dump

echo.
pause
exit /b %errorlevel%
