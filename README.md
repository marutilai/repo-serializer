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
```

### Python API

```python
from repo_serializer import serialize

# Serialize a repository
serialize("/path/to/repository", "output.txt")
```

## Features

- **Directory Structure:** Clearly visualize repository structure in ASCII format.
- **File Filtering**: Excludes common binary files, cache directories, hidden files, and irrelevant artifacts to keep outputs concise and focused.
- **Smart Content Handling**: 
  - Parses Jupyter notebooks to extract markdown and code cells with sample outputs
  - Limits CSV files to first 5 lines
  - Truncates large text files after 1000 lines
  - Handles non-UTF-8 and binary files gracefully
- **Extensive Filtering**: Skips common configuration files, build artifacts, test directories, and more.

## Example

```bash
# Create a serialized snapshot of your project
repo-serializer /Users/example_user/projects/my_repo -o repo_snapshot.txt
```

## Contributing

Pull requests and improvements are welcome! Please ensure your contributions are clearly documented and tested.