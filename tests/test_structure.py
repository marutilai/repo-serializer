"""Test cases for structure generation module."""

import pytest
import tempfile
import os
from repo_serializer.structure import generate_ascii_structure


class TestGenerateAsciiStructure:
    """Test the generate_ascii_structure function."""
    
    def setup_method(self):
        """Set up test directory structure."""
        self.test_dir = tempfile.mkdtemp()
        
        # Create a simple directory structure
        os.makedirs(os.path.join(self.test_dir, "src"))
        os.makedirs(os.path.join(self.test_dir, "tests"))
        os.makedirs(os.path.join(self.test_dir, ".git"))  # Hidden dir
        
        # Create some files
        open(os.path.join(self.test_dir, "README.md"), 'w').close()
        open(os.path.join(self.test_dir, "setup.py"), 'w').close()
        open(os.path.join(self.test_dir, ".gitignore"), 'w').close()  # Hidden file
        open(os.path.join(self.test_dir, "src", "__init__.py"), 'w').close()
        open(os.path.join(self.test_dir, "src", "main.py"), 'w').close()
        open(os.path.join(self.test_dir, "tests", "test_main.py"), 'w').close()
    
    def teardown_method(self):
        """Clean up test directory."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_basic_structure(self):
        """Test basic ASCII structure generation."""
        result = generate_ascii_structure(self.test_dir)
        
        # Check that visible files and directories are included
        assert any("README.md" in line for line in result)
        assert any("setup.py" in line for line in result)
        assert any("src" in line for line in result)
        assert any("tests" in line for line in result)
        
        # Check that hidden files/dirs are not included
        assert not any(".gitignore" in line for line in result)
        assert not any(".git" in line for line in result)
    
    def test_tree_formatting(self):
        """Test that tree formatting is correct."""
        result = generate_ascii_structure(self.test_dir)
        
        # Check for proper tree characters
        assert any("├──" in line for line in result)
        assert any("└──" in line for line in result)
        assert any("│   " in line for line in result)
    
    def test_with_language_filter(self):
        """Test structure generation with language filtering."""
        # Add a JavaScript file
        open(os.path.join(self.test_dir, "app.js"), 'w').close()
        
        # Test Python filter
        result = generate_ascii_structure(self.test_dir, language="python")
        assert any("main.py" in line for line in result)
        assert any("__init__.py" in line for line in result)
        assert not any("app.js" in line for line in result)
        
        # Test JavaScript filter
        result = generate_ascii_structure(self.test_dir, language="javascript")
        assert any("app.js" in line for line in result)
        assert not any("main.py" in line for line in result)
    
    def test_empty_directory(self):
        """Test structure generation on empty directory."""
        empty_dir = tempfile.mkdtemp()
        try:
            result = generate_ascii_structure(empty_dir)
            assert result == []
        finally:
            os.rmdir(empty_dir)
    
    def test_nested_structure(self):
        """Test deeply nested directory structure."""
        # Create deeper nesting
        deep_path = os.path.join(self.test_dir, "src", "utils", "helpers")
        os.makedirs(deep_path)
        open(os.path.join(deep_path, "utility.py"), 'w').close()
        
        result = generate_ascii_structure(self.test_dir)
        
        # Check that nested structure is represented
        assert any("utils" in line for line in result)
        assert any("helpers" in line for line in result)
        assert any("utility.py" in line for line in result)
        
        # Check indentation increases with depth
        for line in result:
            if "utility.py" in line:
                # Should have multiple levels of indentation
                assert line.count("    ") >= 2