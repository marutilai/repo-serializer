import argparse
import os
from .serializer import serialize


def main():
    parser = argparse.ArgumentParser(
        description="""Serialize a repository into a structured text file, capturing directory structure, 
        file names, and contents. Supports filtering by file type and various output formats."""
    )
    parser.add_argument("repo_path", help="Path to the repository to serialize")
    parser.add_argument(
        "-o",
        "--output",
        default="repo_serialized.txt",
        help="Output file path (default: repo_serialized.txt)",
    )
    parser.add_argument(
        "-c",
        "--clipboard",
        action="store_true",
        help="Copy the output to clipboard in addition to saving to file",
    )
    parser.add_argument(
        "-s",
        "--structure-only",
        action="store_true",
        help="Only include directory structure and filenames (no file contents)",
    )
    parser.add_argument(
        "--python",
        action="store_true",
        help="Only include Python files (.py, .ipynb, .pyw, .pyx, .pxd, .pxi)",
    )
    parser.add_argument(
        "--javascript",
        action="store_true",
        help="Only include JavaScript/TypeScript files (.js, .jsx, .ts, .tsx, .vue, .svelte)",
    )

    args = parser.parse_args()

    # Ensure repo_path exists
    if not os.path.isdir(args.repo_path):
        print(f"Error: {args.repo_path} is not a valid directory")
        return 1

    # Handle language filtering
    language = None
    if args.python:
        language = "python"
    elif args.javascript:
        language = "javascript"

    if args.python and args.javascript:
        print("Error: Cannot specify both --python and --javascript")
        return 1

    # Serialize the repository
    content = serialize(
        args.repo_path,
        args.output,
        return_content=True,
        structure_only=args.structure_only,
        language=language,
    )

    print(f"Repository serialized to {args.output}")
    if args.structure_only:
        print("Note: Only directory structure was included (no file contents)")

    # Copy to clipboard if requested
    if args.clipboard:
        try:
            import pyperclip

            pyperclip.copy(content)
            print("Content also copied to clipboard")
        except ImportError:
            print(
                "Warning: pyperclip package not found. Install it with 'pip install pyperclip' to enable clipboard functionality."
            )
        except Exception as e:
            print(f"Warning: Failed to copy to clipboard: {str(e)}")

    return 0


if __name__ == "__main__":
    exit(main())
