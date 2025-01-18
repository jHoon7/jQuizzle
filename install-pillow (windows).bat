@echo off
echo Starting Pillow installation script...
echo.

:: Create a log file
echo Installation started at %date% %time% > install_log.txt

:: Check if Python is installed
echo Checking for Python installation...
python --version >> install_log.txt 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    echo This error has been logged to install_log.txt
    pause
    exit /b 1
)

:: Display Python version
python --version
echo.

:: Try to install Pillow using pip
echo Installing Pillow module...
python -m pip install --user Pillow >> install_log.txt 2>&1

if errorlevel 1 (
    :: If pip install fails, try updating pip first
    echo First attempt failed. Updating pip...
    python -m pip install --upgrade pip >> install_log.txt 2>&1
    
    :: Try installing Pillow again
    echo Retrying Pillow installation...
    python -m pip install --user Pillow >> install_log.txt 2>&1
    
    if errorlevel 1 (
        echo ERROR: Failed to install Pillow
        echo Please check install_log.txt for details
        echo Make sure you have internet connection
        pause
        exit /b 1
    )
)

:: Verify installation
echo Verifying installation...
python -c "from PIL import Image; print('Pillow verification successful!')" >> install_log.txt 2>&1
if errorlevel 1 (
    echo WARNING: Pillow was installed but verification failed
    echo Please try running 'python -m pip install --user Pillow' manually
    echo Check install_log.txt for details
) else (
    echo SUCCESS: Pillow has been successfully installed!
)

echo.
echo Installation process complete. Check install_log.txt for details.
echo.
pause