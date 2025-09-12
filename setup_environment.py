import subprocess
import sys
import os
from pathlib import Path

def check_build_environment():
    print("\n=== Build Environment Check ===")
    
    # Check Python version
    print(f"Python: {sys.version.split()[0]}")
    
    # Check Visual Studio Build Tools and Visual C++
    vs_path = Path("C:/Program Files (x86)/Microsoft Visual Studio")
    vc_path = Path("C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC")
    
    if vs_path.exists():
        print("✓ Visual Studio Build Tools installed")
    else:
        print("✗ Visual Studio Build Tools not found")
        
    if vc_path.exists():
        print("✓ Visual C++ tools installed")
    else:
        print("✗ Visual C++ tools not found - Please install using Visual Studio Installer")
        print("  1. Open Visual Studio Installer")
        print("  2. Select 'Modify' on Visual Studio Build Tools 2022")
        print("  3. Check 'Desktop development with C++'")
        print("  4. Install and restart your computer")
    
    # Check CMake
    cmake_found = False
    try:
        cmake_output = subprocess.check_output(['cmake', '--version'], text=True)
        version_line = cmake_output.split('\n')[0]
        print(f"✓ CMake: {version_line}")
        cmake_found = True
    except:
        print("✗ CMake not found")
    

    # Check if the script is running in a virtual environment
    in_venv = "VITURAL_ENV" in os.environ
    if in_venv:
        print("✓ Virtual Environment: Active")
    else:
        print("✗ Virtual Environment: Not active - Please activate your virtual environment")
    
    # Return True only if all requirements are met
    return all([vs_path.exists(), vc_path.exists(), cmake_found, in_venv])

def install_dependencies():
    print("\n=== Installing Dependencies ===")
    
    # Install core dependencies first
    core_deps = [
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "opencv-python>=4.8.0"
    ]
    
    print("Installing core dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install"] + core_deps)
    
    # Install dlib separately
    print("\nInstalling dlib...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "dlib>=19.24.0"])
    
    # Install remaining dependencies
    print("\nInstalling remaining dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

if __name__ == "__main__":
    if check_build_environment():
        try:
            install_dependencies()
            print("\n✓ Setup completed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"\n✗ Error during installation: {e}")
    else:
        print("\n✗ Please fix environment issues before proceeding")
