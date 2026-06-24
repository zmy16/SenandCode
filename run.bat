@echo off
title SenandCode
echo.
if "%~1"=="" (
    python -m senandika
) else (
    python -m senandika "%~1"
)
echo.
echo Tekan tombol apapun untuk menutup...
pause >nul
