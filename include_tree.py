#!/usr/bin/python

import os
import sys
import re

SOURCE_ROOT = os.getcwd()
INDEX_LIST = ['.h', '.c', '.cpp']
INCL_PAT = r'#include \"(.*?\.h)\"'


def index_files(root):
    """ walk through the file system indexing file paths by their file name. """
    index = {}
    for r, _, files in os.walk(root):
        for f in [x for x in files if os.path.splitext(x)[1] in INDEX_LIST]:
            path = os.path.join(r, f)
            if f.lower() not in index.keys():
                index[f.lower()] = path
    return index


def index_includes(path):
    """ find all the includes in a file and return the list of them. """
    text = ''
    index = []
    with open(path, 'r') as f:
        text = f.read()
    for m in re.finditer(INCL_PAT, text):
        index.append(m.group(1).lower())
    return index


def index_tree(root):
    """ loop through the source tree and build an index of what file includes what headers. """
    file_index = index_files(root)
    incl_index = dict.fromkeys(file_index.keys(), [])
    for f in incl_index.keys():
        incl_index[f] = index_includes(file_index[f])
    return incl_index    


def print_tree(index, f, level=0, printed=[]):
    """ print a representation of the include tree, beginning at a given file. """
    print '|' + ('-' * 3 + '+') * level, ('*' if f in printed else '') + f
    if f not in printed:
        for i in index[f]:
            printed.append(f)
            print_tree(index, i, level + 1, printed)


def print_usage():
    """ print the usage message. """
    message = "call from source root:\n\n    python <path_to_this_file>/include_tree.py <file>"
    print message


if __name__ == '__main__':
    try:
        f = sys.argv[1]
    except:
        print_usage()
        sys.exit(1)

    index = index_tree(SOURCE_ROOT)
    print_tree(index, f.lower())
