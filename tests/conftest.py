"""Pytest configuration and shared fixtures."""

import pytest
import tempfile
import os
import shutil


@pytest.fixture
def temp_repo():
    """Create a temporary repository structure for testing."""
    temp_dir = tempfile.mkdtemp()
    
    # Create a basic repository structure
    os.makedirs(os.path.join(temp_dir, "src"))
    os.makedirs(os.path.join(temp_dir, "tests"))
    os.makedirs(os.path.join(temp_dir, "docs"))
    os.makedirs(os.path.join(temp_dir, ".git"))
    os.makedirs(os.path.join(temp_dir, "__pycache__"))
    
    # Create various files
    files = {
        "README.md": "# Test Repository\n\nThis is a test.",
        "setup.py": 'from setuptools import setup\n\nsetup(name="test")',
        ".gitignore": "__pycache__/\n*.pyc",
        "requirements.txt": "pytest>=7.0\nrequests>=2.0",
        "src/__init__.py": "",
        "src/main.py": 'def main():\n    print("Hello")\n',
        "src/utils.py": 'def helper():\n    return 42\n',
        "tests/test_main.py": 'def test_main():\n    assert True\n',
        "docs/README.md": "# Documentation\n",
        "data.csv": "name,value\ntest,123\ntest2,456\n",
        "config.json": '{"key": "value", "number": 42}',
    }
    
    for filepath, content in files.items():
        full_path = os.path.join(temp_dir, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_file():
    """Create a temporary file that's automatically cleaned up."""
    fd, path = tempfile.mkstemp()
    os.close(fd)
    
    yield path
    
    try:
        os.unlink(path)
    except FileNotFoundError:
        pass