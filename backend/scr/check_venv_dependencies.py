import os
import subprocess

# Project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Path to requirements file
REQUIREMENTS_FILE = os.path.join(PROJECT_ROOT, "requirements.txt")

def get_installed_packages():
    """Retrieve all installed Python dependencies in the current virtual environment."""
    result = subprocess.run(["pip", "freeze"], capture_output=True, text=True, check=True)
    installed_packages = set(line.strip() for line in result.stdout.splitlines())
    return installed_packages

def get_required_packages():
    """Read the dependencies listed in requirements.txt."""
    if not os.path.exists(REQUIREMENTS_FILE):
        print(f"⚠️  Warning: {REQUIREMENTS_FILE} not found. A new requirements.txt will be created.")
        return set()
    
    with open(REQUIREMENTS_FILE, "r") as f:
        required_packages = set(line.strip() for line in f.readlines() if line.strip())
    
    return required_packages

def install_missing_packages(missing_packages):
    """Install missing dependencies that are listed in requirements.txt but not installed in the venv."""
    if missing_packages:
        print(f"📦 Installing missing dependencies: {', '.join(missing_packages)}")
        subprocess.run(["pip", "install", *missing_packages], check=True)
    else:
        print("✅ No missing dependencies found.")

def update_requirements_file(installed_packages):
    """Update requirements.txt to reflect the currently installed packages in the virtual environment."""
    print("🔄 Updating requirements.txt ...")
    with open(REQUIREMENTS_FILE, "w") as f:
        f.write("\n".join(sorted(installed_packages)) + "\n")
    print("✅ requirements.txt has been updated.")

def main():
    installed_packages = get_installed_packages()
    required_packages = get_required_packages()

    missing_packages = required_packages - installed_packages

    install_missing_packages(missing_packages)

    # Re-fetch installed packages and update requirements.txt
    installed_packages = get_installed_packages()
    update_requirements_file(installed_packages)

    print("🎯 Dependency check and update completed!")

if __name__ == "__main__":
    main()
