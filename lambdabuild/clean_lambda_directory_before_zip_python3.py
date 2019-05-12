#!/usr/bin/env python3
import os
import shutil
import py_compile
import argparse
import glob
import sys
import modulefinder

parser = argparse.ArgumentParser()
parser.add_argument("dir")
parser.add_argument("--sourceless", action="store_true")
parser.add_argument("--entry-points", nargs="+")
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
    ".pyc",
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
DIRECTORIES_EXTENSIONS_TO_DELETE = [".dist-info", ".egg-info", ".js"]
NEVER_DELETE = []

assert sys.version_info.major == 3

py_files_to_keep = None
if args.entry_points:
    py_files_to_keep = set()
    module_finder = modulefinder.ModuleFinder(path=sys.path + [args.dir])
    for entry_point in args.entry_points:
        with open("/tmp/entrypoint.py", "w") as writer:
            writer.write(f"import {entry_point}\n")
        module_finder.run_script("/tmp/entrypoint.py")
    for module in module_finder.modules.values():
        if module.__file__ is not None and module.__file__.startswith(args.dir):
            py_files_to_keep.add(os.path.abspath(module.__file__))

never_delete = set(os.path.join(args.dir, p) for p in NEVER_DELETE)
for root, dirs, files in os.walk(args.dir):
    for filename in files:
        for extension in EXTENSIONS_TO_DELETE:
            if filename.endswith(extension):
                os.unlink(os.path.join(root, filename))
        if py_files_to_keep is not None and filename.endswith(".py"):
            full_path = os.path.join(root, filename)
            if os.path.abspath(full_path) not in py_files_to_keep:
                os.unlink(full_path)
    for dirname in list(dirs):
        for extension in DIRECTORIES_EXTENSIONS_TO_DELETE:
            if dirname.endswith(extension):
                shutil.rmtree(os.path.join(root, dirname))
                dirs.remove(dirname)
for root, dirs, files in os.walk(args.dir):
    for filename in files:
        if filename.endswith(".py"):
            full_path = os.path.join(root, filename)
            py_compile.compile(full_path)
            if args.sourceless:
                if full_path not in never_delete:
                    os.unlink(full_path)
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
