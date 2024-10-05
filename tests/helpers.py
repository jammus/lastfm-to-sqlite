import os

def load_file(filename):
    cwd = os.getcwd()
    path = os.path.join(cwd, "tests", filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
