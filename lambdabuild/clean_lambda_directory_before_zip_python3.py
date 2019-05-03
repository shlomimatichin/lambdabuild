#!/usr/bin/env python3
import os
import shutil
import py_compile
import argparse
import glob
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
    ".swp",
    ".swo",
    ".swn",
    ".swm",
]
DIRETORIES_EXTENSIONS_TO_DELETE = [".dist-info", ".egg-info", ".js", "test", "tests"]
NEVER_DELETE = []

assert sys.version_info.major == 3

never_delete = set(os.path.join(args.dir, p) for p in NEVER_DELETE)
for root, dirs, files in os.walk(args.dir):
    for filename in files:
        for extension in EXTENSIONS_TO_DELETE:
            if filename.endswith(extension):
                os.unlink(os.path.join(root, filename))
        if filename.endswith(".py"):
            full_path = os.path.join(root, filename)
            py_compile.compile(full_path)
            if args.sourceless:
                if full_path not in never_delete:
                    os.unlink(full_path)
    for dirname in list(dirs):
        for extension in DIRETORIES_EXTENSIONS_TO_DELETE:
            if dirname.endswith(extension):
                shutil.rmtree(os.path.join(root, dirname))
                dirs.remove(dirname)
if args.sourceless:
    for root, dirs, unused_files in os.walk(args.dir):
        if '__pycache__' not in dirs:
            continue
        dirs.remove('__pycache__')
        cache = os.path.join(root, '__pycache__')
        for filename in glob.glob(f"{cache}/*.pyc"):
            removeMagic = os.path.splitext(os.path.splitext(os.path.basename(filename))[0])[0] + ".pyc"
            if removeMagic[:-1] not in never_delete:
                os.rename(filename, os.path.join(root, removeMagic))
        os.rmdir(cache)
