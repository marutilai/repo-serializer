"""Main serialization logic for repo-serializer."""

import os
from .filters import should_skip
from .structure import generate_ascii_structure
from .file_processors import process_jupyter_notebook, process_csv_file, process_text_file
from .statistics import count_lines, format_statistics


def serialize_repo(
    repo_path,
    output_file,
    max_lines=1000,
    return_content=False,
    structure_only=False,
    language=None,
    skip_dirs=None,
):
    """Serialize a repository to a structured text file."""
    serialized_content = []

    # Add language info to output if specified
    if language:
        serialized_content.append(f"Directory Structure ({language} files only):")
    else:
        serialized_content.append("Directory Structure:")

    generate_ascii_structure(
        repo_path, serialized_content=serialized_content, language=language, skip_dirs=skip_dirs
    )

    # Skip file contents if structure_only is True
    if not structure_only:
        serialized_content.append("\nFiles Content:")
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [
                d
                for d in dirs
                if not should_skip(d, True, language, os.path.join(root, d))
                and d not in (skip_dirs or [])
            ]
            for file in files:
                if should_skip(file, False, language, os.path.join(root, file)):
                    continue
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, repo_path)
                serialized_content.append(f"\n--- Start of {rel_path} ---\n")

                # Process different file types
                try:
                    if file.lower().endswith(".ipynb"):
                        content = process_jupyter_notebook(file_path)
                        serialized_content.append(content)
                    elif file.lower().endswith(".csv"):
                        content = process_csv_file(file_path)
                        serialized_content.append(content)
                    else:
                        content = process_text_file(file_path, max_lines)
                        serialized_content.append(content)
                except UnicodeDecodeError:
                    serialized_content.append("[BINARY or NON-UTF8 CONTENT]")
                except Exception as e:
                    serialized_content.append(f"[Error reading file: {str(e)}]")

    content_str = "\n".join(serialized_content)

    # Add statistics
    total_lines, language_lines = count_lines(content_str, structure_only)
    stats = format_statistics(total_lines, language_lines, structure_only)
    content_str += stats

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
    repo_path, output_file, return_content=False, structure_only=False, language=None, skip_dirs=None
):
    """Public API for serializing a repository."""
    return serialize_repo(
        repo_path,
        output_file,
        return_content=return_content,
        structure_only=structure_only,
        language=language,
        skip_dirs=skip_dirs,
    )