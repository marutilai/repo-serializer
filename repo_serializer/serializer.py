import os
import json

SKIP_EXTENSIONS = {
    ".pyc",
    ".exe",
    ".dll",
    ".so",
    ".o",
    ".bin",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".ico",
    ".svg",
    ".log",
    ".zip",
    ".gz",
    ".tar",
    ".rar",
    ".7z",
    ".pdf",
    ".mp4",
    ".mp3",
    ".wav",
    ".class",
    ".jar",
    ".db",
    ".sqlite",
    ".map",  # Source Maps
    ".d.ts",  # TypeScript Declaration Files
    ".lock",  # Dependency Lock Files
    ".lockb",
    ".lock.json",
    ".lock.yaml",
    ".lock.yml",
    ".lock.toml",
    ".toml",
    ".yarnrc",
    ".npmrc",
    # Config files
    ".ini",
    ".cfg",
    ".conf",
    ".config",
    ".yaml",
    ".yml",
    ".env",
    # Large data files
    ".parquet",
    ".avro",
    ".hdf5",
    ".h5",
    ".feather",
    ".arrow",
    ".pickle",
    ".pkl",
    # Minified files
    ".min.js",
    ".min.css",
    # Backup files
    ".bak",
    ".backup",
    ".swp",
    "~",
    # Test data
    ".fixture",
    ".test.js",
    ".spec.js",
    ".test.ts",
    ".spec.ts",
}

SKIP_FILES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "composer.lock",
    "Cargo.lock",
    "Pipfile.lock",
    "poetry.lock",
    "Gemfile.lock",
    "go.sum",
    # Common config files
    ".gitignore",
    ".gitattributes",
    ".editorconfig",
    ".eslintrc",
    ".prettierrc",
    "tsconfig.json",
    "tslint.json",
    "babel.config.js",
    "jest.config.js",
    "webpack.config.js",
    "rollup.config.js",
    "vite.config.js",
    "next.config.js",
    "nuxt.config.js",
    "svelte.config.js",
    ".browserslistrc",
    ".npmignore",
    # License and legal files
    "LICENSE",
    "LICENSE.txt",
    "LICENSE.md",
    "COPYING",
    "NOTICE",
    # Documentation files (if you want to skip them)
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    # CI/CD config files
    ".travis.yml",
    ".gitlab-ci.yml",
    ".github/workflows/ci.yml",
    "azure-pipelines.yml",
    "Jenkinsfile",
    ".circleci/config.yml",
}

SKIP_DIRS = {
    "__pycache__",
    ".git",
    ".idea",
    ".vscode",
    "node_modules",
    ".DS_Store",
    "venv",
    ".venv",
    ".mypy_cache",
    ".pytest_cache",
    ".coverage",
    ".cache",
    ".temp",
    ".build",
    ".dist",
    ".out",
    ".tmp",
    ".log",
    "temp",
    "tmp",
    "node_modules/.vite",
    "cypress",
    "dist",
    "build",
    "out",
    "cache",
    "temp",
    # Test directories
    "tests",
    "test",
    "__tests__",
    "spec",
    "__mocks__",
    "fixtures",
    "e2e",
    # Documentation directories
    "docs",
    "doc",
    "documentation",
    # Build artifacts
    "coverage",
    ".nyc_output",
    "reports",
    "site",
    "public",
    "static",
    # Dependency directories beyond node_modules
    "vendor",
    "bower_components",
    "jspm_packages",
    ".pnp",
    # IDE specific
    ".settings",
    ".project",
    ".classpath",
    ".factorypath",
    # Misc
    "examples",
    "sample",
    "demo",
    "assets",
    "images",
    "img",
    "fonts",
}


def should_skip(name, is_dir=False):
    if name.startswith("."):
        return True
    if is_dir and name in SKIP_DIRS:
        return True
    if not is_dir:
        if os.path.splitext(name)[1] in SKIP_EXTENSIONS:
            return True
        if name in SKIP_FILES:
            return True
    return False


def generate_ascii_structure(path, prefix="", serialized_content=None):
    if serialized_content is None:
        serialized_content = []
    entries = sorted(
        e
        for e in os.listdir(path)
        if not should_skip(e, os.path.isdir(os.path.join(path, e)))
    )
    for idx, entry in enumerate(entries):
        entry_path = os.path.join(path, entry)
        connector = "└── " if idx == len(entries) - 1 else "├── "
        serialized_content.append(f"{prefix}{connector}{entry}")
        if os.path.isdir(entry_path):
            extension = "    " if idx == len(entries) - 1 else "│   "
            generate_ascii_structure(entry_path, prefix + extension, serialized_content)
    return serialized_content


def serialize_repo(repo_path, output_file, max_lines=1000):
    serialized_content = []

    serialized_content.append("Directory Structure:")
    generate_ascii_structure(repo_path, serialized_content=serialized_content)

    serialized_content.append("\nFiles Content:")
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if not should_skip(d, True)]
        for file in files:
            if should_skip(file, False):
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
                                                    text_lines = text.splitlines()[:3]
                                                    text = "\n".join(text_lines)
                                                    text += (
                                                        "\n... [output truncated] ..."
                                                    )
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
                                                    text_lines = text.splitlines()[:3]
                                                    text = "\n".join(text_lines)
                                                    text += (
                                                        "\n... [output truncated] ..."
                                                    )
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

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(serialized_content))


def serialize(repo_path, output_file):
    serialize_repo(repo_path, output_file)
