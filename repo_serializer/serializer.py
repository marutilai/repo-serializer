import os
import json
from .config import (
    SKIP_EXTENSIONS,
    SKIP_FILES,
    SKIP_DIRS,
    LANGUAGE_PATTERNS,
)


def should_skip(name, is_dir=False, language=None):
    """Enhanced skip check with language filtering"""
    # First apply basic skip rules
    if name.startswith("."):
        return True
    if is_dir and name in SKIP_DIRS:
        return True
    if not is_dir:
        if name in SKIP_FILES:
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


def generate_ascii_structure(path, prefix="", serialized_content=None, language=None):
    if serialized_content is None:
        serialized_content = []
    entries = sorted(
        e
        for e in os.listdir(path)
        if not should_skip(e, os.path.isdir(os.path.join(path, e)), language)
    )
    for idx, entry in enumerate(entries):
        entry_path = os.path.join(path, entry)
        connector = "└── " if idx == len(entries) - 1 else "├── "
        serialized_content.append(f"{prefix}{connector}{entry}")
        if os.path.isdir(entry_path):
            extension = "    " if idx == len(entries) - 1 else "│   "
            generate_ascii_structure(
                entry_path, prefix + extension, serialized_content, language
            )
    return serialized_content


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


def serialize_repo(
    repo_path,
    output_file,
    max_lines=1000,
    return_content=False,
    structure_only=False,
    language=None,
):
    serialized_content = []

    # Add language info to output if specified
    if language:
        serialized_content.append(f"Directory Structure ({language} files only):")
    else:
        serialized_content.append("Directory Structure:")

    generate_ascii_structure(
        repo_path, serialized_content=serialized_content, language=language
    )

    # Skip file contents if structure_only is True
    if not structure_only:
        serialized_content.append("\nFiles Content:")
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not should_skip(d, True, language)]
            for file in files:
                if should_skip(file, False, language):
                    continue
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, repo_path)
                serialized_content.append(f"\n--- Start of {rel_path} ---\n")

                # Check file type
                is_csv = file.lower().endswith(".csv")
                is_notebook = file.lower().endswith(".ipynb")

                try:
                    if is_notebook:
                        # Special handling for Jupyter notebooks
                        with open(file_path, "r", encoding="utf-8") as f:
                            try:
                                notebook = json.load(f)
                                cells_content = []

                                # Add notebook metadata if available
                                if (
                                    "metadata" in notebook
                                    and "kernelspec" in notebook["metadata"]
                                ):
                                    kernel = notebook["metadata"]["kernelspec"].get(
                                        "display_name", "Unknown"
                                    )
                                    cells_content.append(
                                        f"Jupyter Notebook (Kernel: {kernel})\n"
                                    )

                                # Process cells - don't limit the number of cells
                                for i, cell in enumerate(notebook.get("cells", [])):
                                    cell_type = cell.get("cell_type", "unknown")

                                    if cell_type == "markdown":
                                        source = "".join(cell.get("source", []))
                                        cells_content.append(
                                            f"[Markdown Cell {i+1}]\n{source}\n"
                                        )

                                    elif cell_type == "code":
                                        source = "".join(cell.get("source", []))
                                        # Don't limit code cells, show all code
                                        cells_content.append(
                                            f"[Code Cell {i+1}]\n{source}\n"
                                        )

                                        # Include a sample of outputs if present, but limit these
                                        outputs = cell.get("outputs", [])
                                        if outputs:
                                            output_text = []
                                            # Only show first output and limit its size
                                            if outputs:
                                                output = outputs[0]
                                                if "text" in output:
                                                    text = "".join(output["text"])
                                                    # Limit output text to 3 lines
                                                    if len(text.splitlines()) > 3:
                                                        text_lines = text.splitlines()[
                                                            :3
                                                        ]
                                                        text = "\n".join(text_lines)
                                                        text += "\n... [output truncated] ..."
                                                    output_text.append(text)
                                                elif (
                                                    "data" in output
                                                    and "text/plain" in output["data"]
                                                ):
                                                    text = "".join(
                                                        output["data"]["text/plain"]
                                                    )
                                                    # Limit output text to 3 lines
                                                    if len(text.splitlines()) > 3:
                                                        text_lines = text.splitlines()[
                                                            :3
                                                        ]
                                                        text = "\n".join(text_lines)
                                                        text += "\n... [output truncated] ..."
                                                    output_text.append(text)

                                            if output_text:
                                                cells_content.append(
                                                    "Output (sample):\n"
                                                    + "\n".join(output_text)
                                                    + "\n"
                                                )

                                            if len(outputs) > 1:
                                                cells_content.append(
                                                    f"... [{len(outputs) - 1} more outputs not shown] ...\n"
                                                )

                                serialized_content.append("\n".join(cells_content))
                            except json.JSONDecodeError:
                                serialized_content.append(
                                    "[Invalid or corrupted notebook file]"
                                )
                    elif is_csv:
                        # Existing CSV handling
                        with open(file_path, "r", encoding="utf-8") as f:
                            lines = []
                            for i, line in enumerate(f):
                                if i >= 5:
                                    lines.append(
                                        "... [remaining CSV content truncated] ..."
                                    )
                                    break
                                lines.append(line.rstrip())
                            serialized_content.append("\n".join(lines))
                    else:
                        # Existing handling for other text files
                        with open(file_path, "r", encoding="utf-8") as f:
                            lines = []
                            for i, line in enumerate(f):
                                if i >= max_lines:
                                    lines.append(
                                        f"\n... [file truncated after {max_lines} lines] ..."
                                    )
                                    break
                                lines.append(line.rstrip())

                            if len(lines) >= max_lines:
                                serialized_content.append("\n".join(lines))
                            else:
                                f.seek(0)
                                serialized_content.append(f.read())
                except UnicodeDecodeError:
                    serialized_content.append("[BINARY or NON-UTF8 CONTENT]")
                except Exception as e:
                    serialized_content.append(f"[Error reading file: {str(e)}]")

    content_str = "\n".join(serialized_content)

    # Add statistics - pass structure_only flag
    total_lines, language_lines = count_lines(content_str, structure_only)

    # Create statistics section
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

    # Add stats to content
    content_str += "\n" + "\n".join(stats)

    # Write to file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content_str)

    # Print statistics to terminal
    print("\nFile Statistics:")
    print(f"Total lines in output: {total_lines}")
    if not structure_only:
        print("Lines by language:")
        for lang, count in language_lines.items():
            if count > 0:
                print(f"  {lang.capitalize()}: {count}")

    if return_content:
        return content_str


def serialize(
    repo_path, output_file, return_content=False, structure_only=False, language=None
):
    return serialize_repo(
        repo_path,
        output_file,
        return_content=return_content,
        structure_only=structure_only,
        language=language,
    )
