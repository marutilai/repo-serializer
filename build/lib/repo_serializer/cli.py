import argparse
import os
from .serializer import serialize


def main():
    parser = argparse.ArgumentParser(
        description="Serialize a repository into a single file"
    )
    parser.add_argument("repo_path", help="Path to the repository to serialize")
    parser.add_argument(
        "-o",
        "--output",
        default="repo_serialized.txt",
        help="Output file path (default: repo_serialized.txt)",
    )

    args = parser.parse_args()

    # Ensure repo_path exists
    if not os.path.isdir(args.repo_path):
        print(f"Error: {args.repo_path} is not a valid directory")
        return 1

    # Serialize the repository
    serialize(args.repo_path, args.output)
    print(f"Repository serialized to {args.output}")
    return 0


if __name__ == "__main__":
    exit(main())
