"""Test cases for statistics module."""

import pytest
from repo_serializer.statistics import count_lines, format_statistics


class TestCountLines:
    """Test the count_lines function."""
    
    def test_structure_only_mode(self):
        """Test line counting in structure-only mode."""
        content = """Directory Structure:
├── src
│   ├── main.py
│   └── utils.py
├── tests
│   └── test_main.py
└── README.md"""
        
        total, languages = count_lines(content, structure_only=True)
        
        assert total == 7  # 7 non-empty lines
        assert languages["other"] == 7
        assert languages["python"] == 0
    
    def test_content_mode_python(self):
        """Test line counting with Python files."""
        content = """Directory Structure:
├── main.py
└── test.py

Files Content:
--- Start of main.py ---
def hello():
    print("Hello, World!")

if __name__ == "__main__":
    hello()
--- Start of test.py ---
import pytest

def test_hello():
    assert True"""
        
        total, languages = count_lines(content, structure_only=False)
        
        # Count only content lines, not structure or headers
        assert languages["python"] > 0
        assert total == languages["python"]  # All content lines are Python
    
    def test_content_mode_mixed_languages(self):
        """Test line counting with mixed language files."""
        content = """Files Content:
--- Start of script.py ---
print("Python")
--- Start of app.js ---
console.log("JavaScript");
--- Start of README.md ---
# Markdown
--- Start of setup.sh ---
#!/bin/bash
echo "Bash"
--- Start of data.json ---
{"key": "value"}"""
        
        total, languages = count_lines(content, structure_only=False)
        
        assert languages["python"] == 1
        assert languages["javascript"] == 1
        assert languages["markdown"] == 1
        assert languages["bash"] == 2  # shebang + echo
        assert languages["other"] == 1  # JSON
        assert total == 6
    
    def test_empty_content(self):
        """Test counting lines in empty content."""
        total, languages = count_lines("", structure_only=False)
        
        assert total == 0
        assert all(count == 0 for count in languages.values())


class TestFormatStatistics:
    """Test the format_statistics function."""
    
    def test_format_structure_only(self):
        """Test formatting statistics in structure-only mode."""
        result = format_statistics(100, {"other": 100}, structure_only=True)
        
        assert "File Statistics:" in result
        assert "Total lines in output: 100" in result
        assert "Lines by language:" not in result  # Should not show language breakdown
    
    def test_format_with_languages(self):
        """Test formatting statistics with language breakdown."""
        language_lines = {
            "python": 150,
            "javascript": 75,
            "markdown": 25,
            "bash": 0,
            "other": 10
        }
        
        result = format_statistics(260, language_lines, structure_only=False)
        
        assert "File Statistics:" in result
        assert "Total lines in output: 260" in result
        assert "Lines by language:" in result
        assert "Python: 150" in result
        assert "Javascript: 75" in result
        assert "Markdown: 25" in result
        assert "Bash: 0" not in result  # Zero counts should not be shown
        assert "Other: 10" in result
    
    def test_format_no_content(self):
        """Test formatting when there's no content."""
        language_lines = {
            "python": 0,
            "javascript": 0,
            "markdown": 0,
            "bash": 0,
            "other": 0
        }
        
        result = format_statistics(0, language_lines, structure_only=False)
        
        assert "Total lines in output: 0" in result
        # Should not show any language lines since all are zero
        lines = result.split('\n')
        language_lines_in_output = [line for line in lines if line.strip().startswith(('Python:', 'Javascript:', 'Markdown:', 'Bash:', 'Other:'))]
        assert len(language_lines_in_output) == 0