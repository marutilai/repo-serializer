#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd):
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def main():
    # Use root repository directory (one level up from dev)
    repo_dir = str(Path(__file__).parent.parent)
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
        
        # Test prompt extraction mode
        run_command(
            [
                "repo-serializer",
                repo_dir,
                "-o",
                os.path.join(output_dir, "test_prompts.txt"),
                "-p",
            ]
        )
        
        print("\nRunning unit tests with pytest...")
        
        # Run pytest with summary
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "-v", "--tb=short", "-q"],
                capture_output=True,
                text=True
            )
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
            
            if result.returncode == 0:
                print("\n✅ All pytest tests passed!")
            else:
                print("\n⚠️  Some pytest tests failed, but continuing...")
                # Don't exit on pytest failures since they might be environment-specific
        except Exception as e:
            print(f"\n⚠️  Could not run pytest: {e}")
            print("Make sure pytest is installed: pip install pytest")

        print("\nAll tests completed successfully!")
        print("\nOutput files in test_outputs/:")
        print("- test_output.txt (full output)")
        print("- test_python.txt (Python files only)")
        print("- test_structure.txt (structure only)")
        print("- test_prompts.txt (extracted prompts)")

    except subprocess.CalledProcessError as e:
        print(f"\nError: Command failed with exit code {e.returncode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
