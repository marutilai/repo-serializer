import os

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

            # Check if it's a CSV file
            is_csv = file.lower().endswith(".csv")

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    if is_csv:
                        # Only read first 5 lines for CSV files
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
                        # Limit large text files
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
                            # Reset file pointer and read the whole file
                            # (more efficient for small files)
                            f.seek(0)
                            serialized_content.append(f.read())
            except UnicodeDecodeError:
                serialized_content.append("[BINARY or NON-UTF8 CONTENT]")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(serialized_content))


def serialize(repo_path, output_file):
    serialize_repo(repo_path, output_file)
