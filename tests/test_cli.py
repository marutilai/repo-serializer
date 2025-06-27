"""Test cases for CLI module."""

import pytest
import subprocess
import sys
import os
from unittest.mock import patch, MagicMock
from repo_serializer.cli import main


class TestCLI:
    """Test the command-line interface."""
    
    def test_help_output(self):
        """Test that help text is displayed correctly."""
        result = subprocess.run(
            [sys.executable, "-m", "repo_serializer.cli", "--help"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "Serialize a repository into a structured text file" in result.stdout
        assert "--output" in result.stdout
        assert "--clipboard" in result.stdout
        assert "--structure-only" in result.stdout
        assert "--python" in result.stdout
        assert "--javascript" in result.stdout
        assert "--prompt" in result.stdout
    
    def test_invalid_directory(self):
        """Test error handling for invalid directory."""
        with patch('sys.argv', ['repo-serializer', '/nonexistent/directory']):
            with patch('builtins.print') as mock_print:
                result = main()
                
        assert result == 1
        mock_print.assert_called_with("Error: /nonexistent/directory is not a valid directory")
    
    def test_conflicting_language_options(self):
        """Test error when both --python and --javascript are specified."""
        with patch('sys.argv', ['repo-serializer', '.', '--python', '--javascript']):
            with patch('os.path.isdir', return_value=True):
                with patch('builtins.print') as mock_print:
                    result = main()
                    
        assert result == 1
        mock_print.assert_called_with("Error: Cannot specify both --python and --javascript")
    
    def test_prompt_mode_conflicts(self):
        """Test error handling for conflicting options with prompt mode."""
        # Test --prompt with --structure-only
        with patch('sys.argv', ['repo-serializer', '.', '--prompt', '--structure-only']):
            with patch('os.path.isdir', return_value=True):
                with patch('builtins.print') as mock_print:
                    result = main()
                    
        assert result == 1
        mock_print.assert_called_with("Error: Cannot use --prompt with --structure-only")
        
        # Test --prompt with --python
        with patch('sys.argv', ['repo-serializer', '.', '--prompt', '--python']):
            with patch('os.path.isdir', return_value=True):
                with patch('builtins.print') as mock_print:
                    result = main()
                    
        assert result == 1
        mock_print.assert_called_with("Error: Cannot use --prompt with language filters (--python or --javascript)")
    
    @patch('repo_serializer.cli.serialize')
    def test_basic_execution(self, mock_serialize):
        """Test basic CLI execution."""
        mock_serialize.return_value = "test content"
        
        with patch('sys.argv', ['repo-serializer', '.', '-o', 'output.txt']):
            with patch('os.path.isdir', return_value=True):
                with patch('builtins.print') as mock_print:
                    result = main()
        
        assert result == 0
        mock_serialize.assert_called_once_with(
            '.',
            'output.txt',
            return_content=True,
            structure_only=False,
            language=None,
            skip_dirs=[]
        )
        mock_print.assert_called_with("Repository serialized to output.txt")
    
    @patch('repo_serializer.cli.serialize')
    def test_structure_only_mode(self, mock_serialize):
        """Test structure-only mode."""
        mock_serialize.return_value = "test content"
        
        with patch('sys.argv', ['repo-serializer', '.', '-s']):
            with patch('os.path.isdir', return_value=True):
                with patch('builtins.print') as mock_print:
                    result = main()
        
        assert result == 0
        mock_serialize.assert_called_once()
        assert mock_serialize.call_args[1]['structure_only'] is True
        
        # Check for structure-only message
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Only directory structure was included" in str(call) for call in print_calls)
    
    @patch('repo_serializer.cli.serialize')
    @patch('pyperclip.copy')
    def test_clipboard_integration(self, mock_clipboard, mock_serialize):
        """Test clipboard integration."""
        mock_serialize.return_value = "test content"
        
        with patch('sys.argv', ['repo-serializer', '.', '-c']):
            with patch('os.path.isdir', return_value=True):
                with patch('builtins.print') as mock_print:
                    result = main()
        
        assert result == 0
        mock_clipboard.assert_called_once_with("test content")
        
        # Check for clipboard message
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Content also copied to clipboard" in str(call) for call in print_calls)
    
    @patch('repo_serializer.cli.PromptExtractor')
    def test_prompt_extraction_mode(self, mock_extractor_class):
        """Test prompt extraction mode."""
        mock_extractor = MagicMock()
        mock_extractor.extract_prompts.return_value = [
            {
                'file': 'test.py',
                'line': 10,
                'type': 'inline_string',
                'content': 'Test prompt',
                'context': 'Test context'
            }
        ]
        mock_extractor_class.return_value = mock_extractor
        
        with patch('sys.argv', ['repo-serializer', '.', '-p']):
            with patch('os.path.isdir', return_value=True):
                with patch('builtins.print') as mock_print:
                    with patch('builtins.open', create=True) as mock_open:
                        result = main()
        
        assert result == 0
        mock_extractor.extract_prompts.assert_called_once_with('.')
        
        # Check for prompt extraction messages
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Prompts extracted to" in str(call) for call in print_calls)
        assert any("Found 1 prompts" in str(call) for call in print_calls)
    
    def test_skip_dir_parsing(self):
        """Test parsing of --skip-dir arguments."""
        with patch('sys.argv', ['repo-serializer', '.', '--skip-dir', 'build,dist', '--skip-dir', 'node_modules']):
            with patch('os.path.isdir', return_value=True):
                with patch('repo_serializer.cli.serialize') as mock_serialize:
                    mock_serialize.return_value = "content"
                    result = main()
        
        assert result == 0
        # Check that skip_dirs were parsed correctly
        call_args = mock_serialize.call_args[1]
        assert set(call_args['skip_dirs']) == {'build', 'dist', 'node_modules'}