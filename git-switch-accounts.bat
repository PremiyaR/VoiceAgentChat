@echo off
echo Git Account Switcher
echo ===================
echo.
echo Choose an account:
echo 1. Personal Account (PremiyaRajani)
echo 2. Work Account (rajani@genius-germany.de)
echo.
set /p choice="Enter your choice (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo Switching to Personal Account...
    git config user.name "PremiyaR"
    git config user.email "rajanipremiya@gmail.com"
    echo.
    echo Personal account configured:
    echo Username: PremiyaRajani
    echo Email: rajanipremiya@gmail.com
    echo.
    echo You can now push to your personal repositories.
    echo.
) else if "%choice%"=="2" (
    echo.
    echo Switching to Work Account...
    git config user.name "PremiyaRajani"
    git config user.email "rajani@genius-germany.de"
    echo.
    echo Work account configured:
    echo Username: PremiyaRajani
    echo Email: rajani@genius-germany.de
    echo.
    echo You can now push to your work repositories.
    echo.
) else (
    echo Invalid choice. Please run the script again.
    pause
    exit /b 1
)

echo Current Git configuration:
git config user.name
git config user.email
echo.
pause
