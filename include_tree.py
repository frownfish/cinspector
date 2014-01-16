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
    def _print_tree(index, f, level=0, printed=[]):
        """ print a representation of the include tree, beginning at a given file. """
        print '|' + ('-' * 3 + '+') * level, ('*' if f in printed else '') + f
        if f not in printed:
            for i in index.get(f, []):
                printed.append(f)
                _print_tree(index, i, level + 1, printed)
    print "\n\nThis file is includes the following files"
    _print_tree(index, f, level=0, printed=[])


def print_help():
    """ print the usage message. """
    message = "call from source root:\n\n    python <path_to_this_file>/include_tree.py <file> [c|cpp|h|<regex-filter>]"
    print message


def index_usages(index, f, usages=[]):
    """ index what files include the given file, recursively. """
    tmp = []
    for k, items in index.items():
        if f in items and k not in usages:
            tmp.append(k)
            tmp.extend(index_usages(index, k, tmp))

    tmp = list(set(tmp))
    tmp.sort()
    return tmp


def print_usages(usages, fltr=''):
    def _filter(u, fltr):
        ret = []
        for k in u:
            if re.search(fltr, k):
                ret.append(k)
        return ret
    print "\n\nThis file is included in these files (using the filter: \"{f}\")".format(f=fltr)
    for k in _filter(usages, fltr):
        print k


if __name__ == '__main__':
    try:
        f = sys.argv[1]
    except:
        print_help()
        sys.exit(1)

    try:
        fltr = sys.argv[2]
    except:
        fltr = ''

    C_FLTR = r'\.c$'
    CPP_FLTR = r'\.cpp$'
    H_FLTR = r'\.h$'

    if fltr in ['c']:
        fltr = C_FLTR
    elif fltr in ['cpp']:
        fltr = CPP_FLTR
    elif fltr in ['h']:
        fltr = H_FLTR

    index = index_tree(SOURCE_ROOT)
    print_tree(index, f.lower())
    print_usages(index_usages(index, f.lower()), fltr=fltr)
