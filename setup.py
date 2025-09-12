import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    
    # Core requirements
    requirements = [
        "numpy",
        "opencv-python",
        "requests"
    ]
    
    # Install core requirements first
    for req in requirements:
        print(f"Installing {req}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", req])
    
    # Try to install dlib
    print("\nAttempting to install dlib...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "dlib"])
        print("Successfully installed dlib!")
    except subprocess.CalledProcessError:
        print("Failed to install dlib. Please ensure you have:")
        print("1. Visual Studio Build Tools 2022 with C++ workload")
        print("2. CMake installed and in PATH")
        return False
    
    return True

if __name__ == "__main__":
    if install_requirements():
        print("\nAll dependencies installed successfully!")
    else:
        print("\nSome dependencies could not be installed.")