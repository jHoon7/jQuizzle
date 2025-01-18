#!/bin/bash

echo "Starting Pillow installation script..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed!"
    echo "Please install Python from https://www.python.org/downloads/"
    echo "Or use: brew install python3"
    read -p "Press enter to exit"
    exit 1
fi

# Show Python version
echo "Found Python version:"
python3 --version
echo

# Try to install Pillow
echo "Installing Pillow module..."
python3 -m pip install --user Pillow

if [ $? -ne 0 ]; then
    # If pip install fails, try updating pip first
    echo "First attempt failed. Updating pip..."
    python3 -m pip install --upgrade pip
    
    # Try installing Pillow again
    echo "Retrying Pillow installation..."
    python3 -m pip install --user Pillow
    
    if [ $? -ne 0 ]; then
        echo "Failed to install Pillow. Please check your internet connection and try again."
        read -p "Press enter to exit"
        exit 1
    fi
fi

# Verify installation
echo "Verifying installation..."
if python3 -c "from PIL import Image; print('Pillow verification successful!')"; then
    echo "SUCCESS: Pillow has been successfully installed!"
else
    echo "WARNING: Pillow was installed but verification failed"
    echo "Please try running 'python3 -m pip install --user Pillow' manually"
fi

echo
echo "Installation process complete."
read -p "Press enter to exit"