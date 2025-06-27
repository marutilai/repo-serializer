"""Directory structure generation for repo-serializer."""

import os
from .filters import should_skip


def generate_ascii_structure(path, prefix="", serialized_content=None, language=None, skip_dirs=None):
    """Generate ASCII representation of directory structure."""
    if serialized_content is None:
        serialized_content = []
    if skip_dirs is None:
        skip_dirs = []
    
    entries = sorted(
        e
        for e in os.listdir(path)
        if not should_skip(
            e,
            os.path.isdir(os.path.join(path, e)),
            language,
            os.path.join(path, e),
        ) and (not os.path.isdir(os.path.join(path, e)) or e not in skip_dirs)
    )
    for idx, entry in enumerate(entries):
        entry_path = os.path.join(path, entry)
        connector = "└── " if idx == len(entries) - 1 else "├── "
        serialized_content.append(f"{prefix}{connector}{entry}")
        if os.path.isdir(entry_path):
            extension = "    " if idx == len(entries) - 1 else "│   "
            generate_ascii_structure(
                entry_path, prefix + extension, serialized_content, language, skip_dirs
            )
    return serialized_content