"""Test cases for filters module."""

import pytest
from repo_serializer.filters import should_skip


class TestShouldSkip:
    """Test the should_skip function."""
    
    def test_skip_hidden_files(self):
        """Hidden files starting with . should be skipped."""
        assert should_skip(".gitignore") is True
        assert should_skip(".env") is True
        assert should_skip("regular_file.py") is False
    
    def test_skip_directories(self):
        """Test directory skipping."""
        assert should_skip("__pycache__", is_dir=True) is True
        assert should_skip("node_modules", is_dir=True) is True
        assert should_skip("src", is_dir=True) is False
    
    def test_skip_file_extensions(self):
        """Test file extension skipping."""
        assert should_skip("binary.exe") is True
        assert should_skip("image.jpg") is True
        assert should_skip("archive.zip") is True
        assert should_skip("code.py") is False
        assert should_skip("data.json") is False
    
    def test_skip_specific_files(self):
        """Test skipping specific filenames."""
        assert should_skip("package-lock.json") is True
        assert should_skip("yarn.lock") is True
        assert should_skip("package.json") is False
    
    def test_language_filtering_python(self):
        """Test Python language filtering."""
        # Python files should not be skipped
        assert should_skip("script.py", language="python") is False
        assert should_skip("notebook.ipynb", language="python") is False
        
        # Non-Python files should be skipped
        assert should_skip("script.js", language="python") is True
        assert should_skip("style.css", language="python") is True
        
        # Python test files are now included (skip patterns removed)
        assert should_skip("test_module.py", language="python") is False
        assert should_skip("module_test.py", language="python") is False
    
    def test_language_filtering_javascript(self):
        """Test JavaScript language filtering."""
        # JavaScript files should not be skipped
        assert should_skip("app.js", language="javascript") is False
        assert should_skip("component.jsx", language="javascript") is False
        assert should_skip("module.ts", language="javascript") is False
        
        # Non-JavaScript files should be skipped
        assert should_skip("script.py", language="javascript") is True
        
        # JavaScript test files should be skipped
        assert should_skip("app.test.js", language="javascript") is True
        assert should_skip("app.spec.js", language="javascript") is True
    
    def test_full_path_patterns(self):
        """Test patterns that match against full paths."""
        # Test directory patterns with paths
        assert should_skip(".vite", is_dir=True, full_path="node_modules/.vite") is True
        # workflows itself is not in SKIP_DIRS, only specific patterns would match
        assert should_skip("workflows", is_dir=True, full_path=".github/workflows") is False
        # But .github would be skipped as it starts with .
        assert should_skip(".github", is_dir=True) is True
        
    def test_no_language_filtering(self):
        """Test behavior when no language filtering is applied."""
        # Normal files should not be skipped
        assert should_skip("script.py", language=None) is False
        assert should_skip("app.js", language=None) is False
        assert should_skip("data.json", language=None) is False
        
        # Binary files should still be skipped
        assert should_skip("binary.exe", language=None) is True