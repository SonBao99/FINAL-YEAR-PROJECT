import sys
import os
from pathlib import Path

def check_environment():
    venv_path = Path(sys.prefix)
    project_path = Path.cwd()
    interpreter_path = Path(sys.executable)
    
    print('\n=== Environment Details ===')
    print(f"Interpreter path: {interpreter_path}")
    print(f"Working directory: {project_path}")
    print(f"Virtual env active: {'VIRTUAL_ENV' in os.environ}")
    print(f"Virtual env path: {os.environ.get('VIRTUAL_ENV', 'Not found')}")
    print(f"Python version: {sys.version.split()[0]}")
    print('=========================\n')

if __name__ == "__main__":
    check_environment()