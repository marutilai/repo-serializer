from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="repo-serializer",
    version="1.0.1",
    author="Maruti Agarwal",
    author_email="marutiagarwal@gmail.com",
    description="A tool to serialize repository contents into a single file",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/marutilai/repo-serializer",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "repo-serializer=repo_serializer.cli:main",
        ],
    },
    project_urls={
        "Source": "https://github.com/marutilai/repo-serializer",
        "Bug Tracker": "https://github.com/marutilai/repo-serializer/issues",
    },
    install_requires=[
        "pyperclip",  # For clipboard functionality
    ],
)
