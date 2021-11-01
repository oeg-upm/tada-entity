import sys
import os


def is_empty(fdir):
    f = open(fdir)
    content = f.read()
    f.close()
    if content.strip() == "":
        return True
    lines = content.split('\n')
    if len(lines) > 1 and lines[1].strip() != "":
        return False
    return True


def clear_empty(dir_path):
    files = os.listdir(dir_path)
    num_empty = 0
    num_non = 0
    for f in files:
        fdir = os.path.join(dir_path, f)
        if is_empty(fdir):
            os.remove(fdir)
            num_empty += 1
        else:
            num_non += 1
    print("Number of removed files: %d out of %d" % (num_empty, num_non+num_empty))


if __name__ == "__main__":
    clear_empty(".cache")
