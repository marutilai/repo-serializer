"""Statistics calculation for serialized content."""

import os


def count_lines(content, structure_only=False):
    """Count total lines and lines by language in the content."""
    total_lines = 0
    language_lines = {
        "python": 0,
        "javascript": 0,
        "markdown": 0,
        "bash": 0,
        "other": 0,
    }

    if structure_only:
        # For structure-only mode, just count all lines
        total_lines = len([line for line in content.split("\n") if line.strip()])
        # Don't try to categorize by language in structure-only mode
        language_lines["other"] = total_lines
    else:
        current_file = None
        for line in content.split("\n"):
            if line.startswith("--- Start of "):
                current_file = line.replace("--- Start of ", "").replace(" ---", "")
            elif current_file:
                total_lines += 1
                # Count by file extension
                ext = os.path.splitext(current_file)[1].lower()
                if ext in {".py", ".pyw", ".pyx", ".ipynb"}:
                    language_lines["python"] += 1
                elif ext in {".js", ".jsx", ".ts", ".tsx"}:
                    language_lines["javascript"] += 1
                elif ext in {".md", ".markdown"}:
                    language_lines["markdown"] += 1
                elif ext in {".sh", ".bash"}:
                    language_lines["bash"] += 1
                else:
                    language_lines["other"] += 1

    return total_lines, language_lines


def format_statistics(total_lines, language_lines, structure_only=False):
    """Format statistics for output."""
    stats = [
        "\n\nFile Statistics:",
        f"Total lines in output: {total_lines}",
    ]

    # Only show language breakdown if not in structure-only mode
    if not structure_only:
        stats.append("Lines by language:")
        # Add non-zero language counts
        for lang, count in language_lines.items():
            if count > 0:
                stats.append(f"  {lang.capitalize()}: {count}")

    return "\n".join(stats)