@echo off
title psql.exe
echo Restore database
echo.

"C:\Program Files\PostgreSQL\14\bin\psql.exe" -d postgres -U postgres -f database.dump

echo.
pause
exit /b %errorlevel%
