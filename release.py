#!/usr/bin/env python3
import re
import subprocess
import sys
from pathlib import Path


def get_current_version():
    """Get current version from setup.py."""
    setup_py = Path("setup.py").read_text()
    match = re.search(r'version="(\d+\.\d+\.\d+)"', setup_py)
    return match.group(1) if match else None


def update_version(new_version):
    """Update version in setup.py and __init__.py."""
    # Update setup.py
    setup_py = Path("setup.py").read_text()
    updated_setup = re.sub(
        r'version="(\d+\.\d+\.\d+)"', f'version="{new_version}"', setup_py
    )
    Path("setup.py").write_text(updated_setup)

    # Update __init__.py
    init_py = Path("repo_serializer/__init__.py").read_text()
    updated_init = re.sub(
        r'__version__ = "(\d+\.\d+\.\d+)"', f'__version__ = "{new_version}"', init_py
    )
    Path("repo_serializer/__init__.py").write_text(updated_init)


def run_command(cmd, error_msg=None):
    """Run a command and handle errors."""
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        if error_msg:
            print(f"Error: {error_msg}")
            print(f"Command failed with exit code {e.returncode}")
        return False


def main():
    # Get current version
    current_version = get_current_version()
    if not current_version:
        print("Error: Could not find current version in setup.py")
        return 1

    print(f"Current version: {current_version}")

    # Get new version
    new_version = input("Enter new version (or press Enter to cancel): ").strip()
    if not new_version:
        print("Release cancelled")
        return 0

    if not re.match(r"^\d+\.\d+\.\d+$", new_version):
        print("Error: Version must be in format X.Y.Z")
        return 1

    # Confirm
    print("\nThis will:")
    print(f"1. Update version from {current_version} to {new_version}")
    print("2. Commit and push changes")
    print(f"3. Create and push tag v{new_version}")
    confirm = input("\nProceed? (y/N): ").lower()
    if confirm != "y":
        print("Release cancelled")
        return 0

    # Update version numbers
    print("\nUpdating version numbers...")
    update_version(new_version)

    # Run tests
    print("\nRunning tests...")
    if not run_command(["python", "test_dev.py"], "Tests failed"):
        return 1

    # Git commands
    print("\nCommitting changes...")
    if not run_command(["git", "add", "setup.py", "repo_serializer/__init__.py"]):
        return 1
    if not run_command(["git", "commit", "-m", f"Bump version to {new_version}"]):
        return 1

    print("\nPushing to remote...")
    if not run_command(["git", "push"]):
        return 1

    print("\nCreating and pushing tag...")
    if not run_command(["git", "tag", f"v{new_version}"]):
        return 1
    if not run_command(["git", "push", "origin", f"v{new_version}"]):
        return 1

    print(f"\n✨ Version {new_version} has been released!")
    print("\nNext steps:")
    print("1. Go to GitHub and create a new release from the tag")
    print("2. GitHub Actions will automatically publish to PyPI")

    return 0


if __name__ == "__main__":
    sys.exit(main())
