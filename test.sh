#!/bin/bash

# Get the latest version from setup.py
VERSION=$(grep -E "version=\"[0-9]+\.[0-9]+\.[0-9]+\"" setup.py | grep -Eo "[0-9]+\.[0-9]+\.[0-9]+")

echo "Building and testing repo-serializer version $VERSION"

# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build package
python setup.py sdist bdist_wheel

# Install the wheel (using the version we found)
pip install dist/repo_serializer-$VERSION-py3-none-any.whl --force-reinstall

# Run a test
echo "Testing with sample repository..."
repo-serializer /Users/maruti/Desktop/repo_test -o test_output.txt

echo "Done! Check test_output.txt for results" 