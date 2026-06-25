import os
import subprocess
import sys

def package():
    print("Starting packaging process...")
    
    # dependencies check
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Define the command
    # --onefile: Create a single executable
    # --noconsole: Don't show terminal window (optional, maybe keep it for debugging for now)
    # --add-data: Include templates and static files
    # Note: On Windows, use ; as separator for add-data
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name", "ArchiveSystem",
        "--add-data", "templates;templates",
        "--add-data", "static;static",
        "--hidden-import", "pyodbc",
        "--hidden-import", "waitress",
        "wsgi.py"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == "__main__":
    package()
