#!/usr/bin/env python
import os
import shutil
import py_compile
import argparse
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
    ".js.map",
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
    ".woff2",
    ".swp",
    ".swo",
    ".swn",
    ".swm",
]
DIRECTORIES_EXTENSIONS_TO_DELETE = [".dist-info", "__pycache__", ".egg-info", ".js"]

assert sys.version_info.major == 2

py_files_to_keep = None
if args.entry_points:
    py_files_to_keep = set()
    module_finder = modulefinder.ModuleFinder(path=sys.path + [args.dir])
    for entry_point in args.entry_points:
        with open("/tmp/entrypoint.py", "w") as writer:
            writer.write("import %s\n" % entry_point)
        module_finder.run_script("/tmp/entrypoint.py")
    for module in module_finder.modules.values():
        if module.__file__ is not None and module.__file__.startswith(args.dir):
            py_files_to_keep.add(os.path.abspath(module.__file__))

for root, dirs, files in os.walk(args.dir):
    for filename in files:
        for extension in EXTENSIONS_TO_DELETE:
            if filename.endswith(extension):
                os.unlink(os.path.join(root, filename))
        if py_files_to_keep is not None and filename.endswith(".py"):
            full_path = os.path.join(root, filename)
            if os.path.abspath(full_path) not in py_files_to_keep:
                os.unlink(full_path)
                continue
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
