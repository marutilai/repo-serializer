"""Test cases for the main serializer module."""

import pytest
import os
from repo_serializer.serializer import serialize, serialize_repo


class TestSerialize:
    """Test the serialize function."""
    
    def test_basic_serialization(self, temp_repo, temp_file):
        """Test basic repository serialization."""
        result = serialize(temp_repo, temp_file, return_content=True)
        
        # Check that output was created
        assert os.path.exists(temp_file)
        
        # Check content includes directory structure
        assert "Directory Structure:" in result
        assert "src" in result
        assert "tests" in result
        
        # Check that hidden directories are excluded
        assert ".git" not in result
        assert "__pycache__" not in result
        
        # Check file contents are included
        assert "Files Content:" in result
        assert "def main():" in result
        assert "def helper():" in result
        
        # Check statistics are included
        assert "File Statistics:" in result
        assert "Total lines in output:" in result
    
    def test_structure_only_mode(self, temp_repo, temp_file):
        """Test structure-only serialization."""
        result = serialize(temp_repo, temp_file, return_content=True, structure_only=True)
        
        # Check structure is included
        assert "Directory Structure:" in result
        assert "src" in result
        assert "main.py" in result
        
        # Check file contents are NOT included
        assert "Files Content:" not in result
        assert "def main():" not in result
        
        # Check statistics reflect structure-only mode
        assert "File Statistics:" in result
        assert "Lines by language:" not in result
    
    def test_language_filtering_python(self, temp_repo, temp_file):
        """Test Python language filtering."""
        result = serialize(temp_repo, temp_file, return_content=True, language="python")
        
        # Check Python files are included
        assert "main.py" in result
        assert "utils.py" in result
        assert "test_main.py" in result
        
        # Check non-Python files are excluded
        assert "data.csv" not in result
        assert "config.json" not in result
        
        # Check header indicates language filtering
        assert "Directory Structure (python files only):" in result
    
    def test_skip_dirs(self, temp_repo, temp_file):
        """Test custom directory skipping."""
        # Add a custom directory to skip
        custom_dir = os.path.join(temp_repo, "custom_skip")
        os.makedirs(custom_dir)
        with open(os.path.join(custom_dir, "file.txt"), 'w') as f:
            f.write("Should be skipped")
        
        result = serialize(
            temp_repo, 
            temp_file, 
            return_content=True,
            skip_dirs=["custom_skip", "docs"]
        )
        
        # Check that custom directories are skipped
        assert "custom_skip" not in result
        assert "Should be skipped" not in result
        
        # Note: The skip_dirs parameter isn't fully implemented in the current code
        # This test documents the expected behavior
    
    def test_return_content_false(self, temp_repo, temp_file):
        """Test when return_content is False."""
        result = serialize(temp_repo, temp_file, return_content=False)
        
        # Should return None when return_content is False
        assert result is None
        
        # But file should still be created
        assert os.path.exists(temp_file)
        with open(temp_file, 'r') as f:
            content = f.read()
            assert "Directory Structure:" in content


class TestSerializeRepo:
    """Test the serialize_repo function directly."""
    
    def test_max_lines_parameter(self, temp_repo, temp_file):
        """Test the max_lines parameter for file truncation."""
        # Create a large file
        large_file = os.path.join(temp_repo, "large.txt")
        with open(large_file, 'w') as f:
            for i in range(100):
                f.write(f"Line {i}\n")
        
        result = serialize_repo(
            temp_repo,
            temp_file,
            max_lines=50,
            return_content=True
        )
        
        # Check that file was truncated
        assert "Line 49" in result
        assert "Line 50" not in result
        assert "[file truncated after 50 lines]" in result
    
    def test_unicode_handling(self, temp_repo, temp_file):
        """Test handling of unicode content."""
        unicode_file = os.path.join(temp_repo, "unicode.txt")
        with open(unicode_file, 'w', encoding='utf-8') as f:
            f.write("Hello 世界 🌍")
        
        result = serialize_repo(temp_repo, temp_file, return_content=True)
        
        # Check that unicode content is preserved
        assert "Hello 世界 🌍" in result
    
    def test_binary_file_handling(self, temp_repo, temp_file):
        """Test handling of binary files."""
        binary_file = os.path.join(temp_repo, "binary.dat")
        with open(binary_file, 'wb') as f:
            f.write(b'\x00\x01\x02\x03\xff\xfe\xfd')
        
        result = serialize_repo(temp_repo, temp_file, return_content=True)
        
        # Binary files should show placeholder
        assert "[BINARY or NON-UTF8 CONTENT]" in result
    
    def test_special_file_types(self, temp_repo, temp_file):
        """Test handling of special file types (CSV, JSON, notebooks)."""
        result = serialize_repo(temp_repo, temp_file, return_content=True)
        
        # CSV should be limited to 5 lines
        assert "name,value" in result
        assert "test,123" in result
        
        # JSON should be included normally
        assert '"key": "value"' in result