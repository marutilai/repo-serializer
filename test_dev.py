#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd):
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def main():
    # Use current repository directory
    repo_dir = str(Path(__file__).parent)
    output_dir = os.path.join(repo_dir, "test_outputs")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Clean and build
        run_command(["pip", "install", "-e", "."])

        print("\nTesting repo-serializer...")

        # Test basic functionality
        run_command(
            [
                "repo-serializer",
                repo_dir,
                "-o",
                os.path.join(output_dir, "test_output.txt"),
            ]
        )

        # Test Python-only mode
        run_command(
            [
                "repo-serializer",
                repo_dir,
                "-o",
                os.path.join(output_dir, "test_python.txt"),
                "--python",
            ]
        )

        # Test structure-only mode
        run_command(
            [
                "repo-serializer",
                repo_dir,
                "-o",
                os.path.join(output_dir, "test_structure.txt"),
                "-s",
            ]
        )

        print("\nAll tests completed successfully!")
        print("\nOutput files in test_outputs/:")
        print("- test_output.txt (full output)")
        print("- test_python.txt (Python files only)")
        print("- test_structure.txt (structure only)")

    except subprocess.CalledProcessError as e:
        print(f"\nError: Command failed with exit code {e.returncode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
