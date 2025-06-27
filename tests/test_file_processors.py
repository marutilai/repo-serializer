"""Test cases for file processors module."""

import pytest
import tempfile
import os
import json
from repo_serializer.file_processors import (
    process_jupyter_notebook,
    process_csv_file,
    process_text_file
)


class TestProcessJupyterNotebook:
    """Test Jupyter notebook processing."""
    
    def test_valid_notebook(self):
        """Test processing a valid Jupyter notebook."""
        notebook_content = {
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3"
                }
            },
            "cells": [
                {
                    "cell_type": "markdown",
                    "source": ["# Test Notebook\n", "This is a test."]
                },
                {
                    "cell_type": "code",
                    "source": ["print('Hello, World!')"],
                    "outputs": [
                        {
                            "text": ["Hello, World!\n"]
                        }
                    ]
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ipynb', delete=False) as f:
            json.dump(notebook_content, f)
            temp_path = f.name
        
        try:
            result = process_jupyter_notebook(temp_path)
            
            # Check metadata
            assert "Jupyter Notebook (Kernel: Python 3)" in result
            
            # Check markdown cell
            assert "[Markdown Cell 1]" in result
            assert "# Test Notebook" in result
            assert "This is a test." in result
            
            # Check code cell
            assert "[Code Cell 2]" in result
            assert "print('Hello, World!')" in result
            
            # Check output
            assert "Output (sample):" in result
            assert "Hello, World!" in result
        finally:
            os.unlink(temp_path)
    
    def test_invalid_notebook(self):
        """Test processing an invalid notebook file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ipynb', delete=False) as f:
            f.write("This is not valid JSON")
            temp_path = f.name
        
        try:
            result = process_jupyter_notebook(temp_path)
            assert result == "[Invalid or corrupted notebook file]"
        finally:
            os.unlink(temp_path)
    
    def test_notebook_with_long_output(self):
        """Test notebook with output that needs truncation."""
        notebook_content = {
            "cells": [
                {
                    "cell_type": "code",
                    "source": ["for i in range(10):\n    print(i)"],
                    "outputs": [
                        {
                            "text": ["0\n1\n2\n3\n4\n5\n6\n7\n8\n9\n"]
                        }
                    ]
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ipynb', delete=False) as f:
            json.dump(notebook_content, f)
            temp_path = f.name
        
        try:
            result = process_jupyter_notebook(temp_path)
            assert "... [output truncated] ..." in result
        finally:
            os.unlink(temp_path)


class TestProcessCsvFile:
    """Test CSV file processing."""
    
    def test_csv_file(self):
        """Test processing a CSV file."""
        csv_content = """name,age,city
John,30,New York
Jane,25,Los Angeles
Bob,35,Chicago
Alice,28,Boston
Charlie,32,Seattle
David,29,Portland"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name
        
        try:
            result = process_csv_file(temp_path)
            
            # Check that only first 5 lines are included
            assert "John,30,New York" in result
            assert "Alice,28,Boston" in result
            assert "Charlie,32,Seattle" not in result
            assert "... [remaining CSV content truncated] ..." in result
        finally:
            os.unlink(temp_path)
    
    def test_small_csv_file(self):
        """Test processing a small CSV file that doesn't need truncation."""
        csv_content = """header1,header2
value1,value2
value3,value4"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name
        
        try:
            result = process_csv_file(temp_path)
            
            # All content should be included
            assert "header1,header2" in result
            assert "value1,value2" in result
            assert "value3,value4" in result
            assert "truncated" not in result
        finally:
            os.unlink(temp_path)


class TestProcessTextFile:
    """Test text file processing."""
    
    def test_small_text_file(self):
        """Test processing a small text file."""
        content = "Line 1\nLine 2\nLine 3"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            result = process_text_file(temp_path)
            assert result == content
        finally:
            os.unlink(temp_path)
    
    def test_large_text_file(self):
        """Test processing a large text file that needs truncation."""
        # Create a file with more than 1000 lines
        lines = [f"Line {i}" for i in range(1500)]
        content = "\n".join(lines)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            result = process_text_file(temp_path, max_lines=1000)
            
            # Check that it's truncated
            assert "Line 999" in result
            assert "Line 1000" not in result
            assert "... [file truncated after 1000 lines] ..." in result
        finally:
            os.unlink(temp_path)
    
    def test_text_file_with_custom_limit(self):
        """Test processing with custom line limit."""
        lines = [f"Line {i}" for i in range(20)]
        content = "\n".join(lines)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            result = process_text_file(temp_path, max_lines=10)
            
            # Check that it's truncated at custom limit
            assert "Line 9" in result
            assert "Line 10" not in result
            assert "... [file truncated after 10 lines] ..." in result
        finally:
            os.unlink(temp_path)