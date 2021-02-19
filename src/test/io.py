from pathlib import Path


def read_test_file(file_name):
    with open(Path("/test", "files", file_name), "r") as f:
        return f.read()
