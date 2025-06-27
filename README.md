# Repo Serializer

A Python utility for serializing local Git repositories into a structured text file, capturing the directory structure (in ASCII format), file names, and contents of source files. Ideal for providing a comprehensive snapshot of a repository for code review, documentation, or interaction with large language models (LLMs).

## Installation

```bash
# Install from PyPI
pip install repo-serializer

# For development
pip install "repo-serializer[dev]"
```

## Usage

### Command Line

```bash
# Basic usage
repo-serializer /path/to/repository

# Specify output file
repo-serializer /path/to/repository -o output.txt

# Copy to clipboard in addition to saving to file
repo-serializer /path/to/repository -c

# Use structure-only mode to output only the directory structure and filenames
repo-serializer /path/to/repository -s

# Skip specific directories (can be used multiple times or as a comma-separated list)
repo-serializer /path/to/repository --skip-dir build,dist
repo-serializer /path/to/repository --skip-dir build --skip-dir dist

# Only include Python files (.py, .ipynb)
repo-serializer /path/to/repository --python

# Only include JavaScript/TypeScript files
repo-serializer /path/to/repository --javascript

# Combine with other options
repo-serializer /path/to/repository --python -s -c  # Python files, structure only, copy to clipboard

# Extract AI/LLM prompts from the repository
repo-serializer /path/to/repository -p
repo-serializer /path/to/repository --prompt -o prompts.txt
```

### Python API

```python
from repo_serializer import serialize

# Serialize a repository, skipping specific directories
serialize("/path/to/repository", "output.txt", skip_dirs=["build", "dist"])
```

## Features

- **Directory Structure:** Clearly visualize repository structure in ASCII format.
- **Structure-Only Mode:** Option to output only the directory structure and filenames without file contents.
- **File Filtering**: Excludes common binary files, cache directories, hidden files, and irrelevant artifacts to keep outputs concise and focused.
- **Smart Content Handling**: 
  - Parses Jupyter notebooks to extract markdown and code cells with sample outputs
  - Limits CSV files to first 5 lines
  - Truncates large text files after 1000 lines
  - Handles non-UTF-8 and binary files gracefully
- **Extensive Filtering**: Skips common configuration files, build artifacts, test directories, and more.
- **Clipboard Integration**: Option to copy output directly to clipboard.
- **Prompt Extraction**: Extract AI/LLM prompts from various sources:
  - Inline strings in Python/JavaScript code near LLM API calls (OpenAI, Anthropic, etc.)
  - Standalone prompt files (`.prompt.txt`, `.prompt.md`, etc.)
  - YAML/JSON configuration files with prompt definitions
  - Jupyter notebooks containing prompts
  - Markdown files in prompt-related directories

## Example

```bash
# Create a serialized snapshot of your project
repo-serializer /Users/example_user/projects/my_repo -o repo_snapshot.txt
```

## Prompt Extraction

The prompt extraction feature (`-p` or `--prompt`) helps you analyze and audit AI/LLM prompts used throughout your codebase. This is particularly useful for:

- Reviewing prompt consistency and quality
- Refactoring duplicate prompts
- Creating prompt libraries
- Documenting AI behavior
- Security auditing of prompts

### What Gets Extracted

1. **Inline Prompts in Code**
   - Strings near OpenAI, Anthropic, and other LLM API calls
   - Multi-line strings assigned to prompt-related variables
   - Template literals in JavaScript/TypeScript

2. **Standalone Prompt Files**
   - Files with extensions like `.prompt.txt`, `.prompt.md`
   - Files in `prompts/` or similar directories
   - YAML/JSON files with prompt configurations

3. **Configuration Files**
   - YAML/JSON files with keys like `prompt`, `system_prompt`, `instructions`
   - Nested prompt definitions in configuration objects

### Example Output

```
Found 5 prompts in the repository:
================================================================================

File: src/ai_agent.py
--------------------------------------------------------------------------------

Line 15 (inline_string) - Near LLM API call:
```
You are an expert Python developer. Your task is to help users write clean,
efficient, and well-documented Python code. Follow these guidelines:

1. Always use proper error handling
2. Write comprehensive docstrings
3. Follow PEP 8 style guidelines
```

File: config/prompts.yaml
--------------------------------------------------------------------------------

Line 3 (config_file) - Key: system:
```
You are a code reviewer. Analyze the provided code for:
- Security vulnerabilities
- Performance issues
- Code quality and maintainability
```
```

## Contributing

Pull requests and improvements are welcome! Please ensure your contributions are clearly documented and tested.

## Development

### Quick Testing

For quick testing during development:

```bash
# Install in development mode
pip install -e .

# Now any changes to the source code take effect immediately
repo-serializer /path/to/test/repo -o test_output.txt
```

### Full Test Suite

Run the test script:
```bash
./dev/test_dev.py
```

This will:
1. Install the package in development mode
2. Run multiple test scenarios
3. Generate test outputs for review