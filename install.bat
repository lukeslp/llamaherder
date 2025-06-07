@echo off
REM LlamaHerder Installation Script for Windows
REM This script installs the LlamaHerder package with all dependencies

echo 🦙 LlamaHerder Installation Script
echo ==================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python 3 is required but not installed.
    echo Please install Python 3.8 or later from https://python.org and try again.
    pause
    exit /b 1
)

REM Check if pip is available
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip is required but not installed.
    echo Please install pip and try again.
    pause
    exit /b 1
)

echo 📦 Installing LlamaHerder package...

REM Install in development mode with all dependencies
pip install -e ".[all]"

if %errorlevel% neq 0 (
    echo ❌ Installation failed. Please check the error messages above.
    pause
    exit /b 1
)

echo ✅ Installation complete!
echo.
echo 🚀 You can now run:
echo    herd --help          # Show CLI help
echo    herd --gui           # Launch web interface
echo    herd                 # Interactive menu
echo.
echo 🔧 For development:
echo    pre-commit install   # Install git hooks
echo    pytest               # Run tests
echo.
echo 📚 Documentation: https://github.com/lukeslp/llamaherder#readme
pause 