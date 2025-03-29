# Repo Serializer

A Python utility for serializing local Git repositories into a structured text file, capturing the directory structure (in ASCII format), file names, and contents of source files. Ideal for providing a comprehensive snapshot of a repository for code review, documentation, or interaction with large language models (LLMs).

## Installation

```bash
# Install from PyPI
pip install repo-serializer
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

# Only include Python files (.py, .ipynb)
repo-serializer /path/to/repository --python

# Only include JavaScript/TypeScript files
repo-serializer /path/to/repository --javascript

# Combine with other options
repo-serializer /path/to/repository --python -s -c  # Python files, structure only, copy to clipboard
```

### Python API

```python
from repo_serializer import serialize

# Serialize a repository
serialize("/path/to/repository", "output.txt")
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

## Example

```bash
# Create a serialized snapshot of your project
repo-serializer /Users/example_user/projects/my_repo -o repo_snapshot.txt
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