#!/usr/bin/env python
import os
import shutil
import py_compile
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("dir")
parser.add_argument("--sourceless", action="store_true")
args = parser.parse_args()

EXTENSIONS_TO_DELETE = [
    ".c",
    ".cmake",
    ".coffee",
    ".cpp",
    ".css",
    ".cxx",
    ".dot",
    ".exe",
    ".gif",
    ".gz",
    ".h",
    ".html",
    ".ico",
    ".java",
    ".js",
    ".jsx",
    ".make",
    ".md",
    ".mk",
    ".odt",
    ".php",
    ".pl",
    ".png",
    ".psk",
    ".pyo",
    ".rb",
    ".svg",
    ".tex",
    ".tgz",
    ".woff",
]
DIRECTORIES_EXTENSIONS_TO_DELETE = [".dist-info", "__pycache__", ".egg-info", ".js"]

assert sys.version_info.major == 2

for root, dirs, files in os.walk(args.dir):
    for filename in files:
        for extension in EXTENSIONS_TO_DELETE:
            if filename.endswith(extension):
                os.unlink(os.path.join(root, filename))
        if filename.endswith(".py") and root != args.dir:
            full_path = os.path.join(root, filename)
            pyc = full_path[:-len(".py")] + ".pyc"
            if not os.path.exists(pyc) or os.stat(pyc).st_mtime < os.stat(full_path).st_mtime:
                with open(full_path) as contents_reader:
                    contents = contents_reader.read()
                should_compile = 'async def ' not in contents and 'yield from ' not in contents
                if should_compile:
                    py_compile.compile(full_path)
            if args.sourceless:
                os.unlink(full_path)
    for dirname in list(dirs):
        for extension in DIRECTORIES_EXTENSIONS_TO_DELETE:
            if dirname.endswith(extension):
                shutil.rmtree(os.path.join(root, dirname))
                dirs.remove(dirname)
