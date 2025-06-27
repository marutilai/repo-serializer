"""File and directory filtering logic for repo-serializer."""

import os
from .config import (
    SKIP_EXTENSIONS,
    SKIP_FILES,
    SKIP_DIRS,
    LANGUAGE_PATTERNS,
)


def should_skip(name, is_dir=False, language=None, full_path=None):
    """Enhanced skip check with language filtering"""
    # First apply basic skip rules
    if name.startswith("."):
        return True
    if is_dir:
        # Check if the directory name matches exactly
        if name in SKIP_DIRS:
            return True
        # Check patterns with paths if full_path is provided
        if full_path:
            normalized_path = full_path.replace(os.sep, "/")
            for pattern in SKIP_DIRS:
                if "/" in pattern and normalized_path.endswith(pattern):
                    return True
    else:
        for pattern in SKIP_FILES:
            if "/" in pattern and full_path:
                if full_path.replace(os.sep, "/").endswith(pattern):
                    return True
            elif name == pattern:
                return True

        # If language filtering is enabled
        if language:
            patterns = LANGUAGE_PATTERNS.get(language, {})
            ext = os.path.splitext(name)[1].lower()
            # Skip if extension doesn't match language
            if ext not in patterns.get("extensions", set()):
                return True
            # Skip if matches skip patterns
            if any(
                pattern in name.lower()
                for pattern in patterns.get("skip_patterns", set())
            ):
                return True
            # File matches language requirements, don't skip
            return False
        # No language filtering, apply normal extension skip
        if os.path.splitext(name)[1] in SKIP_EXTENSIONS:
            return True
    return False