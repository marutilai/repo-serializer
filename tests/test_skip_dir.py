import os
import tempfile
import shutil
from repo_serializer import serialize

def test_skip_dir():
    # Create a temporary directory structure
    with tempfile.TemporaryDirectory() as tmpdir:
        os.makedirs(os.path.join(tmpdir, "keep_me"))
        os.makedirs(os.path.join(tmpdir, "skip_me"))
        with open(os.path.join(tmpdir, "keep_me", "file1.txt"), "w") as f:
            f.write("hello world\n")
        with open(os.path.join(tmpdir, "skip_me", "file2.txt"), "w") as f:
            f.write("should be skipped\n")
        output_file = os.path.join(tmpdir, "output.txt")
        # Run serialize with skip_dirs
        serialize(tmpdir, output_file, skip_dirs=["skip_me"])
        # Read output and check
        with open(output_file, "r") as f:
            output = f.read()
        assert "keep_me" in output, "keep_me directory should be present"
        assert "file1.txt" in output, "file1.txt should be present"
        assert "skip_me" not in output, "skip_me directory should be skipped"
        assert "file2.txt" not in output, "file2.txt should be skipped"
        print("test_skip_dir passed!")

if __name__ == "__main__":
    test_skip_dir() 