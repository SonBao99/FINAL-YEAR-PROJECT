import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install {package}: {e}")
        return False

def main():
    print("Installing Attendance System Dependencies")
    print("=========================================")
    
    # Core packages that should install easily
    core_packages = [
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "sqlalchemy>=2.0.0",
        "python-multipart>=0.0.6",
        "websockets>=12.0",
        "aiofiles>=23.2.0"
    ]
    
    print("\nInstalling core packages...")
    for package in core_packages:
        install_package(package)
    
    # Try to install face_recognition (this might fail on Windows)
    print("\nAttempting to install face_recognition...")
    if not install_package("face_recognition>=1.3.0"):
        print("\n⚠️  face_recognition installation failed.")
        print("This is common on Windows. The system will work without it for now.")
        print("You can add face recognition later by:")
        print("1. Installing Visual Studio Build Tools")
        print("2. Installing CMake")
        print("3. Running: pip install face_recognition")
    
    print("\n✅ Installation complete!")
    print("\nTo start the system:")
    print("1. Run: python attendance_api_simple.py")
    print("2. Run: python kiosk_simple.py")
    print("3. Open web_dashboard.html in your browser")

if __name__ == "__main__":
    main()